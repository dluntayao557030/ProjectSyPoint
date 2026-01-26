import datetime
from PyQt6.QtWidgets import QMessageBox
from Utilities.DatabaseConnection import getConnection
from View.AdminGUI.AdminDashboard import AdminDashboardView, KPIDetailDialog
from Model.AdminDashboardModel import AdminDashboardModel


class AdminDashboardController:
    """Controller for Admin Dashboard - Recent Transactions Section Removed"""

    def __init__(self, current_user: dict):
        self.current_user = current_user
        self.admin_id = current_user.get('user_id')
        self.view = None
        self.users_controller = None
        self.products_controller = None
        self.reports_controller = None

        # Dashboard data
        self.kpi_data = {}

    def open_dashboard(self):
        """Initialize and show dashboard"""
        self.view = AdminDashboardView(self.current_user)
        self._load_dashboard_data()
        self._connect_signals()
        self.view.show()

    def _connect_signals(self):
        """Connect UI signals"""
        # Navigation
        self.view.productsButton.clicked.connect(self.navigate_to_products)
        self.view.reportsButton.clicked.connect(self.navigate_to_reports)
        self.view.usersButton.clicked.connect(self.navigate_to_users)
        self.view.logoutButton.clicked.connect(self.logout)

        # Chart filter
        self.view.chartFilterCombo.currentTextChanged.connect(self.update_sales_chart)

        # KPI card clicks
        self.view.totalSalesCard.mousePressEvent = lambda e: self.show_sales_detail()
        self.view.transactionsCard.mousePressEvent = lambda e: self.show_transactions_detail()
        self.view.productsCard.mousePressEvent = lambda e: self.show_products_detail()
        self.view.avgSaleCard.mousePressEvent = lambda e: self.show_transactions_detail()

    def _load_dashboard_data(self):
        """Load all dashboard data"""
        try:
            self._load_kpis()
            self.update_sales_chart("Last 7 Days")
        except Exception as e:
            QMessageBox.critical(self.view, "Error",
                                 f"Failed to load dashboard data: {str(e)}")
            print(f"Error loading dashboard: {e}")

    def _load_kpis(self):
        """Load KPI data"""
        try:
            conn = getConnection()
            cursor = conn.cursor(dictionary=True)
            today = datetime.date.today()

            # Total Sales Today
            query, params = AdminDashboardModel.get_total_sales_today_query(today)
            cursor.execute(query, params)
            result = cursor.fetchone()
            total_sales = float(result['total_sales'] or 0)
            self.kpi_data['total_sales'] = total_sales
            self.view.update_kpi('totalSales', f"PHP {total_sales:,.2f}")

            # Transactions Today
            query, params = AdminDashboardModel.get_transactions_today_query(today)
            cursor.execute(query, params)
            result = cursor.fetchone()
            transactions = int(result['transaction_count'] or 0)
            self.kpi_data['transactions'] = transactions
            self.view.update_kpi('transactions', str(transactions))

            # Products Sold Today
            query, params = AdminDashboardModel.get_products_sold_today_query(today)
            cursor.execute(query, params)
            result = cursor.fetchone()
            products = int(result['products_sold'] or 0)
            self.kpi_data['products'] = products
            self.view.update_kpi('products', str(products))

            # Average Sale
            avg_sale = total_sales / transactions if transactions > 0 else 0
            self.kpi_data['avg_sale'] = avg_sale
            self.view.update_kpi('avgSale', f"PHP {avg_sale:,.2f}")

            cursor.close()
            conn.close()

        except Exception as e:
            print(f"Error loading KPIs: {e}")
            raise

    def update_sales_chart(self, filter_text: str):
        """Update sales chart based on filter"""
        try:
            conn = getConnection()
            cursor = conn.cursor(dictionary=True)

            # Determine date range
            today = datetime.date.today()
            if filter_text == "Last 7 Days":
                start_date = today - datetime.timedelta(days=6)
            elif filter_text == "Last 30 Days":
                start_date = today - datetime.timedelta(days=29)
            elif filter_text == "This Month":
                start_date = today.replace(day=1)
            elif filter_text == "Last Month":
                first_this_month = today.replace(day=1)
                start_date = (first_this_month - datetime.timedelta(days=1)).replace(day=1)
                today = first_this_month - datetime.timedelta(days=1)
            else:
                start_date = today - datetime.timedelta(days=6)

            # Get sales data
            query, params = AdminDashboardModel.get_sales_by_date_query(start_date, today)
            cursor.execute(query, params)
            results = cursor.fetchall()

            cursor.close()
            conn.close()

            # Prepare data for chart
            if results:
                dates = [row['sale_date'].strftime("%m/%d") for row in results]
                sales = [float(row['total_sales'] or 0) for row in results]
            else:
                dates = ["No Data"]
                sales = [0]

            self.view.plot_sales_chart(dates, sales, f"Sales Trend - {filter_text}")

        except Exception as e:
            print(f"Error updating chart: {e}")

    def show_sales_detail(self):
        """Show detailed sales breakdown - NO IDs"""
        try:
            dialog = KPIDetailDialog("Total Sales Today", self.view)

            conn = getConnection()
            cursor = conn.cursor(dictionary=True)
            today = datetime.date.today()

            query, params = AdminDashboardModel.get_sales_detail_query(today)
            cursor.execute(query, params)
            results = cursor.fetchall()

            cursor.close()
            conn.close()

            columns = ["Transaction #", "Time", "Cashier", "Subtotal", "Discount", "Total"]
            data = []
            for row in results:
                time_str = row['transaction_date'].strftime("%I:%M %p")
                data.append([
                    row['transaction_number'],
                    time_str,
                    row['cashier_name'],
                    f"PHP {row['subtotal']:.2f}",
                    f"PHP {row['discount_amount']:.2f}",
                    f"PHP {row['final_total']:.2f}"
                ])

            dialog.populate_table(columns, data)
            dialog.exec()

        except Exception as e:
            QMessageBox.critical(self.view, "Error", f"Failed to load details: {str(e)}")
            print(f"Error showing sales detail: {e}")

    def show_transactions_detail(self):
        """Show detailed transactions list - NO IDs"""
        try:
            dialog = KPIDetailDialog("Transactions Today", self.view)

            conn = getConnection()
            cursor = conn.cursor(dictionary=True)
            today = datetime.date.today()

            query, params = AdminDashboardModel.get_transactions_detail_query(today)
            cursor.execute(query, params)
            results = cursor.fetchall()

            cursor.close()
            conn.close()

            columns = ["Transaction #", "Time", "Cashier", "Items", "Total"]
            data = []
            for row in results:
                time_str = row['transaction_date'].strftime("%I:%M %p")
                data.append([
                    row['transaction_number'],
                    time_str,
                    row['cashier_name'],
                    str(row['items_count']),
                    f"PHP {row['final_total']:.2f}"
                ])

            dialog.populate_table(columns, data)
            dialog.exec()

        except Exception as e:
            QMessageBox.critical(self.view, "Error", f"Failed to load details: {str(e)}")
            print(f"Error showing transactions detail: {e}")

    def show_products_detail(self):
        """Show detailed products sold today - NO IDs"""
        try:
            dialog = KPIDetailDialog("Products Sold Today", self.view)

            conn = getConnection()
            cursor = conn.cursor(dictionary=True)
            today = datetime.date.today()

            query, params = AdminDashboardModel.get_products_detail_query(today)
            cursor.execute(query, params)
            results = cursor.fetchall()

            cursor.close()
            conn.close()

            columns = ["Product Name", "Quantity Sold", "Revenue"]
            data = []
            for row in results:
                data.append([
                    row['product_name'],
                    str(row['quantity_sold']),
                    f"PHP {row['revenue']:.2f}"
                ])

            dialog.populate_table(columns, data)
            dialog.exec()

        except Exception as e:
            QMessageBox.critical(self.view, "Error", f"Failed to load details: {str(e)}")
            print(f"Error showing products detail: {e}")

    def navigate_to_products(self):
        """Navigate to product management"""
        self.view.close()
        from Controller.Admin.ProductsManagementController import AdminProductsController
        self.products_controller = AdminProductsController(self.current_user)
        self.products_controller.open_products_window()

    def navigate_to_reports(self):
        """Navigate to reports"""
        self.view.close()
        from Controller.Admin.ReportsController import AdminReportsController
        self.reports_controller = AdminReportsController(self.current_user)
        self.reports_controller.open_reports()

    def navigate_to_users(self):
        """Navigate to user management"""
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