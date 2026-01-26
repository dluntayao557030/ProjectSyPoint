from View.LoginGUI.Login import LoginView, LoginErrorPopup, LoginSuccessPopup
from Model.Authentication.LoginModel import LoginModel
from mysql.connector import Error


class LoginController:
    """
    Controller for Login. Handles user input validation and executes database queries.
    Controller now manages cursor.execute() - Model only provides connection/queries.
    """

    def __init__(self, model: LoginModel, view: LoginView):
        self.model = model
        self.view = view
        self.view.loginButton.clicked.connect(self.handle_login)

        self.popup = None
        self.current_user = None
        self.dashboard_controller = None
        self.transaction_controller = None

    def handle_login(self):
        username = self.view.usernameInput.text().strip()
        password = self.view.passwordInput.text().strip()

        # Check for empty fields
        if not username or not password:
            self.popup = LoginErrorPopup("empty", self.view)
            self.popup.show()
            self.popup.closeButton.clicked.connect(self.clear_fields)
            return

        # Validate user using controller-managed execution
        user = self.validateUser(username, password)

        if not user:
            self.popup = LoginErrorPopup("invalid", self.view)
            self.popup.show()
            self.popup.closeButton.clicked.connect(self.clear_fields)
            return

        # Check if account is active
        if not user.get('is_active'):
            self.popup = LoginErrorPopup("inactive", self.view)
            self.popup.show()
            self.popup.closeButton.clicked.connect(self.clear_fields)
            return

        # Successful login
        display_name = user.get('full_name', username).split()[0]  # First name
        self.popup = LoginSuccessPopup(display_name, user['role'], self.view)
        self.popup.show()
        self.popup.continueButton.clicked.connect(self.continue_after_login)

        # Store user info
        self.current_user = user

    def validateUser(self, username: str, password: str) -> dict:
        """
        Validates user credentials by executing query in controller.
        Model provides connection and query template.
        """
        connection = None
        try:
            connection = self.model.getConnection()
            cursor = connection.cursor(dictionary=True)

            query = self.model.getUserValidationQuery()
            cursor.execute(query, (username, password))

            user = cursor.fetchone()
            cursor.close()
            return user if user else None

        except Error as e:
            print(f"[LoginController] Database error during validation: {e}")
            return None
        finally:
            if connection and connection.is_connected():
                connection.close()

    def clear_fields(self):
        """Closes popup and clears login input fields"""
        if self.popup:
            self.popup.close()
        self.view.usernameInput.setText("")
        self.view.passwordInput.setText("")
        self.view.usernameInput.setFocus()

    def continue_after_login(self):
        """Closes login and opens appropriate dashboard based on role"""
        if self.popup:
            self.popup.close()
        self.view.close()

        role = self.current_user['role']

        if role == "cashier":
            self.open_cashier_transaction()
        elif role == "admin":
            self.open_admin_dashboard()

    # ======================================================
    # REDIRECTION METHODS: Directs to the GUI for each role
    # ======================================================

    def open_cashier_transaction(self):
        """Open Transaction window with current user data"""
        from Controller.Cashier.TransactionController import TransactionController
        self.transaction_controller = TransactionController(self.current_user)
        self.transaction_controller.open_transaction()

    def open_admin_dashboard(self):
        """Open Admin Dashboard with current user data"""
        from Controller.Admin.AdminDashboardController import AdminDashboardController
        self.dashboard_controller = AdminDashboardController(self.current_user)
        self.dashboard_controller.open_dashboard()