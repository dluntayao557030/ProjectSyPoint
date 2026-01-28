"""
ShiftSummaryController.py - FIXED
Controller for Shift Summary window
FIXED: Shows all transactions for the logged-in cashier from today, regardless of shift time
"""
import datetime
from PyQt6.QtWidgets import QMessageBox, QFileDialog
from Utilities.DatabaseConnection import getConnection
from View.CashierGUI.ShiftSummaryWindow import ShiftSummaryView
from Model.ShiftSummaryModel import ShiftSummaryModel
from matplotlib.backends.backend_pdf import PdfPages
import matplotlib.pyplot as plt


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
            # FIXED: Get today's date at midnight (start of day)
            # This ensures we show ALL transactions from today for this cashier
            today_start = datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)

            # Store for debugging
            print(f"Loading shift data for cashier_id={self.cashier_id}, today_start={today_start}")

            # Load KPIs
            self._load_kpis(today_start)

            # Load payment breakdown
            self._load_payment_breakdown(today_start)

            # Load top products
            self._load_top_products(today_start)

            # Load transactions table
            self._load_transactions(today_start)

        except Exception as e:
            QMessageBox.critical(self.view, "Error",
                                 f"Failed to load shift data: {str(e)}")
            print(f"Error loading shift data: {e}")

    def _load_kpis(self, today_start):
        """Load and display KPI data"""
        try:
            conn = getConnection()
            cursor = conn.cursor(dictionary=True)

            # Total sales
            sales_query, sales_params = ShiftSummaryModel.get_total_sales_query(
                self.cashier_id, today_start)
            print(f"Sales query: {sales_query}")
            print(f"Sales params: {sales_params}")
            cursor.execute(sales_query, sales_params)
            result = cursor.fetchone()
            total_sales = float(result['total_sales'] or 0)
            self.shift_data['total_sales'] = total_sales
            self.view.update_kpi('sales', f"PHP {total_sales:,.2f}")
            print(f"Total sales: {total_sales}")

            # Items sold
            items_query, items_params = ShiftSummaryModel.get_items_sold_query(
                self.cashier_id, today_start)
            cursor.execute(items_query, items_params)
            result = cursor.fetchone()
            items_sold = int(result['items_sold'] or 0)
            self.shift_data['items_sold'] = items_sold
            self.view.update_kpi('items', str(items_sold))
            print(f"Items sold: {items_sold}")

            # Transaction count
            trans_query, trans_params = ShiftSummaryModel.get_transaction_count_query(
                self.cashier_id, today_start)
            cursor.execute(trans_query, trans_params)
            result = cursor.fetchone()
            trans_count = int(result['transaction_count'] or 0)
            self.shift_data['transaction_count'] = trans_count
            self.view.update_kpi('transactions', str(trans_count))
            print(f"Transaction count: {trans_count}")

            # Average per sale
            avg_sale = total_sales / trans_count if trans_count > 0 else 0
            self.shift_data['avg_sale'] = avg_sale
            self.view.update_kpi('avg', f"PHP {avg_sale:,.2f}")

            cursor.close()
            conn.close()

        except Exception as e:
            print(f"Error loading KPIs: {e}")
            raise

    def _load_payment_breakdown(self, today_start):
        """Load payment methods breakdown"""
        try:
            conn = getConnection()
            cursor = conn.cursor(dictionary=True)

            query, params = ShiftSummaryModel.get_payment_breakdown_query(
                self.cashier_id, today_start)
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
                    if count > 0:  # Only show payment methods that were actually used
                        breakdown_text += f"• {method}: {count} ({total:,.2f} PHP)\n"
                self.view.update_info_card(self.view.paymentFrame,
                                           breakdown_text.strip() if breakdown_text else "No payment data")
            else:
                self.view.update_info_card(self.view.paymentFrame, "No payment data")

        except Exception as e:
            print(f"Error loading payment breakdown: {e}")
            self.view.update_info_card(self.view.paymentFrame, "Error loading data")

    def _load_top_products(self, today_start):
        """Load top 5 products sold"""
        try:
            conn = getConnection()
            cursor = conn.cursor(dictionary=True)

            query, params = ShiftSummaryModel.get_top_products_query(
                self.cashier_id, today_start)
            cursor.execute(query, params)
            results = cursor.fetchall()

            cursor.close()
            conn.close()

            if results:
                products_text = ""
                for i, row in enumerate(results, 1):
                    name = row['product_name']
                    qty = int(row['total_qty'])
                    products_text += f"{i}. {name} ({qty} sold)\n"
                self.view.update_info_card(self.view.topProductsFrame, products_text.strip())
            else:
                self.view.update_info_card(self.view.topProductsFrame, "No products sold")

        except Exception as e:
            print(f"Error loading top products: {e}")
            self.view.update_info_card(self.view.topProductsFrame, "Error loading data")

    def _load_transactions(self, today_start):
        """Load transactions table"""
        try:
            conn = getConnection()
            cursor = conn.cursor(dictionary=True)

            query, params = ShiftSummaryModel.get_shift_transactions_query(
                self.cashier_id, today_start)
            print(f"Transactions query: {query}")
            print(f"Transactions params: {params}")
            cursor.execute(query, params)
            results = cursor.fetchall()
            print(f"Transactions found: {len(results)}")

            cursor.close()
            conn.close()

            if results:
                table_data = []
                for row in results:
                    time_str = row['transaction_date'].strftime('%I:%M %p')
                    discount = row['discount_type'] or 'None'

                    table_data.append([
                        row['transaction_number'],
                        time_str,
                        str(row['items_count']),
                        f"PHP {row['final_total']:.2f}",
                        'Cash',  # Placeholder - update when payment table exists
                        discount
                    ])

                self.view.update_transactions_table(table_data)
            else:
                self.view.update_transactions_table([])

        except Exception as e:
            print(f"Error loading transactions: {e}")
            self.view.update_transactions_table([])

    def print_summary(self):
        """Generate and save shift summary as PDF"""
        try:
            # Get file path from user
            file_path, _ = QFileDialog.getSaveFileName(
                self.view,
                "Save Shift Summary",
                f"shift_summary_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                "PDF Files (*.pdf)"
            )

            if not file_path:
                return

            # Create PDF
            with PdfPages(file_path) as pdf:
                self._create_summary_pdf(pdf)

            QMessageBox.information(
                self.view,
                "Success",
                f"Shift summary saved to:\n{file_path}"
            )

        except Exception as e:
            QMessageBox.critical(
                self.view,
                "Error",
                f"Failed to generate PDF: {str(e)}"
            )
            print(f"Error generating PDF: {e}")

    def _create_summary_pdf(self, pdf):
        """Create PDF content for shift summary"""
        fig = plt.figure(figsize=(8.5, 11))
        fig.suptitle("SHIFT SUMMARY REPORT", fontsize=16, fontweight='bold', y=0.98)

        # Header info
        cashier_name = self.current_user.get('full_name', 'Unknown')
        shift = self.current_user.get('shift', 'Unknown').title()
        date_str = datetime.datetime.now().strftime('%B %d, %Y')

        fig.text(0.1, 0.92, f"Cashier: {cashier_name}", fontsize=11, fontweight='bold')
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