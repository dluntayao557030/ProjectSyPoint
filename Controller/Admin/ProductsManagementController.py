from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import QMessageBox, QTableWidgetItem
from PyQt6.QtCore import Qt
from Utilities.DatabaseConnection import getConnection
from View.AdminGUI.ProductsManagementWindow import (
    AdminProductsView, AddCategoryDialog, AddProductDialog, EditProductDialog
)
from Model.ProductsModel import AdminProductsModel


class AdminProductsController:
    """Controller for Admin Product Management"""

    def __init__(self, current_user: dict):
        self.current_user = current_user
        self.admin_id = current_user.get('user_id')
        self.view = None
        self.users_controller = None
        self.reports_controller = None
        self.dashboard_controller = None

        self.all_products = []
        self.all_categories = []

    def open_products_window(self):
        """Initialize and show products window"""
        self.view = AdminProductsView(self.current_user)
        self._load_categories()
        self._load_all_products()
        self._connect_signals()
        self.view.show()

    def _connect_signals(self):
        """Connect UI signals"""
        # Navigation
        self.view.dashboardButton.clicked.connect(self.navigate_to_dashboard)
        self.view.reportsButton.clicked.connect(self.navigate_to_reports)
        self.view.usersButton.clicked.connect(self.navigate_to_users)
        self.view.logoutButton.clicked.connect(self.logout)

        # Product actions
        self.view.applyFilterButton.clicked.connect(self.apply_filters)
        self.view.searchInput.returnPressed.connect(self.apply_filters)
        self.view.addCategoryButton.clicked.connect(self.show_add_category_dialog)
        self.view.addProductButton.clicked.connect(self.show_add_product_dialog)
        self.view.editProductButton.clicked.connect(self.show_edit_product_dialog)
        self.view.archiveProductButton.clicked.connect(self.archive_product)
        self.view.productsTable.itemClicked.connect(self.on_product_selected)

    def _load_categories(self):
        """Load all categories and populate filter"""
        try:
            conn = getConnection()
            cursor = conn.cursor(dictionary=True)

            query, params = AdminProductsModel.get_all_categories_query()
            cursor.execute(query, params)
            self.all_categories = cursor.fetchall()

            cursor.close()
            conn.close()

            # Populate category filter
            self.view.categoryFilter.clear()
            self.view.categoryFilter.addItem("All Categories", None)
            for cat in self.all_categories:
                self.view.categoryFilter.addItem(cat['category_name'], cat['category_id'])

        except Exception as e:
            QMessageBox.critical(self.view, "Error",
                                 f"Failed to load categories: {str(e)}")
            print(f"Error loading categories: {e}")

    def _load_all_products(self):
        """Load all products and populate table"""
        try:
            conn = getConnection()
            cursor = conn.cursor(dictionary=True)

            query, params = AdminProductsModel.get_all_products_query()
            cursor.execute(query, params)
            self.all_products = cursor.fetchall()

            cursor.close()
            conn.close()

            self._populate_products_table(self.all_products)

        except Exception as e:
            QMessageBox.critical(self.view, "Error",
                                 f"Failed to load products: {str(e)}")
            print(f"Error loading products: {e}")

    def _populate_products_table(self, products: list):
        """Populate products table - REMOVED Product ID column"""
        self.view.productsTable.setRowCount(len(products))
        for row, product in enumerate(products):
            status = "Active" if product.get('is_active', 0) == 1 else "Archived"
            created = product.get('created_at')
            created_str = created.strftime("%Y-%m-%d") if created else "N/A"

            # Store product_id as hidden data in the Reference column
            reference_item = QTableWidgetItem(product.get('reference_number', ''))
            reference_item.setData(Qt.ItemDataRole.UserRole, product.get('product_id'))

            items = [
                reference_item,  # Reference (with hidden product_id)
                QTableWidgetItem(product.get('product_name', '')),
                QTableWidgetItem(product.get('category_name', '')),
                QTableWidgetItem(f"PHP {product.get('price', 0):.2f}"),
                QTableWidgetItem(status),
                QTableWidgetItem(created_str)
            ]

            for col, item in enumerate(items):
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                item.setFlags(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable)

                # Set text color based on status
                if col == 4:  # Status column
                    if status == "Active":
                        item.setForeground(QColor("#1a4d2e"))  # Green for active
                    else:
                        item.setForeground(QColor("#d32f2f"))  # Red for archived

                self.view.productsTable.setItem(row, col, item)

    def on_product_selected(self, item):
        """Handle product selection"""
        row = item.row()
        try:
            # Get product_id from hidden data in Reference column
            reference_item = self.view.productsTable.item(row, 0)
            product_id = reference_item.data(Qt.ItemDataRole.UserRole)

            if product_id:
                self.view.selected_product_id = product_id

                # Find product data
                for product in self.all_products:
                    if product['product_id'] == product_id:
                        self.view.selected_product_data = product
                        break
        except (ValueError, Exception) as e:
            print(f"Error selecting product: {e}")
            self.view.clear_selection()

    def apply_filters(self):
        """Apply filters to products table"""
        keyword = self.view.searchInput.text().strip()
        category_id = self.view.categoryFilter.currentData()
        status = self.view.statusFilter.currentText()

        try:
            conn = getConnection()
            cursor = conn.cursor(dictionary=True)

            # Build query based on filters
            query, params = AdminProductsModel.get_filtered_products_query(
                keyword=keyword if keyword else None,
                category_id=category_id,
                status=status
            )
            cursor.execute(query, params)
            results = cursor.fetchall()

            cursor.close()
            conn.close()

            self._populate_products_table(results)

        except Exception as e:
            QMessageBox.critical(self.view, "Error",
                                 f"Failed to apply filters: {str(e)}")
            print(f"Error applying filters: {e}")

    def show_add_category_dialog(self):
        """Show add category dialog"""
        dialog = AddCategoryDialog(self.view)

        def add_category():
            category_name = dialog.get_category_name()

            if not category_name:
                QMessageBox.warning(dialog, "Input Required",
                                    "Please enter a category name.")
                return

            try:
                conn = getConnection()
                cursor = conn.cursor()

                # Check if exists
                check_query, check_params = AdminProductsModel.check_category_exists_query(category_name)
                cursor.execute(check_query, check_params)
                if cursor.fetchone()[0] > 0:
                    QMessageBox.warning(dialog, "Duplicate Category",
                                        "This category already exists.")
                    return

                # Insert category
                query, params = AdminProductsModel.create_category_query(category_name)
                cursor.execute(query, params)
                conn.commit()

                cursor.close()
                conn.close()

                dialog.accept()
                QMessageBox.information(self.view, "Success",
                                        "Category added successfully!")
                self._load_categories()

            except Exception as e:
                QMessageBox.critical(dialog, "Error",
                                     f"Failed to add category: {str(e)}")
                print(f"Error adding category: {e}")

        dialog.submitButton.clicked.connect(add_category)
        dialog.exec()

    def show_add_product_dialog(self):
        """Show add product dialog"""
        if not self.all_categories:
            QMessageBox.warning(self.view, "No Categories",
                                "Please add at least one category first.")
            return

        dialog = AddProductDialog(self.all_categories, self.view)

        def add_product():
            data = dialog.get_product_data()

            # Validation
            error = self._validate_product_data(data)
            if error:
                QMessageBox.warning(dialog, "Validation Error", error)
                return

            try:
                conn = getConnection()
                cursor = conn.cursor()

                # Check if reference exists
                check_query, check_params = AdminProductsModel.check_reference_exists_query(
                    data['reference_number'])
                cursor.execute(check_query, check_params)
                if cursor.fetchone()[0] > 0:
                    QMessageBox.warning(dialog, "Duplicate Reference",
                                        "This reference number already exists.")
                    return

                # Insert product
                query, params = AdminProductsModel.create_product_query(
                    reference_number=data['reference_number'],
                    product_name=data['product_name'],
                    price=data['price'],
                    category_id=data['category_id']
                )
                cursor.execute(query, params)
                conn.commit()

                cursor.close()
                conn.close()

                dialog.accept()
                QMessageBox.information(self.view, "Success",
                                        "Product added successfully!")
                self._load_all_products()

            except Exception as e:
                QMessageBox.critical(dialog, "Error",
                                     f"Failed to add product: {str(e)}")
                print(f"Error adding product: {e}")

        dialog.submitButton.clicked.connect(add_product)
        dialog.exec()

    def show_edit_product_dialog(self):
        """Show edit product dialog"""
        if not self.view.selected_product_id:
            QMessageBox.warning(self.view, "No Selection",
                                "Please select a product to edit.")
            return

        dialog = EditProductDialog(self.all_categories, self.view)
        dialog.populate_form(self.view.selected_product_data)

        def update_product():
            data = dialog.get_product_data()

            # Validation
            error = self._validate_product_data(data)
            if error:
                QMessageBox.warning(dialog, "Validation Error", error)
                return

            try:
                conn = getConnection()
                cursor = conn.cursor()

                # Check if new reference conflicts
                check_query, check_params = AdminProductsModel.check_reference_exists_except_query(
                    data['reference_number'], self.view.selected_product_id)
                cursor.execute(check_query, check_params)
                if cursor.fetchone()[0] > 0:
                    QMessageBox.warning(dialog, "Duplicate Reference",
                                        "This reference number is already used by another product.")
                    return

                # Update product
                query, params = AdminProductsModel.update_product_query(
                    product_id=self.view.selected_product_id,
                    reference_number=data['reference_number'],
                    product_name=data['product_name'],
                    price=data['price'],
                    category_id=data['category_id']
                )
                cursor.execute(query, params)
                conn.commit()

                cursor.close()
                conn.close()

                dialog.accept()
                QMessageBox.information(self.view, "Success",
                                        "Product updated successfully!")
                self._load_all_products()
                self.view.clear_selection()

            except Exception as e:
                QMessageBox.critical(dialog, "Error",
                                     f"Failed to update product: {str(e)}")
                print(f"Error updating product: {e}")

        dialog.submitButton.clicked.connect(update_product)
        dialog.exec()

    def archive_product(self):
        """Archive selected product"""
        if not self.view.selected_product_id:
            QMessageBox.warning(self.view, "No Selection",
                                "Please select a product to archive.")
            return

        product_name = self.view.selected_product_data.get('product_name', 'this product')

        reply = QMessageBox.question(
            self.view,
            "Confirm Archive",
            f"Are you sure you want to archive '{product_name}'?\n\n"
            "Archived products will not appear in active listings.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            try:
                conn = getConnection()
                cursor = conn.cursor()

                query, params = AdminProductsModel.archive_product_query(
                    self.view.selected_product_id)
                cursor.execute(query, params)
                conn.commit()

                cursor.close()
                conn.close()

                QMessageBox.information(self.view, "Success",
                                        "Product archived successfully!")
                self._load_all_products()
                self.view.clear_selection()

            except Exception as e:
                QMessageBox.critical(self.view, "Error",
                                     f"Failed to archive product: {str(e)}")
                print(f"Error archiving product: {e}")

    @staticmethod
    def _validate_product_data(data: dict):
        """Validate product data"""
        if not data['reference_number']:
            return "Reference number is required."
        if not data['product_name']:
            return "Product name is required."
        if data['price'] <= 0:
            return "Price must be greater than zero."
        if not data['category_id']:
            return "Please select a category."
        return None

    def navigate_to_dashboard(self):
        """Navigate to dashboard"""
        self.view.close()
        from Controller.Admin.AdminDashboardController import AdminDashboardController
        self.dashboard_controller = AdminDashboardController(self.current_user)
        self.dashboard_controller.open_dashboard()

    def navigate_to_reports(self):
        """Navigate to reports"""
        self.view.close()
        from Controller.Admin.ReportsController import AdminReportsController
        self.reports_controller = AdminReportsController(self.current_user)
        self.reports_controller.open_reports()

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