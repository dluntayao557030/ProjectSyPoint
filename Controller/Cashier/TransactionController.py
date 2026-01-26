import datetime
import os
from PyQt6.QtWidgets import QMessageBox
from Utilities.DatabaseConnection import getConnection
from View.CashierGUI.TransactionWindow import TransactionView, VoidTransactionDialog, PaymentPopup
from Model.TransactionModel import TransactionModel


class TransactionController:
    """Controller for Transaction window - handles business logic and DB operations"""

    def __init__(self, current_user: dict):
        self.current_user = current_user
        self.cashier_id = current_user.get('user_id')
        self.role = current_user.get('role', 'cashier')
        self.view = None
        self.payment_popup = None

        # Receipt data storage
        self.last_transaction_id = None
        self.last_payment_data = None
        self.last_cart_items = None
        self.last_cashier_name = None

    def open_transaction(self):
        """Initialize and show transaction window"""
        self.view = TransactionView(self.current_user)
        self._connect_signals()
        self.view.show()

    def _connect_signals(self):
        """Connect all UI signals to controller methods"""
        self.view.searchButton.clicked.connect(self.search_product)
        self.view.productSearchInput.returnPressed.connect(self.search_product)
        self.view.addToCartButton.clicked.connect(self.add_to_cart)
        self.view.voidTransactionButton.clicked.connect(self.void_transaction)
        self.view.checkoutButton.clicked.connect(self.proceed_to_payment)
        self.view.shiftSummaryButton.clicked.connect(self.navigate_to_shift_summary)
        self.view.logoutButton.clicked.connect(self.logout)

    # ============================================================
    # PRODUCT SEARCH
    # ============================================================

    def search_product(self):
        """Search product by reference number"""
        ref = self.view.productSearchInput.text().strip()
        if not ref:
            return

        # Get query from model
        query, params = TransactionModel.get_product_query(ref)

        # Execute in controller
        try:
            conn = getConnection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute(query, params)
            product = cursor.fetchone()
            cursor.close()
            conn.close()

            if product:
                # Display product name in search box
                self.view.productSearchInput.setText(product['product_name'])
                self.view.quantityInput.setFocus()
            else:
                QMessageBox.warning(self.view, "Not Found",
                                    "Product with this reference number not found.")
                self.view.productSearchInput.clear()
                self.view.productSearchInput.setFocus()
        except Exception as e:
            QMessageBox.critical(self.view, "Error", f"Database error: {str(e)}")
            print(f"Error in search_product: {e}")

    # ============================================================
    # CART MANAGEMENT
    # ============================================================

    def add_to_cart(self):
        """Add product to cart"""
        ref = self.view.productSearchInput.text().strip()
        qty = self.view.quantityInput.value()

        if not ref:
            QMessageBox.warning(self.view, "Input Required",
                                "Please enter a reference number.")
            return

        # Get query from model
        query, params = TransactionModel.get_product_query(ref)

        # Execute in controller
        try:
            conn = getConnection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute(query, params)
            product = cursor.fetchone()
            cursor.close()
            conn.close()

            if not product:
                QMessageBox.warning(self.view, "Not Found", "Product not found.")
                return

            # Create cart item
            item = {
                'product_id': product['product_id'],
                'reference_number': product['reference_number'],
                'product_name': product['product_name'],
                'price': float(product['price']),
                'qty': qty,
                'subtotal': float(product['price']) * qty
            }

            self.view.add_item_to_cart(item)

            # Reset inputs
            self.view.productSearchInput.clear()
            self.view.productSearchInput.setFocus()
            self.view.quantityInput.setValue(1)

        except Exception as e:
            QMessageBox.critical(self.view, "Error", f"Database error: {str(e)}")
            print(f"Error in add_to_cart: {e}")

    # ============================================================
    # VOID TRANSACTION
    # ============================================================

    def void_transaction(self):
        """Void transaction with admin code verification"""
        if not self.view.cart_items:
            QMessageBox.information(self.view, "Empty Cart",
                                    "No items in cart to void.")
            return

        # Show admin code dialog
        dialog = VoidTransactionDialog(self.view)

        def verify_and_void():
            admin_code = dialog.get_admin_code()

            if not admin_code:
                QMessageBox.warning(dialog, "Input Required",
                                    "Please enter admin code.")
                return

            # Verify admin code
            query, params = TransactionModel.verify_admin_code_query(admin_code)

            try:
                conn = getConnection()
                cursor = conn.cursor(dictionary=True)
                cursor.execute(query, params)
                admin_user = cursor.fetchone()
                cursor.close()
                conn.close()

                if admin_user and admin_user.get('role') == 'admin':
                    # Admin verified - void transaction
                    self.view.clear_cart()
                    dialog.accept()
                    QMessageBox.information(self.view, "Transaction Voided",
                                            "Transaction has been voided successfully.")
                else:
                    QMessageBox.critical(dialog, "Authorization Failed",
                                         "Invalid admin code or insufficient permissions.")
            except Exception as e:
                QMessageBox.critical(dialog, "Error", f"Database error: {str(e)}")
                print(f"Error in verify_and_void: {e}")

        dialog.confirmButton.clicked.connect(verify_and_void)
        dialog.exec()

    # ============================================================
    # PAYMENT PROCESSING
    # ============================================================

    def proceed_to_payment(self):
        """Open payment popup"""
        if not self.view.get_cart_items():
            QMessageBox.warning(self.view, "Empty Cart",
                                "Please add items to the cart before proceeding to payment.")
            return

        base_total = self.view.get_current_total()
        self.payment_popup = PaymentPopup(base_total, self.view)
        self.payment_popup.confirmButton.clicked.connect(
            lambda: self.confirm_payment(self.payment_popup))
        self.payment_popup.show()

    def confirm_payment(self, popup):
        """Process payment and save transaction"""
        payment_data = popup.get_payment_data()

        if payment_data['tendered'] < payment_data['total']:
            QMessageBox.warning(popup, "Insufficient Payment",
                                "Amount received is less than the total.")
            return

        cart_items = self.view.get_cart_items()

        # Create transaction
        transaction_id = self._create_transaction(payment_data, cart_items)

        if not transaction_id:
            QMessageBox.critical(self.view, "Error",
                                 "Failed to create transaction. Please try again.")
            return

        popup.close()

        # Store receipt data
        cashier_name = self.current_user.get('full_name', 'CASHIER').upper()
        self.last_transaction_id = transaction_id
        self.last_payment_data = payment_data.copy()
        self.last_cart_items = cart_items[:]
        self.last_cashier_name = cashier_name

        # Generate and save receipt
        success, result = self._generate_receipt(
            transaction_id, payment_data, cart_items, cashier_name
        )

        if success:
            QMessageBox.information(self.view, "Transaction Complete",
                                    f"Payment successful!\nReceipt saved:\n{result}")
        else:
            QMessageBox.warning(self.view, "Receipt Warning",
                                f"Transaction saved, but receipt failed:\n{result}")

        # Clear cart
        self.view.clear_cart()

    def _create_transaction(self, payment_data: dict, cart_items: list) -> int:
        """Create transaction in database"""
        try:
            conn = getConnection()
            cursor = conn.cursor()

            # Generate transaction number
            today = datetime.date.today().strftime('%Y%m%d')
            transaction_number = f"TXN-{today}-{datetime.datetime.now().strftime('%H%M%S')}"

            # Get discount type ID
            discount_type_id = None
            if payment_data.get('discount_type') != "None":
                discount_query, discount_params = TransactionModel.get_discount_type_id_query(
                    payment_data['discount_type'])
                cursor.execute(discount_query, discount_params)
                discount_result = cursor.fetchone()
                if discount_result:
                    discount_type_id = discount_result[0]

            # Insert transaction
            trans_query, trans_params = TransactionModel.create_transaction_query(
                transaction_number=transaction_number,
                cashier_id=self.cashier_id,
                subtotal=payment_data['subtotal'],
                discount_amount=payment_data['discount'],
                final_total=payment_data['total'],
                discount_type_id=discount_type_id
            )
            cursor.execute(trans_query, trans_params)
            transaction_id = cursor.lastrowid

            # Insert transaction items
            for item in cart_items:
                item_query, item_params = TransactionModel.add_transaction_item_query(
                    transaction_id=transaction_id,
                    product_id=item['product_id'],
                    product_name=item['product_name'],
                    quantity=item['qty'],
                    unit_price=item['price'],
                    total_price=item['subtotal']
                )
                cursor.execute(item_query, item_params)

            conn.commit()
            cursor.close()
            conn.close()
            return transaction_id

        except Exception as e:
            if conn:
                conn.rollback()
            print(f"Error creating transaction: {e}")
            return 0
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    @staticmethod
    def _generate_receipt(transaction_id: int, payment_data: dict,
                          cart_items: list, cashier_name: str):
        """Generate receipt text file"""
        now = datetime.datetime.now()
        WIDTH = 42

        def center(t):
            return f"{t:^{WIDTH}}"

        def lr(left, right):
            gap = WIDTH - len(str(left)) - len(str(right))
            return str(left) + " " * max(0, gap) + str(right)

        def line(c='-'):
            return c * WIDTH

        def price(v):
            return f"₱{float(v):,.2f}"

        receipt_lines = [
            center("** SyPoint POS **"),
            center("Your Friendly Store - Davao"),
            center("Contact: 0917-XXX-XXXX"),
            line(),
            lr("Transaction #:", f"TXN-{transaction_id:06d}"),
            lr("Date:", now.strftime("%b %d, %Y")),
            lr("Time:", now.strftime("%I:%M %p")),
            lr("Cashier:", cashier_name),
            line(),
            "ITEM                  QTY     AMOUNT",
            line("-"),
        ]

        for item in cart_items:
            name = item['product_name'][:22].ljust(22)
            qty = f"{item['qty']:>3}"
            amt = price(item['subtotal'])
            receipt_lines.append(f"{name} {qty}   {amt:>9}")

        receipt_lines.extend([
            line(),
            lr("Subtotal:", price(payment_data['subtotal'])),
            lr("Tax (12%):", price(payment_data['tax'])),
        ])

        if payment_data.get('discount', 0) > 0:
            disc_type = payment_data.get('discount_type', 'Discount')
            receipt_lines.append(lr(f"{disc_type}:", f"-{price(payment_data['discount'])}"))

        receipt_lines.extend([
            line("="),
            lr("TOTAL:", price(payment_data['total'])),
            "",
            lr("Payment Method:", payment_data['method'].upper()),
            lr("Amount Tendered:", price(payment_data['tendered'])),
            lr("Change:", price(payment_data['change'])),
            line(),
            center("Thank You for Shopping!"),
            center("Come Again Soon ♥"),
            "",
            "\f"
        ])

        # Save file
        folder = "receipts"
        os.makedirs(folder, exist_ok=True)

        filename = f"receipt_TXN-{transaction_id:06d}_{now.strftime('%Y%m%d_%H%M')}.txt"
        filepath = os.path.join(folder, filename)

        try:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write("\n".join(receipt_lines))
            return True, filepath
        except Exception as e:
            print(f"Receipt save failed: {e}")
            return False, str(e)

    # ============================================================
    # NAVIGATION
    # ============================================================

    def navigate_to_shift_summary(self):
        """Navigate to shift summary window"""
        self.view.close()
        from Controller.Cashier.ShiftSummaryController import ShiftSummaryController
        self.shift_controller = ShiftSummaryController(self.current_user)
        self.shift_controller.open_shift_summary()

    def logout(self):
        """Logout and return to login"""
        reply = QMessageBox.question(
            self.view,
            "Logout",
            "Are you sure you want to logout?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            self.view.close()
            from Controller.Login.LoginController import LoginController
            from Model.Authentication.LoginModel import LoginModel
            from View.LoginGUI.Login import LoginView

            login_model = LoginModel()
            login_view = LoginView()
            login_controller = LoginController(login_model, login_view)
            login_view.show()