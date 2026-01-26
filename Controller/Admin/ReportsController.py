import datetime
from PyQt6.QtWidgets import QMessageBox, QFileDialog
from Utilities.DatabaseConnection import getConnection
from View.AdminGUI.ReportsWindow import AdminReportsView, ReportSummaryDialog
from Model.ReportsModel import AdminReportsModel


class AdminReportsController:
    """Controller for Admin Reports"""

    def __init__(self, current_user: dict):
        self.current_user = current_user
        self.admin_id = current_user.get('user_id')
        self.view = None
        self.dashboard_controller = None
        self.users_controller = None
        self.products_controller = None

        # Report data
        self.current_report_type = None
        self.current_report_data = []

    def open_reports(self):
        """Initialize and show reports window"""
        self.view = AdminReportsView(self.current_user)
        self._connect_signals()
        self.view.show()

    def _connect_signals(self):
        """Connect UI signals"""
        # Navigation
        self.view.dashboardButton.clicked.connect(self.navigate_to_dashboard)
        self.view.productsButton.clicked.connect(self.navigate_to_products)
        self.view.usersButton.clicked.connect(self.navigate_to_users)
        self.view.logoutButton.clicked.connect(self.logout)

        # Report actions
        self.view.generateButton.clicked.connect(self.generate_report)
        self.view.viewSummaryButton.clicked.connect(self.view_summary)
        self.view.printButton.clicked.connect(self.print_report)

    def generate_report(self):
        """Generate selected report"""
        report_type = self.view.reportTypeCombo.currentText()

        if report_type == "-- Select Report Type --":
            QMessageBox.warning(self.view, "Selection Required",
                                "Please select a report type.")
            return

        from_date = self.view.fromDateEdit.date().toPyDate()
        to_date = self.view.toDateEdit.date().toPyDate()

        if from_date > to_date:
            QMessageBox.warning(self.view, "Invalid Date Range",
                                "From date cannot be later than To date.")
            return

        self.current_report_type = report_type

        try:
            # Generate based on report type
            if report_type == "Daily Sales Report":
                self._generate_daily_sales_report(from_date, to_date)
            elif report_type == "Shift Summary Report":
                self._generate_shift_summary_report(from_date, to_date)
            elif report_type == "Cashier Performance Report":
                self._generate_cashier_performance_report(from_date, to_date)
            elif report_type == "Product Sales Report":
                self._generate_product_sales_report(from_date, to_date)
            elif report_type == "Discount Usage Report":
                self._generate_discount_usage_report(from_date, to_date)

            # Enable action buttons
            self.view.viewSummaryButton.setEnabled(True)
            self.view.printButton.setEnabled(True)

        except Exception as e:
            QMessageBox.critical(self.view, "Error",
                                 f"Failed to generate report: {str(e)}")
            print(f"Error generating report: {e}")

    def _generate_daily_sales_report(self, from_date, to_date):
        """Generate Daily Sales Report"""
        try:
            conn = getConnection()
            cursor = conn.cursor(dictionary=True)

            query, params = AdminReportsModel.get_daily_sales_report_query(from_date, to_date)
            cursor.execute(query, params)
            results = cursor.fetchall()

            cursor.close()
            conn.close()

            columns = ["Date", "Transactions", "Gross Sales", "Discounts", "Net Sales"]
            data = []
            for row in results:
                data.append([
                    row['sale_date'].strftime("%Y-%m-%d"),
                    str(row['transaction_count']),
                    f"PHP {row['gross_sales']:.2f}",
                    f"PHP {row['total_discounts']:.2f}",
                    f"PHP {row['net_sales']:.2f}"
                ])

            self.current_report_data = results
            self.view.populate_report_table(columns, data)

        except Exception as e:
            print(f"Error generating daily sales report: {e}")
            raise

    def _generate_shift_summary_report(self, from_date, to_date):
        """Generate Shift Summary Report"""
        try:
            conn = getConnection()
            cursor = conn.cursor(dictionary=True)

            query, params = AdminReportsModel.get_shift_summary_report_query(from_date, to_date)
            cursor.execute(query, params)
            results = cursor.fetchall()

            cursor.close()
            conn.close()

            columns = ["Date", "Cashier", "Shift", "Transactions", "Total Sales", "Discounts"]
            data = []
            for row in results:
                data.append([
                    row['shift_date'].strftime("%Y-%m-%d"),
                    row['cashier_name'],
                    row['shift'].capitalize(),
                    str(row['transaction_count']),
                    f"PHP {row['total_sales']:.2f}",
                    f"PHP {row['total_discounts']:.2f}"
                ])

            self.current_report_data = results
            self.view.populate_report_table(columns, data)

        except Exception as e:
            print(f"Error generating shift summary report: {e}")
            raise

    def _generate_cashier_performance_report(self, from_date, to_date):
        """Generate Cashier Performance Report"""
        try:
            conn = getConnection()
            cursor = conn.cursor(dictionary=True)

            query, params = AdminReportsModel.get_cashier_performance_report_query(from_date, to_date)
            cursor.execute(query, params)
            results = cursor.fetchall()

            cursor.close()
            conn.close()

            columns = ["Cashier", "Transactions", "Total Sales", "Avg Transaction", "Efficiency"]
            data = []
            for row in results:
                avg_trans = float(row['avg_transaction'])
                efficiency = "High" if avg_trans > 500 else "Medium" if avg_trans > 200 else "Low"

                # Color code efficiency
                efficiency_cell = str(efficiency)

                data.append([
                    row['cashier_name'],
                    str(row['transaction_count']),
                    f"PHP {row['total_sales']:.2f}",
                    f"PHP {avg_trans:.2f}",
                    efficiency_cell
                ])

            self.current_report_data = results
            self.view.populate_report_table(columns, data)

        except Exception as e:
            print(f"Error generating cashier performance report: {e}")
            raise

    def _generate_product_sales_report(self, from_date, to_date):
        """Generate Product Sales Report"""
        try:
            conn = getConnection()
            cursor = conn.cursor(dictionary=True)

            query, params = AdminReportsModel.get_product_sales_report_query(from_date, to_date)
            cursor.execute(query, params)
            results = cursor.fetchall()

            cursor.close()
            conn.close()

            columns = ["Product Name", "Category", "Qty Sold", "Revenue", "Avg Price"]
            data = []
            for row in results:
                data.append([
                    row['product_name'],
                    row['category_name'],
                    str(row['quantity_sold']),
                    f"PHP {row['revenue']:.2f}",
                    f"PHP {row['avg_price']:.2f}"
                ])

            self.current_report_data = results
            self.view.populate_report_table(columns, data)

        except Exception as e:
            print(f"Error generating product sales report: {e}")
            raise

    def _generate_discount_usage_report(self, from_date, to_date):
        """Generate Discount Usage Report"""
        try:
            conn = getConnection()
            cursor = conn.cursor(dictionary=True)

            query, params = AdminReportsModel.get_discount_usage_report_query(from_date, to_date)
            cursor.execute(query, params)
            results = cursor.fetchall()

            cursor.close()
            conn.close()

            columns = ["Discount Type", "Usage Count", "Total Discount", "Avg Discount", "% of Total"]

            # Calculate total discount for percentage
            total_discount = sum(float(row['total_discount_amount'] or 0) for row in results)

            data = []
            for row in results:
                discount_amt = float(row['total_discount_amount'] or 0)
                percentage = (discount_amt / total_discount * 100) if total_discount > 0 else 0
                data.append([
                    row['discount_type'] or "None",
                    str(row['usage_count']),
                    f"PHP {discount_amt:.2f}",
                    f"PHP {row['avg_discount']:.2f}",
                    f"{percentage:.1f}%"
                ])

            self.current_report_data = results
            self.view.populate_report_table(columns, data)

        except Exception as e:
            print(f"Error generating discount usage report: {e}")
            raise

    def view_summary(self):
        """View report summary"""
        if not self.current_report_data:
            QMessageBox.information(self.view, "No Data",
                                    "Please generate a report first.")
            return

        try:
            dialog = ReportSummaryDialog(self.current_report_type, self.view)

            from_date = self.view.fromDateEdit.date().toString("MMM dd, yyyy")
            to_date = self.view.toDateEdit.date().toString("MMM dd, yyyy")
            date_range = f"{from_date} to {to_date}"

            # Generate summary based on report type
            summary = self._generate_summary_text()

            dialog.set_summary_data(date_range, summary)
            dialog.exec()

        except Exception as e:
            QMessageBox.critical(self.view, "Error",
                                 f"Failed to generate summary: {str(e)}")
            print(f"Error viewing summary: {e}")

    def _generate_summary_text(self):
        """Generate summary statistics text"""
        summary_lines = []
        summary_lines.append(f"Report: {self.current_report_type}")
        summary_lines.append(f"Total Records: {len(self.current_report_data)}")
        summary_lines.append("-" * 50)

        if self.current_report_type == "Daily Sales Report":
            total_trans = sum(int(row['transaction_count']) for row in self.current_report_data)
            total_gross = sum(float(row['gross_sales']) for row in self.current_report_data)
            total_discounts = sum(float(row['total_discounts']) for row in self.current_report_data)
            total_net = sum(float(row['net_sales']) for row in self.current_report_data)

            summary_lines.append(f"Total Transactions: {total_trans}")
            summary_lines.append(f"Total Gross Sales: PHP {total_gross:,.2f}")
            summary_lines.append(f"Total Discounts: PHP {total_discounts:,.2f}")
            summary_lines.append(f"Total Net Sales: PHP {total_net:,.2f}")
            summary_lines.append(f"Average Daily Sales: PHP {total_net / len(self.current_report_data):,.2f}")

        elif self.current_report_type == "Shift Summary Report":
            total_trans = sum(int(row['transaction_count']) for row in self.current_report_data)
            total_sales = sum(float(row['total_sales']) for row in self.current_report_data)

            summary_lines.append(f"Total Shifts: {len(self.current_report_data)}")
            summary_lines.append(f"Total Transactions: {total_trans}")
            summary_lines.append(f"Total Sales: PHP {total_sales:,.2f}")
            summary_lines.append(f"Average per Shift: PHP {total_sales / len(self.current_report_data):,.2f}")

        elif self.current_report_type == "Cashier Performance Report":
            total_trans = sum(int(row['transaction_count']) for row in self.current_report_data)
            total_sales = sum(float(row['total_sales']) for row in self.current_report_data)

            top_cashier = max(self.current_report_data, key=lambda x: float(x['total_sales']))

            summary_lines.append(f"Total Cashiers: {len(self.current_report_data)}")
            summary_lines.append(f"Total Transactions: {total_trans}")
            summary_lines.append(f"Total Sales: PHP {total_sales:,.2f}")
            summary_lines.append(f"Top Performer: {top_cashier['cashier_name']}")
            summary_lines.append(f"  Sales: PHP {top_cashier['total_sales']:,.2f}")

        elif self.current_report_type == "Product Sales Report":
            total_qty = sum(int(row['quantity_sold']) for row in self.current_report_data)
            total_revenue = sum(float(row['revenue']) for row in self.current_report_data)

            top_product = max(self.current_report_data, key=lambda x: float(x['revenue']))

            summary_lines.append(f"Total Products: {len(self.current_report_data)}")
            summary_lines.append(f"Total Quantity Sold: {total_qty}")
            summary_lines.append(f"Total Revenue: PHP {total_revenue:,.2f}")
            summary_lines.append(f"Best Seller: {top_product['product_name']}")
            summary_lines.append(f"  Revenue: PHP {top_product['revenue']:,.2f}")

        elif self.current_report_type == "Discount Usage Report":
            total_usage = sum(int(row['usage_count']) for row in self.current_report_data)
            total_discount = sum(float(row['total_discount_amount']) for row in self.current_report_data)

            summary_lines.append(f"Discount Types: {len(self.current_report_data)}")
            summary_lines.append(f"Total Usage: {total_usage}")
            summary_lines.append(f"Total Discount Amount: PHP {total_discount:,.2f}")
            summary_lines.append(f"Average Discount: PHP {total_discount / total_usage:,.2f}")

        return "\n".join(summary_lines)

    def print_report(self):
        """Print report to PDF"""
        if not self.current_report_data:
            QMessageBox.information(self.view, "No Data",
                                    "Please generate a report first.")
            return

        try:
            # Get save location
            now = datetime.datetime.now()
            report_type_safe = self.current_report_type.replace(" ", "_")
            default_filename = f"SyPoint_{report_type_safe}_{now.strftime('%Y%m%d_%H%M')}.pdf"

            filename, _ = QFileDialog.getSaveFileName(
                self.view, "Save Report", default_filename, "PDF Files (*.pdf)")

            if not filename:
                return

            # Generate PDF
            self._generate_pdf_report(filename)

            QMessageBox.information(self.view, "Export Success",
                                    f"Report saved to:\n{filename}")

        except Exception as e:
            QMessageBox.critical(self.view, "Export Error",
                                 f"Failed to export PDF: {str(e)}")
            print(f"Error exporting PDF: {e}")

    def _generate_pdf_report(self, filename: str):
        """Generate PDF report using matplotlib"""
        import matplotlib.pyplot as plt
        from matplotlib.backends.backend_pdf import PdfPages

        with PdfPages(filename) as pdf:
            fig = plt.figure(figsize=(11, 8.5))

            # Header
            fig.text(0.5, 0.95, "SYPOINT POS SYSTEM", ha='center', fontsize=20,
                     fontweight='bold')
            fig.text(0.5, 0.92, self.current_report_type, ha='center', fontsize=16,
                     fontweight='bold')

            # Date range
            from_date = self.view.fromDateEdit.date().toString("MMM dd, yyyy")
            to_date = self.view.toDateEdit.date().toString("MMM dd, yyyy")
            fig.text(0.5, 0.88, f"Period: {from_date} to {to_date}", ha='center',
                     fontsize=11)

            # Generated date
            now = datetime.datetime.now()
            fig.text(0.5, 0.85, f"Generated: {now.strftime('%B %d, %Y %I:%M %p')}",
                     ha='center', fontsize=10, style='italic', color='gray')

            # Summary statistics
            summary_text = self._generate_summary_text()
            fig.text(0.1, 0.75, summary_text, fontsize=10, family='monospace',
                     verticalalignment='top')

            # Footer
            fig.text(0.5, 0.05, "This is a computer-generated report", ha='center',
                     fontsize=8, style='italic', color='gray')

            pdf.savefig(fig, bbox_inches='tight')
            plt.close(fig)

    def navigate_to_dashboard(self):
        """Navigate to dashboard"""
        self.view.close()
        from Controller.Admin.AdminDashboardController import AdminDashboardController
        self.dashboard_controller = AdminDashboardController(self.current_user)
        self.dashboard_controller.open_dashboard()

    def navigate_to_products(self):
        """Navigate to products"""
        self.view.close()
        from Controller.Admin.ProductsManagementController import AdminProductsController
        self.products_controller = AdminProductsController(self.current_user)
        self.products_controller.open_products_window()

    def navigate_to_users(self):
        """Navigate to users"""
        self.view.close()
        from Controller.Admin.UsersManagementController import AdminUsersController
        self.users_controller = AdminUsersController(self.current_user)
        self.users_controller.open_users_window()

    def logout(self):
        """Logout"""
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