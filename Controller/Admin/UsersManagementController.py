from PyQt6.QtWidgets import QMessageBox, QTableWidgetItem
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor
from Utilities.DatabaseConnection import getConnection
from View.AdminGUI.UsersManagementWindow import AdminUsersView, AddUserDialog, EditUserDialog
from Model.UsersModel import AdminUsersModel


class AdminUsersController:
    """Controller for Admin User Management"""

    def __init__(self, current_user: dict):
        self.current_user = current_user
        self.admin_id = current_user.get('user_id')
        self.view = None
        self.add_dialog = None
        self.edit_dialog = None
        self.dashboard_controller = None
        self.products_controller = None
        self.reports_controller = None

        self.all_users = []

    def open_users_window(self):
        """Initialize and show users window"""
        self.view = AdminUsersView(self.current_user)
        self._load_all_users()
        self._connect_signals()
        self.view.show()

    def _connect_signals(self):
        """Connect UI signals"""
        # Navigation
        self.view.dashboardButton.clicked.connect(self.navigate_to_dashboard)
        self.view.productsButton.clicked.connect(self.navigate_to_products)
        self.view.reportsButton.clicked.connect(self.navigate_to_reports)
        self.view.logoutButton.clicked.connect(self.logout)

        # User actions
        self.view.searchButton.clicked.connect(self.search_users)
        self.view.searchInput.returnPressed.connect(self.search_users)
        self.view.addUserButton.clicked.connect(self.show_add_user_dialog)
        self.view.editUserButton.clicked.connect(self.show_edit_user_dialog)
        self.view.usersTable.itemClicked.connect(self.on_user_selected)

    def _load_all_users(self):
        """Load all users and populate table"""
        try:
            conn = getConnection()
            cursor = conn.cursor(dictionary=True)

            query, params = AdminUsersModel.get_all_users_query()
            cursor.execute(query, params)
            self.all_users = cursor.fetchall()

            cursor.close()
            conn.close()

            self._populate_users_table(self.all_users)

        except Exception as e:
            QMessageBox.critical(self.view, "Error",
                                 f"Failed to load users: {str(e)}")
            print(f"Error loading users: {e}")

    def _populate_users_table(self, users: list):
        """Populate users table - REMOVED User ID column"""
        self.view.usersTable.setRowCount(len(users))
        for row, user in enumerate(users):
            status = "Active" if user.get('is_active', 0) == 1 else "Inactive"

            # Store user_id as hidden data in the Username column
            username_item = QTableWidgetItem(user.get('username', ''))
            username_item.setData(Qt.ItemDataRole.UserRole, user.get('user_id'))

            items = [
                username_item,  # Username (with hidden user_id)
                QTableWidgetItem(user.get('full_name', '')),
                QTableWidgetItem(user.get('role', '').capitalize()),
                QTableWidgetItem(user.get('shift', '').capitalize()),
                QTableWidgetItem(status)
            ]

            for col, item in enumerate(items):
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                item.setFlags(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable)

                # Set text color based on status
                if col == 4:  # Status column
                    if status == "Active":
                        item.setForeground(QColor("#1a4d2e"))  # Green for active
                    else:
                        item.setForeground(QColor("#d32f2f"))  # Red for inactive

                # Set text color based on role
                if col == 2:  # Role column
                    if user.get('role') == 'admin':
                        item.setForeground(QColor("#1a4d2e"))  # Green for admin
                    else:
                        item.setForeground(QColor("#1976d2"))  # Blue for cashier

                self.view.usersTable.setItem(row, col, item)

    def on_user_selected(self, item):
        """Handle user selection"""
        row = item.row()
        try:
            # Get user_id from hidden data in Username column
            username_item = self.view.usersTable.item(row, 0)
            user_id = username_item.data(Qt.ItemDataRole.UserRole)

            if user_id:
                self.view.selected_user_id = user_id

                # Find user data
                for user in self.all_users:
                    if user['user_id'] == user_id:
                        self.view.selected_user_data = user
                        break
        except (ValueError, Exception) as e:
            print(f"Error selecting user: {e}")
            self.view.clear_selection()

    def search_users(self):
        """Search users by keyword"""
        keyword = self.view.searchInput.text().strip()

        if not keyword:
            self._populate_users_table(self.all_users)
            return

        try:
            conn = getConnection()
            cursor = conn.cursor(dictionary=True)

            query, params = AdminUsersModel.search_users_query(keyword)
            cursor.execute(query, params)
            results = cursor.fetchall()

            cursor.close()
            conn.close()

            self._populate_users_table(results)

        except Exception as e:
            QMessageBox.critical(self.view, "Error",
                                 f"Search failed: {str(e)}")
            print(f"Error searching users: {e}")

    def show_add_user_dialog(self):
        """Show add user dialog"""
        self.add_dialog = AddUserDialog(self.view)
        self.add_dialog.submitButton.clicked.connect(self.add_user)
        self.add_dialog.exec()

    def add_user(self):
        """Add new user"""
        data = self.add_dialog.get_user_data()

        # Validation
        error = self._validate_user_data(data, is_new=True)
        if error:
            QMessageBox.warning(self.add_dialog, "Validation Error", error)
            return

        try:
            conn = getConnection()
            cursor = conn.cursor()

            # Check if username exists
            check_query, check_params = AdminUsersModel.check_username_exists_query(data['username'])
            cursor.execute(check_query, check_params)
            if cursor.fetchone()[0] > 0:
                QMessageBox.warning(self.add_dialog, "Username Taken",
                                    "This username already exists. Please choose another.")
                return

            # Insert user
            query, params = AdminUsersModel.create_user_query(
                username=data['username'],
                password=data['password'],
                full_name=data['full_name'],
                role=data['role'],
                shift=data['shift']
            )
            cursor.execute(query, params)
            conn.commit()

            cursor.close()
            conn.close()

            self.add_dialog.accept()
            QMessageBox.information(self.view, "Success",
                                    "User added successfully!")
            self._load_all_users()

        except Exception as e:
            QMessageBox.critical(self.add_dialog, "Error",
                                 f"Failed to add user: {str(e)}")
            print(f"Error adding user: {e}")

    def show_edit_user_dialog(self):
        """Show edit user dialog"""
        if not self.view.selected_user_id:
            QMessageBox.warning(self.view, "No Selection",
                                "Please select a user to edit.")
            return

        self.edit_dialog = EditUserDialog(self.view)
        self.edit_dialog.populate_form(self.view.selected_user_data)
        self.edit_dialog.submitButton.clicked.connect(self.update_user)
        self.edit_dialog.exec()

    def update_user(self):
        """Update existing user"""
        data = self.edit_dialog.get_user_data()

        # Validation
        error = self._validate_user_data(data, is_new=False)
        if error:
            QMessageBox.warning(self.edit_dialog, "Validation Error", error)
            return

        try:
            conn = getConnection()
            cursor = conn.cursor()

            # Check if new username conflicts
            check_query, check_params = AdminUsersModel.check_username_exists_except_query(
                data['username'], self.view.selected_user_id)
            cursor.execute(check_query, check_params)
            if cursor.fetchone()[0] > 0:
                QMessageBox.warning(self.edit_dialog, "Username Taken",
                                    "This username is already taken by another user.")
                return

            # Update user
            query, params = AdminUsersModel.update_user_query(
                user_id=self.view.selected_user_id,
                username=data['username'],
                password=data['password'],
                full_name=data['full_name'],
                role=data['role'],
                shift=data['shift'],
                is_active=data['is_active']
            )
            cursor.execute(query, params)
            conn.commit()

            cursor.close()
            conn.close()

            self.edit_dialog.accept()
            QMessageBox.information(self.view, "Success",
                                    "User updated successfully!")
            self._load_all_users()
            self.view.clear_selection()

        except Exception as e:
            QMessageBox.critical(self.edit_dialog, "Error",
                                 f"Failed to update user: {str(e)}")
            print(f"Error updating user: {e}")

    @staticmethod
    def _validate_user_data(data: dict, is_new: bool = True):
        """Validate user form data"""
        if not data['username']:
            return "Username is required."
        if len(data['username']) < 3:
            return "Username must be at least 3 characters."
        if not data['full_name']:
            return "Full name is required."
        if is_new and not data['password']:
            return "Password is required for new users."
        if data['password'] and len(data['password']) < 4:
            return "Password must be at least 4 characters."
        if not data['role']:
            return "Please select a role."
        return None

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

    def navigate_to_reports(self):
        """Navigate to reports"""
        self.view.close()
        from Controller.Admin.ReportsController import AdminReportsController
        self.reports_controller = AdminReportsController(self.current_user)
        self.reports_controller.open_reports()

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