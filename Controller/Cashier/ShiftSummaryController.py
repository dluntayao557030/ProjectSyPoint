import datetime
from PyQt6.QtWidgets import QMessageBox, QFileDialog
from Utilities.DatabaseConnection import getConnection
from View.CashierGUI.ShiftSummaryWindow import ShiftSummaryView
from Model.ShiftSummaryModel import ShiftSummaryModel


class ShiftSummaryController:
    """Controller for Shift Summary window"""

    def __init__(self, current_user: dict):
        self.current_user = current_user
        self.cashier_id = current_user.get('user_id')
        self.role = current_user.get('role', 'cashier')
        self.view = None

        # Summary data
        self.shift_data = {}

    def open_shift_summary(self):
        """Initialize and show shift summary window"""
        self.view = ShiftSummaryView(self.current_user)
        self._load_shift_data()
        self._connect_signals()
        self.view.show()

    def _connect_signals(self):
        """Connect UI signals"""
        self.view.transactionButton.clicked.connect(self.navigate_to_transaction)
        self.view.printButton.clicked.connect(self.print_summary)
        self.view.logoutButton.clicked.connect(self.logout)

    def _load_shift_data(self):
        """Load all shift summary data"""
        try:
            # Get shift start time (start of cashier's shift)
            shift_start = self._get_shift_start_time()

            # Load KPIs
            self._load_kpis(shift_start)

            # Load payment breakdown
            self._load_payment_breakdown(shift_start)

            # Load top products
            self._load_top_products(shift_start)

            # Load transactions table
            self._load_transactions(shift_start)

        except Exception as e:
            QMessageBox.critical(self.view, "Error",
                                 f"Failed to load shift data: {str(e)}")
            print(f"Error loading shift data: {e}")

    def _get_shift_start_time(self):
        """Get shift start time based on user shift"""
        user_shift = self.current_user.get('shift', 'morning')
        now = datetime.datetime.now()
        today = now.date()

        # Define shift start times
        shift_times = {
            'morning': datetime.time(6, 0),  # 6 AM
            'afternoon': datetime.time(14, 0),  # 2 PM
            'evening': datetime.time(22, 0),  # 10 PM
            'night': datetime.time(22, 0)  # 10 PM (previous day)
        }

        start_time = shift_times.get(user_shift, datetime.time(6, 0))

        # For night shift, use previous day
        if user_shift == 'night' and now.time() < datetime.time(6, 0):
            today = today - datetime.timedelta(days=1)

        return datetime.datetime.combine(today, start_time)

    def _load_kpis(self, shift_start):
        """Load and display KPI data"""
        try:
            conn = getConnection()
            cursor = conn.cursor(dictionary=True)

            # Total sales
            sales_query, sales_params = ShiftSummaryModel.get_total_sales_query(
                self.cashier_id, shift_start)
            cursor.execute(sales_query, sales_params)
            result = cursor.fetchone()
            total_sales = float(result['total_sales'] or 0)
            self.shift_data['total_sales'] = total_sales
            self.view.update_kpi('sales', f"PHP {total_sales:,.2f}")

            # Items sold
            items_query, items_params = ShiftSummaryModel.get_items_sold_query(
                self.cashier_id, shift_start)
            cursor.execute(items_query, items_params)
            result = cursor.fetchone()
            items_sold = int(result['items_sold'] or 0)
            self.shift_data['items_sold'] = items_sold
            self.view.update_kpi('items', str(items_sold))

            # Transaction count
            trans_query, trans_params = ShiftSummaryModel.get_transaction_count_query(
                self.cashier_id, shift_start)
            cursor.execute(trans_query, trans_params)
            result = cursor.fetchone()
            trans_count = int(result['transaction_count'] or 0)
            self.shift_data['transaction_count'] = trans_count
            self.view.update_kpi('transactions', str(trans_count))

            # Average per sale
            avg_sale = total_sales / trans_count if trans_count > 0 else 0
            self.shift_data['avg_sale'] = avg_sale
            self.view.update_kpi('avg', f"PHP {avg_sale:,.2f}")

            cursor.close()
            conn.close()

        except Exception as e:
            print(f"Error loading KPIs: {e}")
            raise

    def _load_payment_breakdown(self, shift_start):
        """Load payment methods breakdown"""
        try:
            conn = getConnection()
            cursor = conn.cursor(dictionary=True)

            query, params = ShiftSummaryModel.get_payment_breakdown_query(
                self.cashier_id, shift_start)
            cursor.execute(query, params)
            results = cursor.fetchall()

            cursor.close()
            conn.close()

            if results:
                breakdown_text = ""
                for row in results:
                    method = row['payment_method'] or 'Unknown'
                    count = row['count']
                    total = float(row['total'] or 0)
                    breakdown_text += f"• {method}: {count} ({total:,.2f} PHP)\n"
                self.view.update_info_card(self.view.paymentFrame, breakdown_text.strip())
            else:
                self.view.update_info_card(self.view.paymentFrame, "No payment data")

        except Exception as e:
            print(f"Error loading payment breakdown: {e}")
            self.view.update_info_card(self.view.paymentFrame, "Error loading data")

    def _load_top_products(self, shift_start):
        """Load top 5 products sold"""
        try:
            conn = getConnection()
            cursor = conn.cursor(dictionary=True)

            query, params = ShiftSummaryModel.get_top_products_query(
                self.cashier_id, shift_start)
            cursor.execute(query, params)
            results = cursor.fetchall()

            cursor.close()
            conn.close()

            if results:
                products_text = ""
                for idx, row in enumerate(results, 1):
                    product = row['product_name']
                    qty = int(row['total_qty'])
                    products_text += f"{idx}. {product} ({qty} sold)\n"
                self.view.update_info_card(self.view.topProductsFrame, products_text.strip())
            else:
                self.view.update_info_card(self.view.topProductsFrame, "No products sold yet")

        except Exception as e:
            print(f"Error loading top products: {e}")
            self.view.update_info_card(self.view.topProductsFrame, "Error loading data")

    def _load_transactions(self, shift_start):
        """Load transactions table"""
        try:
            conn = getConnection()
            cursor = conn.cursor(dictionary=True)

            query, params = ShiftSummaryModel.get_shift_transactions_query(
                self.cashier_id, shift_start)
            cursor.execute(query, params)
            results = cursor.fetchall()

            cursor.close()
            conn.close()

            # Format for table
            formatted_data = []
            for row in results:
                time_str = row['transaction_date'].strftime("%I:%M %p")
                discount_text = row['discount_type'] if row['discount_type'] else "None"
                formatted_data.append([
                    row['transaction_number'],
                    time_str,
                    str(row['items_count']),
                    f"PHP {row['final_total']:.2f}",
                    "Cash",  # Default payment method display
                    discount_text
                ])

            self.view.update_transactions_table(formatted_data)

        except Exception as e:
            print(f"Error loading transactions: {e}")
            self.view.update_transactions_table([])

    def print_summary(self):
        """Print shift summary to PDF"""
        try:
            # Get save location
            cashier_name = self.current_user.get('full_name', 'CASHIER').replace(' ', '_')
            now = datetime.datetime.now()
            default_filename = f"ShiftSummary_{cashier_name}_{now.strftime('%Y%m%d_%H%M')}.pdf"

            filename, _ = QFileDialog.getSaveFileName(
                self.view, "Save Shift Summary", default_filename, "PDF Files (*.pdf)")

            if not filename:
                return

            # Generate PDF using matplotlib
            self._generate_pdf_summary(filename)

            QMessageBox.information(self.view, "Print Success",
                                    f"Shift summary saved to:\n{filename}")

        except Exception as e:
            QMessageBox.critical(self.view, "Print Error",
                                 f"Failed to generate PDF: {str(e)}")
            print(f"Error generating PDF: {e}")

    def _generate_pdf_summary(self, filename: str):
        """Generate PDF summary using matplotlib"""
        import matplotlib.pyplot as plt
        from matplotlib.backends.backend_pdf import PdfPages

        with PdfPages(filename) as pdf:
            fig = plt.figure(figsize=(8.5, 11))
            fig.suptitle("SHIFT SUMMARY REPORT", fontsize=20, fontweight='bold', y=0.98)

            # Cashier info
            cashier_name = self.current_user.get('full_name', 'CASHIER')
            shift = self.current_user.get('shift', 'N/A').capitalize()
            date_str = datetime.datetime.now().strftime("%B %d, %Y %I:%M %p")

            fig.text(0.1, 0.92, f"Cashier: {cashier_name}", fontsize=12, fontweight='bold')
            fig.text(0.1, 0.89, f"Shift: {shift}", fontsize=11)
            fig.text(0.1, 0.86, f"Date: {date_str}", fontsize=11)

            # KPI Summary
            fig.text(0.1, 0.80, "PERFORMANCE SUMMARY", fontsize=14, fontweight='bold',
                     bbox=dict(boxstyle='round', facecolor='#0d3b2b', alpha=0.1))

            kpi_y = 0.75
            kpis = [
                ("Total Sales:", f"PHP {self.shift_data.get('total_sales', 0):,.2f}"),
                ("Items Sold:", str(self.shift_data.get('items_sold', 0))),
                ("Transactions:", str(self.shift_data.get('transaction_count', 0))),
                ("Average per Sale:", f"PHP {self.shift_data.get('avg_sale', 0):,.2f}")
            ]

            for label, value in kpis:
                fig.text(0.15, kpi_y, label, fontsize=11, fontweight='bold')
                fig.text(0.5, kpi_y, value, fontsize=11, color='#1a4d2e')
                kpi_y -= 0.04

            # Footer
            fig.text(0.5, 0.05, "SyPoint POS System - Shift Summary",
                     ha='center', fontsize=9, style='italic', color='gray')

            pdf.savefig(fig, bbox_inches='tight')
            plt.close(fig)

    def navigate_to_transaction(self):
        """Navigate back to transaction window"""
        self.view.close()
        from Controller.Cashier.TransactionController import TransactionController
        self.trans_controller = TransactionController(self.current_user)
        self.trans_controller.open_transaction()

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