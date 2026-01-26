from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame,
    QTableWidget, QTableWidgetItem, QHeaderView, QLineEdit, QSpinBox,
    QComboBox, QDialog
)
from PyQt6.QtGui import QFont, QPixmap, QColor


class TransactionView(QWidget):
    """Main Transaction Window for Cashiers"""

    def __init__(self, current_user: dict = None):
        super().__init__()
        self.current_user = current_user or {}
        self.showMaximized()
        self.setWindowTitle("SyPoint POS - Transaction")
        palette = self.palette()
        palette.setColor(self.backgroundRole(), QColor("#f5f0e8"))
        self.setPalette(palette)
        self.setAutoFillBackground(True)

        mainLayout = QHBoxLayout(self)
        mainLayout.setContentsMargins(0, 0, 0, 0)
        mainLayout.setSpacing(0)

        # Sidebar
        sidebar = self._build_sidebar()

        # Content Area
        contentArea = QWidget()
        contentLayout = QHBoxLayout(contentArea)
        contentLayout.setContentsMargins(30, 30, 30, 30)
        contentLayout.setSpacing(20)

        leftPanel = self._build_left_panel()
        rightPanel = self._build_right_panel()

        contentLayout.addWidget(leftPanel, 2)
        contentLayout.addWidget(rightPanel, 1)

        mainLayout.addWidget(sidebar)
        mainLayout.addWidget(contentArea)

        # Cart data
        self.cart_items = []
        self.update_cart_table()
        self.update_summary()

    def _build_sidebar(self):
        """Build unified sidebar with navigation"""
        sidebar = QFrame()
        sidebar.setFixedWidth(170)
        sidebar.setStyleSheet("background-color: #0d3b2b;")
        sidebarLayout = QVBoxLayout(sidebar)
        sidebarLayout.setContentsMargins(15, 25, 15, 25)
        sidebarLayout.setSpacing(20)
        sidebarLayout.setAlignment(Qt.AlignmentFlag.AlignTop)

        # Logo container
        logoContainer = QFrame()
        logoContainer.setFixedSize(140, 100)
        logoContainer.setStyleSheet("background-color: white; border-radius: 15px;")
        logoLayout = QVBoxLayout(logoContainer)
        logoLayout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        logoLabel = QLabel()
        pixmap = QPixmap("../ImageResources/SyPointLogo.png")
        if not pixmap.isNull():
            scaled = pixmap.scaled(110, 70, Qt.AspectRatioMode.KeepAspectRatio,
                                   Qt.TransformationMode.SmoothTransformation)
            logoLabel.setPixmap(scaled)
        else:
            logoLabel.setText("SyPoint")
            logoLabel.setFont(QFont("Arial", 14, QFont.Weight.Bold))
            logoLabel.setStyleSheet("color: #f4d03f;")
        logoLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logoLayout.addWidget(logoLabel)

        sidebarLayout.addWidget(logoContainer, alignment=Qt.AlignmentFlag.AlignCenter)
        sidebarLayout.addSpacing(30)

        # User info
        userIcon = QLabel("👤")
        userIcon.setFont(QFont("Arial", 28))
        userIcon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        userIcon.setStyleSheet("color: white;")
        sidebarLayout.addWidget(userIcon)

        full_name = f"{self.current_user.get('full_name', 'CASHIER')}".strip().upper()
        userLabel = QLabel(full_name)
        userLabel.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        userLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        userLabel.setStyleSheet("color: white;")
        userLabel.setWordWrap(True)
        sidebarLayout.addWidget(userLabel)

        sidebarLayout.addSpacing(40)

        # Navigation buttons
        self.transactionButton = self._create_sidebar_button("💳 Transaction", active=True)
        self.shiftSummaryButton = self._create_sidebar_button("📊 Shift", active=False)
        self.logoutButton = self._create_sidebar_button("🚪 Logout", active=False)

        sidebarLayout.addWidget(self.transactionButton)
        sidebarLayout.addWidget(self.shiftSummaryButton)
        sidebarLayout.addWidget(self.logoutButton)
        sidebarLayout.addStretch()

        return sidebar

    def _create_sidebar_button(self, text: str, active: bool = False):
        """Create styled sidebar navigation button"""
        btn = QPushButton(text)
        btn.setFont(QFont("Arial", 11))
        btn.setFixedHeight(45)
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        if active:
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #f4d03f; color: #1a1a1a; font-weight: bold;
                    border-radius: 8px; text-align: left; padding-left: 20px;
                }
                QPushButton:hover { background-color: #f5e05d; }
            """)
        else:
            btn.setStyleSheet("""
                QPushButton {
                    background-color: transparent; color: white;
                    border-radius: 8px; text-align: left; padding-left: 20px;
                }
                QPushButton:hover { background-color: #1a5040; }
            """)
        return btn

    def _build_left_panel(self):
        """Build left panel - Product search & Cart"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setSpacing(15)

        # Title
        title = QLabel("New Transaction")
        title.setFont(QFont("Arial", 24, QFont.Weight.Bold))
        title.setStyleSheet("color: #1a1a1a;")
        layout.addWidget(title)

        # Search frame
        searchFrame = QFrame()
        searchFrame.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 10px;
                padding: 15px;
            }
        """)
        searchLayout = QVBoxLayout(searchFrame)

        searchLabel = QLabel("Search Product")
        searchLabel.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        searchLabel.setStyleSheet("color: #1a1a1a;")
        searchLayout.addWidget(searchLabel)

        # Reference input + search button
        inputRow = QHBoxLayout()

        self.productSearchInput = QLineEdit()
        self.productSearchInput.setPlaceholderText("Enter Reference Number (e.g., PRO-001)")
        self.productSearchInput.setFixedHeight(45)
        self.productSearchInput.setStyleSheet("""
            QLineEdit {
                background-color: #f5f0e8;
                color: #1a1a1a;
                border: 2px solid #d0d0d0;
                border-radius: 5px;
                padding-left: 10px;
                font-size: 13px;
            }
            QLineEdit::placeholder {
                color: #7a7a7a;
            }
            QLineEdit:focus {
                border: 2px solid #f4d03f;
            }
        """)
        inputRow.addWidget(self.productSearchInput)

        self.searchButton = QPushButton("Search")
        self.searchButton.setFixedHeight(45)
        self.searchButton.setFixedWidth(100)
        self.searchButton.setStyleSheet("""
            QPushButton {
                background-color: #1a4d2e;
                color: white;
                border-radius: 5px;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #234d35;
            }
        """)
        inputRow.addWidget(self.searchButton)
        searchLayout.addLayout(inputRow)

        # Quantity
        qtyRow = QHBoxLayout()

        qtyLabel = QLabel("Quantity:")
        qtyLabel.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        qtyLabel.setStyleSheet("color: #1a1a1a;")
        qtyRow.addWidget(qtyLabel)

        self.quantityInput = QSpinBox()
        self.quantityInput.setMinimum(1)
        self.quantityInput.setMaximum(9999)
        self.quantityInput.setValue(1)
        self.quantityInput.setFixedHeight(45)
        self.quantityInput.setFixedWidth(120)
        self.quantityInput.setStyleSheet("""
            QSpinBox {
                background-color: #f5f0e8;
                color: #1a1a1a;
                border: 2px solid #d0d0d0;
                border-radius: 5px;
                padding-left: 8px;
                font-size: 13px;
            }

            QSpinBox::up-button, QSpinBox::down-button {
                width: 18px;
                background-color: #e0dccf;
                border-left: 1px solid #c0c0c0;
            }

            QSpinBox::up-button:hover, QSpinBox::down-button:hover {
                background-color: #d6d2c5;
            }

            QSpinBox::up-arrow {
                image: url(none);
                border-left: 6px solid transparent;
                border-right: 6px solid transparent;
                border-bottom: 8px solid #1a1a1a;
                width: 0;
                height: 0;
            }

            QSpinBox::down-arrow {
                image: url(none);
                border-left: 6px solid transparent;
                border-right: 6px solid transparent;
                border-top: 8px solid #1a1a1a;
                width: 0;
                height: 0;
            }
        """)
        qtyRow.addWidget(self.quantityInput)
        qtyRow.addStretch()
        searchLayout.addLayout(qtyRow)

        # Add to cart button
        self.addToCartButton = QPushButton("Add to Cart")
        self.addToCartButton.setFixedHeight(40)
        self.addToCartButton.setStyleSheet("""
            QPushButton {
                background-color: #f4d03f;
                color: #1a1a1a;
                font-weight: bold;
                border-radius: 5px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #f5e05d;
            }
        """)
        searchLayout.addWidget(self.addToCartButton)

        layout.addWidget(searchFrame)

        # Cart title
        cartTitle = QLabel("Shopping Cart")
        cartTitle.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        cartTitle.setStyleSheet("color: #1a1a1a; margin-top: 10px;")
        layout.addWidget(cartTitle)

        # Cart table
        self.cartTable = QTableWidget()
        self.cartTable.setColumnCount(4)
        self.cartTable.setHorizontalHeaderLabels(
            ["Product", "Price", "Qty", "Subtotal"]
        )
        self.cartTable.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.cartTable.verticalHeader().setVisible(False)
        self.cartTable.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.cartTable.setStyleSheet("""
            QTableWidget {
                background-color: white;
                border: 2px solid #d0d0d0;
                border-radius: 10px;
                gridline-color: #e0e0e0;
                color: #1a1a1a;
            }
            QHeaderView::section {
                background-color: #0d3b2b;
                color: white;
                font-weight: bold;
                padding: 10px;
                border: none;
            }
        """)
        layout.addWidget(self.cartTable)

        # Cart actions
        actionsLayout = QHBoxLayout()

        self.voidTransactionButton = QPushButton("Void Transaction")
        self.voidTransactionButton.setFixedHeight(40)
        self.voidTransactionButton.setStyleSheet("""
            QPushButton {
                background-color: #ff6f00;
                color: white;
                border-radius: 5px;
                font-weight: bold;
                font-size: 11px;
            }
            QPushButton:hover {
                background-color: #f57c00;
            }
        """)
        actionsLayout.addWidget(self.voidTransactionButton)

        layout.addLayout(actionsLayout)
        return panel

    def _build_right_panel(self):
        """Build right panel - Order Summary"""
        panel = QFrame()
        panel.setFixedWidth(350)
        panel.setStyleSheet("background-color: #0d3b2b; border-radius: 15px;")
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        title = QLabel("Order Summary")
        title.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        title.setStyleSheet("color: white;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        divider1 = QFrame()
        divider1.setFrameShape(QFrame.Shape.HLine)
        divider1.setStyleSheet("background-color: #1a5040;")
        layout.addWidget(divider1)

        self.subtotalLabel = self._create_summary_row("Subtotal:", "PHP 0.00")
        self.taxLabel = self._create_summary_row("Tax (12%):", "PHP 0.00")
        self.discountLabel = self._create_summary_row("Discount:", "PHP 0.00")
        layout.addLayout(self.subtotalLabel)
        layout.addLayout(self.taxLabel)
        layout.addLayout(self.discountLabel)

        divider2 = QFrame()
        divider2.setFrameShape(QFrame.Shape.HLine)
        divider2.setStyleSheet("background-color: #f4d03f; min-height: 2px;")
        layout.addWidget(divider2)

        self.totalLabel = self._create_summary_row("TOTAL:", "PHP 0.00", is_total=True)
        layout.addLayout(self.totalLabel)

        layout.addSpacing(20)

        self.checkoutButton = QPushButton("Proceed to Payment")
        self.checkoutButton.setFixedHeight(50)
        self.checkoutButton.setEnabled(False)
        self.checkoutButton.setStyleSheet("""
            QPushButton {
                background-color: #f4d03f; color: #1a1a1a;
                font-size: 14px; font-weight: bold; border-radius: 8px;
            }
            QPushButton:hover { background-color: #f5e05d; }
            QPushButton:disabled { background-color: #666666; color: #999999; }
        """)
        layout.addWidget(self.checkoutButton)

        layout.addStretch()
        return panel

    def _create_summary_row(self, label_text: str, value_text: str, is_total: bool = False):
        """Create summary row with label and value"""
        row = QHBoxLayout()
        label = QLabel(label_text)
        value = QLabel(value_text)

        if is_total:
            label.setFont(QFont("Arial", 16, QFont.Weight.Bold))
            label.setStyleSheet("color: #f4d03f;")
            value.setFont(QFont("Arial", 18, QFont.Weight.Bold))
            value.setStyleSheet("color: #4caf50;")
        else:
            label.setFont(QFont("Arial", 12))
            label.setStyleSheet("color: white;")
            value.setFont(QFont("Arial", 12, QFont.Weight.Bold))
            value.setStyleSheet("color: white;")

        # Store value labels for updates
        if "Subtotal" in label_text:
            self.subtotalValue = value
        elif "Tax" in label_text:
            self.taxValue = value
        elif "Discount" in label_text:
            self.discountValue = value
        elif "TOTAL" in label_text:
            self.totalValue = value

        row.addWidget(label)
        row.addStretch()
        row.addWidget(value)
        return row

    def update_summary(self):
        """Update order summary panel"""
        subtotal = sum(item['subtotal'] for item in self.cart_items)
        tax = subtotal * 0.12
        discount = 0.0
        total = subtotal + tax - discount

        self.subtotalValue.setText(f"PHP {subtotal:.2f}")
        self.taxValue.setText(f"PHP {tax:.2f}")
        self.discountValue.setText(f"PHP {discount:.2f}")
        self.totalValue.setText(f"PHP {total:.2f}")

        self.checkoutButton.setEnabled(len(self.cart_items) > 0)

    def update_cart_table(self):
        """Update cart table display"""
        self.cartTable.setRowCount(len(self.cart_items))

        for row_idx, item in enumerate(self.cart_items):
            self.cartTable.setItem(
                row_idx, 0, QTableWidgetItem(item['product_name'])
            )
            self.cartTable.setItem(
                row_idx, 1, QTableWidgetItem(f"PHP {item['price']:.2f}")
            )
            self.cartTable.setItem(
                row_idx, 2, QTableWidgetItem(str(item['qty']))
            )
            self.cartTable.setItem(
                row_idx, 3, QTableWidgetItem(f"PHP {item['subtotal']:.2f}")
            )

        self.update_summary()

    def add_item_to_cart(self, item: dict):
        """Add item to cart"""
        self.cart_items.append(item)
        self.update_cart_table()

    def clear_cart(self):
        """Clear all cart items"""
        self.cart_items.clear()
        self.update_cart_table()

    def get_cart_items(self):
        """Get current cart items"""
        return self.cart_items

    def get_current_total(self):
        """Get current total (subtotal + tax)"""
        subtotal = sum(item['subtotal'] for item in self.cart_items)
        return subtotal + (subtotal * 0.12)


class VoidTransactionDialog(QDialog):
    """Admin code verification for voiding transactions"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(450, 300)
        self.setWindowTitle("Void Transaction - Admin Authorization")
        self.setModal(True)
        self.setStyleSheet("background-color: #f5f0e8;")

        # Center on parent
        if parent:
            parent_geo = parent.geometry()
            self.move(parent_geo.center() - self.rect().center())

        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)

        # Title
        title = QLabel("🔒 Admin Authorization Required")
        title.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        title.setStyleSheet("color: #d32f2f;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        # Message
        msg = QLabel("Enter admin code to void this transaction:")
        msg.setFont(QFont("Arial", 11))
        msg.setStyleSheet("color: #666666;")
        msg.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(msg)

        # Admin code input
        self.adminCodeInput = QLineEdit()
        self.adminCodeInput.setPlaceholderText("Admin Code")
        self.adminCodeInput.setEchoMode(QLineEdit.EchoMode.Password)
        self.adminCodeInput.setFixedHeight(45)
        self.adminCodeInput.setStyleSheet("""
            QLineEdit {
                background-color: white; border: 2px solid #d0d0d0;
                border-radius: 5px; padding-left: 15px; font-size: 13px;
            }
            QLineEdit:focus { border: 2px solid #f4d03f; }
        """)
        layout.addWidget(self.adminCodeInput)

        # Buttons
        btnLayout = QHBoxLayout()

        self.cancelButton = QPushButton("Cancel")
        self.cancelButton.setFixedHeight(45)
        self.cancelButton.setStyleSheet("""
            QPushButton {
                background-color: #666666; color: white; border-radius: 5px;
                font-weight: bold; font-size: 12px;
            }
            QPushButton:hover { background-color: #777777; }
        """)
        self.cancelButton.clicked.connect(self.reject)
        btnLayout.addWidget(self.cancelButton)

        self.confirmButton = QPushButton("Void Transaction")
        self.confirmButton.setFixedHeight(45)
        self.confirmButton.setStyleSheet("""
            QPushButton {
                background-color: #d32f2f; color: white; border-radius: 5px;
                font-weight: bold; font-size: 12px;
            }
            QPushButton:hover { background-color: #c62828; }
        """)
        btnLayout.addWidget(self.confirmButton)

        layout.addLayout(btnLayout)

    def get_admin_code(self):
        """Get entered admin code"""
        return self.adminCodeInput.text().strip()


class PaymentPopup(QWidget):
    """Payment processing popup with discount support"""

    def __init__(self, base_total: float, parent=None):
        super().__init__(parent)
        self.setFixedSize(500, 650)
        self.setWindowTitle("Process Payment")
        self.setWindowModality(Qt.WindowModality.ApplicationModal)
        self.setStyleSheet("background-color: #f5f0e8;")

        if parent:
            parent_geo = parent.geometry()
            self.move(parent_geo.center() - self.rect().center())

        mainLayout = QVBoxLayout(self)
        mainLayout.setContentsMargins(30, 30, 30, 30)
        mainLayout.setSpacing(20)

        # Title
        title = QLabel("Payment")
        title.setFont(QFont("Arial", 24, QFont.Weight.Bold))
        title.setStyleSheet("color: #1a4d2e;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        mainLayout.addWidget(title)

        # Details Frame
        detailsFrame = QFrame()
        detailsFrame.setStyleSheet("background-color: white; border-radius: 10px;")
        detailsLayout = QVBoxLayout(detailsFrame)
        detailsLayout.setContentsMargins(20, 20, 20, 20)
        detailsLayout.setSpacing(15)

        # Discount Type
        discountRow = QHBoxLayout()
        discountLabel = QLabel("Discount Type:")
        discountLabel.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        discountRow.addWidget(discountLabel)

        self.discountComboBox = QComboBox()
        self.discountComboBox.addItems(["None", "Senior Citizen (20%)", "PWD (20%)"])
        self.discountComboBox.setFixedHeight(35)
        self.discountComboBox.setStyleSheet("""
            QComboBox {
                background-color: #f5f0e8; border: 2px solid #d0d0d0;
                border-radius: 5px; padding-left: 10px;
            }
        """)
        discountRow.addWidget(self.discountComboBox)
        detailsLayout.addLayout(discountRow)

        # Payment Method
        methodRow = QHBoxLayout()
        methodLabel = QLabel("Payment Method:")
        methodLabel.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        methodRow.addWidget(methodLabel)

        self.paymentMethodComboBox = QComboBox()
        self.paymentMethodComboBox.addItems(["Cash", "GCash"])
        self.paymentMethodComboBox.setFixedHeight(35)
        self.paymentMethodComboBox.setStyleSheet("""
            QComboBox {
                background-color: #f5f0e8; border: 2px solid #d0d0d0;
                border-radius: 5px; padding-left: 10px;
            }
        """)
        methodRow.addWidget(self.paymentMethodComboBox)
        detailsLayout.addLayout(methodRow)

        # Amount Received
        amountRow = QHBoxLayout()
        amountLabel = QLabel("Amount Received:")
        amountLabel.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        amountRow.addWidget(amountLabel)

        self.amountReceivedInput = QLineEdit()
        self.amountReceivedInput.setPlaceholderText("0.00")
        self.amountReceivedInput.setFixedHeight(35)
        self.amountReceivedInput.setStyleSheet("""
            QLineEdit {
                background-color: #f5f0e8; border: 2px solid #d0d0d0;
                border-radius: 5px; padding-left: 10px;
            }
        """)
        amountRow.addWidget(self.amountReceivedInput)
        detailsLayout.addLayout(amountRow)

        mainLayout.addWidget(detailsFrame)

        # Summary Frame
        summaryFrame = QFrame()
        summaryFrame.setStyleSheet("background-color: #0d3b2b; border-radius: 10px;")
        summaryLayout = QVBoxLayout(summaryFrame)
        summaryLayout.setContentsMargins(20, 20, 20, 20)
        summaryLayout.setSpacing(10)

        self.subtotalLabel = self._create_summary_row("Subtotal:", f"PHP {base_total:.2f}", summaryLayout)
        self.taxLabel = self._create_summary_row("Tax (12%):", "PHP 0.00", summaryLayout)
        self.discountLabel = self._create_summary_row("Discount:", "PHP 0.00", summaryLayout)

        divider = QFrame()
        divider.setFrameShape(QFrame.Shape.HLine)
        divider.setStyleSheet("background-color: #f4d03f; min-height: 2px;")
        summaryLayout.addWidget(divider)

        self.totalLabel = self._create_summary_row("TOTAL:", f"PHP {base_total:.2f}", summaryLayout, is_total=True)
        self.changeLabel = self._create_summary_row("Change:", "PHP 0.00", summaryLayout, is_total=True)

        mainLayout.addWidget(summaryFrame)

        # Buttons
        buttonsLayout = QHBoxLayout()
        cancelButton = QPushButton("Cancel")
        cancelButton.setFixedHeight(45)
        cancelButton.setStyleSheet("""
            QPushButton {
                background-color: #d32f2f; color: white; border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #c62828; }
        """)
        cancelButton.clicked.connect(self.close)
        buttonsLayout.addWidget(cancelButton)

        self.confirmButton = QPushButton("Confirm Payment")
        self.confirmButton.setFixedHeight(45)
        self.confirmButton.setStyleSheet("""
            QPushButton {
                background-color: #4caf50; color: white; border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #45a049; }
            QPushButton:disabled { background-color: #666666; color: #999999; }
        """)
        self.confirmButton.setEnabled(False)
        buttonsLayout.addWidget(self.confirmButton)

        mainLayout.addLayout(buttonsLayout)

        # Discount rates
        self.discount_rates = {
            "None": 0.0,
            "Senior Citizen (20%)": 0.20,
            "PWD (20%)": 0.20,
        }

        # Connect signals
        self.discountComboBox.currentTextChanged.connect(self.update_summary)
        self.amountReceivedInput.textChanged.connect(self.update_summary)

        # Initial calculation
        self.update_summary()

    def _create_summary_row(self, text: str, value: str, layout: QVBoxLayout, is_total: bool = False):
        row = QHBoxLayout()
        label = QLabel(text)
        value_label = QLabel(value)

        if is_total:
            label.setFont(QFont("Arial", 13, QFont.Weight.Bold))
            label.setStyleSheet("color: #f4d03f;")
            value_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
            value_label.setStyleSheet("color: #4caf50;")
        else:
            label.setFont(QFont("Arial", 11))
            label.setStyleSheet("color: white;")
            value_label.setFont(QFont("Arial", 11, QFont.Weight.Bold))
            value_label.setStyleSheet("color: white;")

        row.addWidget(label)
        row.addStretch()
        row.addWidget(value_label)
        layout.addLayout(row)

        # Store references
        if "Subtotal" in text:
            self.subtotalValue = value_label
        elif "Tax" in text:
            self.taxValue = value_label
        elif "Discount" in text:
            self.discountValue = value_label
        elif "TOTAL" in text:
            self.totalValue = value_label
        elif "Change" in text:
            self.changeValue = value_label

        return row

    def update_summary(self):
        """Update payment summary with real-time calculations"""
        cart_items = self.parent().get_cart_items() if self.parent() else []
        subtotal = sum(item['subtotal'] for item in cart_items)
        tax = subtotal * 0.12
        discount_rate = self.discount_rates[self.discountComboBox.currentText()]
        discount = subtotal * discount_rate
        total = subtotal + tax - discount

        tendered_text = self.amountReceivedInput.text().strip()
        tendered = float(tendered_text) if tendered_text else 0.0
        change = max(0.0, tendered - total)

        self.subtotalValue.setText(f"PHP {subtotal:.2f}")
        self.taxValue.setText(f"PHP {tax:.2f}")
        self.discountValue.setText(f"PHP {discount:.2f}")
        self.totalValue.setText(f"PHP {total:.2f}")
        self.changeValue.setText(f"PHP {change:.2f}")

        self.confirmButton.setEnabled(tendered >= total)

    def get_payment_data(self):
        """Return all calculated payment details"""
        cart_items = self.parent().get_cart_items() if self.parent() else []
        subtotal = sum(item['subtotal'] for item in cart_items)
        tax = subtotal * 0.12
        discount_rate = self.discount_rates[self.discountComboBox.currentText()]
        discount = subtotal * discount_rate
        total = subtotal + tax - discount
        tendered = float(self.amountReceivedInput.text() or 0)
        change = max(0, tendered - total)

        return {
            'subtotal': subtotal,
            'tax': tax,
            'discount': discount,
            'total': total,
            'tendered': tendered,
            'change': change,
            'method': self.paymentMethodComboBox.currentText(),
            'discount_type': self.discountComboBox.currentText()
        }


class TransactionSuccessPopup(QWidget):
    """Success popup shown after payment"""

    def __init__(self, transaction_number: str, total_amount: float,
                 payment_method: str, change_amount: float, parent=None):
        super().__init__(parent)
        self.setFixedSize(450, 420)
        self.setWindowTitle("Transaction Successful")
        self.setWindowModality(Qt.WindowModality.ApplicationModal)
        self.setStyleSheet("background-color: #f5f0e8;")

        if parent:
            parent_geo = parent.geometry()
            self.move(parent_geo.center() - self.rect().center())

        frame = QFrame(self)
        frame.setGeometry(10, 10, 430, 400)
        frame.setStyleSheet("""
            QFrame { background-color: #e8f5e9; border-radius: 15px; }
        """)

        layout = QVBoxLayout(frame)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(15)

        # Success icon
        icon = QLabel("✓")
        icon.setFont(QFont("Arial", 72, QFont.Weight.Bold))
        icon.setStyleSheet("color: #4caf50;")
        icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(icon)

        # Message
        msg = QLabel("Transaction Successful!")
        msg.setFont(QFont("Arial", 20, QFont.Weight.Bold))
        msg.setStyleSheet("color: #2e7d32;")
        msg.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(msg)

        # Details
        details = [
            f"Transaction #: {transaction_number}",
            f"Total: PHP {total_amount:.2f}",
            f"Payment Method: {payment_method}"
        ]
        for text in details:
            lbl = QLabel(text)
            lbl.setFont(QFont("Arial", 12))
            lbl.setStyleSheet("color: #1a1a1a;")
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(lbl)

        if change_amount > 0:
            change_lbl = QLabel(f"Change: PHP {change_amount:.2f}")
            change_lbl.setFont(QFont("Arial", 13, QFont.Weight.Bold))
            change_lbl.setStyleSheet("color: #f57c00;")
            change_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(change_lbl)

        # Buttons
        buttons = QHBoxLayout()
        self.printReceiptButton = QPushButton("Print Receipt")
        self.printReceiptButton.setFixedHeight(40)
        self.printReceiptButton.setStyleSheet("""
            QPushButton {
                background-color: #1a4d2e; color: white; border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #234d35; }
        """)

        self.closeButton = QPushButton("Close")
        self.closeButton.setFixedHeight(40)
        self.closeButton.setStyleSheet("""
            QPushButton {
                background-color: #f4d03f; color: #1a1a1a; border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #f5e05d; }
        """)

        buttons.addWidget(self.printReceiptButton)
        buttons.addWidget(self.closeButton)
        layout.addLayout(buttons)