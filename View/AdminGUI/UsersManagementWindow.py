from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame,
    QTableWidget, QHeaderView, QLineEdit, QComboBox,
    QDialog, QButtonGroup, QRadioButton
)
from PyQt6.QtGui import QFont, QPixmap, QColor


class AdminUsersView(QWidget):
    """Admin User Management Window"""

    def __init__(self, current_user: dict = None):
        super().__init__()
        self.current_user = current_user or {}
        self.showMaximized()
        self.setWindowTitle("SyPoint POS - User Management")
        palette = self.palette()
        palette.setColor(self.backgroundRole(), QColor("#f5f0e8"))
        self.setPalette(palette)
        self.setAutoFillBackground(True)

        self.selected_user_id = None
        self.selected_user_data = None

        mainLayout = QHBoxLayout(self)
        mainLayout.setContentsMargins(0, 0, 0, 0)
        mainLayout.setSpacing(0)

        # Sidebar
        sidebar = self._build_sidebar()

        # Content Area
        contentArea = QWidget()
        contentLayout = QVBoxLayout(contentArea)
        contentLayout.setContentsMargins(40, 40, 40, 40)
        contentLayout.setSpacing(25)

        # Header
        headerLayout = QHBoxLayout()

        titleLabel = QLabel("User Management")
        titleLabel.setFont(QFont("Arial", 28, QFont.Weight.Bold))
        titleLabel.setStyleSheet("color: #1a1a1a;")
        headerLayout.addWidget(titleLabel)

        headerLayout.addStretch()

        # Search
        self.searchInput = QLineEdit()
        self.searchInput.setPlaceholderText("🔍 Search users...")
        self.searchInput.setFixedWidth(250)
        self.searchInput.setFixedHeight(40)
        self.searchInput.setStyleSheet("""
            QLineEdit {
                background-color: white; border: 2px solid #d0d0d0;
                border-radius: 5px; padding-left: 15px; font-size: 13px;
                color: #333333;
            }
            QLineEdit:focus { border: 2px solid #f4d03f; }
            QLineEdit::placeholder { color: #888888; }
        """)
        headerLayout.addWidget(self.searchInput)

        self.searchButton = QPushButton("Search")
        self.searchButton.setFixedHeight(40)
        self.searchButton.setFixedWidth(100)
        self.searchButton.setStyleSheet("""
            QPushButton {
                background-color: #1a4d2e; color: white; border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #234d35; }
        """)
        headerLayout.addWidget(self.searchButton)

        contentLayout.addLayout(headerLayout)

        # Subtitle
        subtitleLabel = QLabel("Manage system users and permissions")
        subtitleLabel.setFont(QFont("Arial", 12))
        subtitleLabel.setStyleSheet("color: #666666;")
        contentLayout.addWidget(subtitleLabel)

        # Users Table - REMOVED "User ID" column
        self.usersTable = QTableWidget()
        self.usersTable.setColumnCount(5)  # Changed from 6 to 5
        self.usersTable.setHorizontalHeaderLabels([
            "Username", "Full Name", "Role", "Shift", "Status"
        ])
        self.usersTable.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.usersTable.verticalHeader().setVisible(False)
        self.usersTable.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.usersTable.setStyleSheet("""
            QTableWidget {
                background-color: white; border-radius: 10px; gridline-color: #e0e0e0;
                color: #333333;
                font-size: 12px;
            }
            QHeaderView::section {
                background-color: #0d3b2b; color: white; font-weight: bold; padding: 12px;
                font-size: 12px;
            }
            QTableWidget::item {
                padding: 8px;
                color: #333333;
            }
            QTableWidget::item:selected {
                background-color: #e8f5e8;
                color: #333333;
            }
        """)
        contentLayout.addWidget(self.usersTable)

        # Action Buttons
        actionsLayout = QHBoxLayout()
        actionsLayout.addStretch()

        self.addUserButton = QPushButton("➕ Add User")
        self.addUserButton.setFixedHeight(45)
        self.addUserButton.setFixedWidth(150)
        self.addUserButton.setStyleSheet("""
            QPushButton {
                background-color: #1a4d2e; color: white; border-radius: 8px;
                font-weight: bold; font-size: 13px;
            }
            QPushButton:hover { background-color: #234d35; }
        """)
        actionsLayout.addWidget(self.addUserButton)

        self.editUserButton = QPushButton("✏️ Edit User")
        self.editUserButton.setFixedHeight(45)
        self.editUserButton.setFixedWidth(150)
        self.editUserButton.setStyleSheet("""
            QPushButton {
                background-color: #f4d03f; color: #1a1a1a; border-radius: 8px;
                font-weight: bold; font-size: 13px;
            }
            QPushButton:hover { background-color: #f5e05d; }
        """)
        actionsLayout.addWidget(self.editUserButton)

        contentLayout.addLayout(actionsLayout)

        mainLayout.addWidget(sidebar)
        mainLayout.addWidget(contentArea)

    def _build_sidebar(self):
        """Build admin sidebar"""
        sidebar = QFrame()
        sidebar.setFixedWidth(170)
        sidebar.setStyleSheet("background-color: #0d3b2b;")
        sidebarLayout = QVBoxLayout(sidebar)
        sidebarLayout.setContentsMargins(15, 25, 15, 25)
        sidebarLayout.setSpacing(20)
        sidebarLayout.setAlignment(Qt.AlignmentFlag.AlignTop)

        # Logo
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

        userLabel = QLabel("ADMIN")
        userLabel.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        userLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        userLabel.setStyleSheet("color: white;")
        sidebarLayout.addWidget(userLabel)

        sidebarLayout.addSpacing(40)

        # Navigation
        self.dashboardButton = self._create_sidebar_button("🏠 Dashboard", active=False)
        self.productsButton = self._create_sidebar_button("📦 Manage Products", active=False)
        self.reportsButton = self._create_sidebar_button("📊 Sales Report", active=False)
        self.usersButton = self._create_sidebar_button("👥 User Management", active=True)
        self.logoutButton = self._create_sidebar_button("🚪 Logout", active=False)

        sidebarLayout.addWidget(self.dashboardButton)
        sidebarLayout.addWidget(self.productsButton)
        sidebarLayout.addWidget(self.reportsButton)
        sidebarLayout.addWidget(self.usersButton)
        sidebarLayout.addWidget(self.logoutButton)
        sidebarLayout.addStretch()

        return sidebar

    def _create_sidebar_button(self, text: str, active: bool = False):
        """Create sidebar button"""
        btn = QPushButton(text)
        btn.setFont(QFont("Arial", 10))
        btn.setFixedHeight(45)
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        if active:
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #f4d03f; color: #1a1a1a; font-weight: bold;
                    border-radius: 8px; text-align: left; padding-left: 15px;
                }
                QPushButton:hover { background-color: #f5e05d; }
            """)
        else:
            btn.setStyleSheet("""
                QPushButton {
                    background-color: transparent; color: white;
                    border-radius: 8px; text-align: left; padding-left: 15px;
                }
                QPushButton:hover { background-color: #1a5040; }
            """)
        return btn

    def clear_selection(self):
        """Clear selected user"""
        self.selected_user_id = None
        self.selected_user_data = None


class AddUserDialog(QDialog):
    """Dialog for adding new users"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(600, 650)
        self.setWindowTitle("Add New User")
        self.setModal(True)
        self.setStyleSheet("background-color: #f5f0e8;")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)

        # Title
        title = QLabel("Add New User")
        title.setFont(QFont("Arial", 20, QFont.Weight.Bold))
        title.setStyleSheet("color: #1a1a1a;")
        layout.addWidget(title)

        subtitle = QLabel("Create a new system user account")
        subtitle.setFont(QFont("Arial", 11))
        subtitle.setStyleSheet("color: #666666;")
        layout.addWidget(subtitle)

        # Form Frame
        formFrame = QFrame()
        formFrame.setStyleSheet("background-color: white; border-radius: 10px;")
        formLayout = QVBoxLayout(formFrame)
        formLayout.setContentsMargins(20, 20, 20, 20)
        formLayout.setSpacing(15)

        # Username
        usernameLabel = QLabel("Username:")
        usernameLabel.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        usernameLabel.setStyleSheet("color: #333333;")
        formLayout.addWidget(usernameLabel)

        self.usernameInput = QLineEdit()
        self.usernameInput.setPlaceholderText("Enter username")
        self.usernameInput.setFixedHeight(40)
        self.usernameInput.setStyleSheet("""
            QLineEdit {
                background-color: #f5f0e8; border: 2px solid #d0d0d0;
                border-radius: 5px; padding-left: 10px;
                color: #333333;
            }
            QLineEdit:focus { border: 2px solid #f4d03f; }
            QLineEdit::placeholder { color: #888888; }
        """)
        formLayout.addWidget(self.usernameInput)

        # Password
        passwordLabel = QLabel("Password:")
        passwordLabel.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        passwordLabel.setStyleSheet("color: #333333;")
        formLayout.addWidget(passwordLabel)

        self.passwordInput = QLineEdit()
        self.passwordInput.setPlaceholderText("Enter password")
        self.passwordInput.setEchoMode(QLineEdit.EchoMode.Password)
        self.passwordInput.setFixedHeight(40)
        self.passwordInput.setStyleSheet("""
            QLineEdit {
                background-color: #f5f0e8; border: 2px solid #d0d0d0;
                border-radius: 5px; padding-left: 10px;
                color: #333333;
            }
            QLineEdit:focus { border: 2px solid #f4d03f; }
            QLineEdit::placeholder { color: #888888; }
        """)
        formLayout.addWidget(self.passwordInput)

        # Full Name
        nameLabel = QLabel("Full Name:")
        nameLabel.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        nameLabel.setStyleSheet("color: #333333;")
        formLayout.addWidget(nameLabel)

        self.fullNameInput = QLineEdit()
        self.fullNameInput.setPlaceholderText("Enter full name")
        self.fullNameInput.setFixedHeight(40)
        self.fullNameInput.setStyleSheet("""
            QLineEdit {
                background-color: #f5f0e8; border: 2px solid #d0d0d0;
                border-radius: 5px; padding-left: 10px;
                color: #333333;
            }
            QLineEdit:focus { border: 2px solid #f4d03f; }
            QLineEdit::placeholder { color: #888888; }
        """)
        formLayout.addWidget(self.fullNameInput)

        # Role
        roleLabel = QLabel("Role:")
        roleLabel.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        roleLabel.setStyleSheet("color: #333333;")
        formLayout.addWidget(roleLabel)

        roleLayout = QHBoxLayout()
        self.roleGroup = QButtonGroup(self)

        self.adminRadio = QRadioButton("Admin")
        self.cashierRadio = QRadioButton("Cashier")

        radio_style = """
            QRadioButton {
                color: #333333; font-size: 12px; font-weight: bold;
            }
            QRadioButton::indicator {
                width: 16px; height: 16px; border: 3px solid #1a4d2e;
                border-radius: 10px; background: white;
            }
            QRadioButton::indicator:checked {
                background-color: #1a4d2e; border: 3px solid #f4d03f;
            }
        """
        self.adminRadio.setStyleSheet(radio_style)
        self.cashierRadio.setStyleSheet(radio_style)

        self.roleGroup.addButton(self.adminRadio, 1)
        self.roleGroup.addButton(self.cashierRadio, 2)

        roleLayout.addWidget(self.adminRadio)
        roleLayout.addWidget(self.cashierRadio)
        roleLayout.addStretch()
        formLayout.addLayout(roleLayout)

        # Shift (only for cashiers)
        shiftLabel = QLabel("Shift:")
        shiftLabel.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        shiftLabel.setStyleSheet("color: #333333;")
        formLayout.addWidget(shiftLabel)

        self.shiftCombo = QComboBox()
        self.shiftCombo.addItems(["morning", "afternoon", "evening", "night"])
        self.shiftCombo.setFixedHeight(40)
        self.shiftCombo.setStyleSheet("""
            QComboBox {
                background-color: #f5f0e8; border: 2px solid #d0d0d0;
                border-radius: 5px; padding-left: 10px;
                color: #333333;
            }
            QComboBox QAbstractItemView {
                background-color: white;
                color: #333333;
                selection-background-color: #f4d03f;
            }
        """)
        formLayout.addWidget(self.shiftCombo)

        layout.addWidget(formFrame)

        # Buttons
        buttonsLayout = QHBoxLayout()

        cancelButton = QPushButton("Cancel")
        cancelButton.setFixedHeight(45)
        cancelButton.setFixedWidth(120)
        cancelButton.setStyleSheet("""
            QPushButton {
                background-color: #666666; color: white; border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #777777; }
        """)
        cancelButton.clicked.connect(self.reject)
        buttonsLayout.addWidget(cancelButton)

        buttonsLayout.addStretch()

        self.submitButton = QPushButton("Add User")
        self.submitButton.setFixedHeight(45)
        self.submitButton.setFixedWidth(120)
        self.submitButton.setStyleSheet("""
            QPushButton {
                background-color: #1a4d2e; color: white; border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #234d35; }
        """)
        buttonsLayout.addWidget(self.submitButton)

        layout.addLayout(buttonsLayout)

    def get_user_data(self):
        """Get form data"""
        role = "admin" if self.adminRadio.isChecked() else "cashier"
        return {
            'username': self.usernameInput.text().strip(),
            'password': self.passwordInput.text().strip(),
            'full_name': self.fullNameInput.text().strip(),
            'role': role,
            'shift': self.shiftCombo.currentText()
        }

    def clear_form(self):
        """Reset form"""
        self.usernameInput.clear()
        self.passwordInput.clear()
        self.fullNameInput.clear()
        self.roleGroup.setExclusive(False)
        self.adminRadio.setChecked(False)
        self.cashierRadio.setChecked(False)
        self.roleGroup.setExclusive(True)
        self.shiftCombo.setCurrentIndex(0)


class EditUserDialog(QDialog):
    """Dialog for editing existing users"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(600, 700)
        self.setWindowTitle("Edit User")
        self.setModal(True)
        self.setStyleSheet("background-color: #f5f0e8;")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)

        # Title
        title = QLabel("Edit User")
        title.setFont(QFont("Arial", 20, QFont.Weight.Bold))
        title.setStyleSheet("color: #1a1a1a;")
        layout.addWidget(title)

        subtitle = QLabel("Modify user account details")
        subtitle.setFont(QFont("Arial", 11))
        subtitle.setStyleSheet("color: #666666;")
        layout.addWidget(subtitle)

        # Form Frame
        formFrame = QFrame()
        formFrame.setStyleSheet("background-color: white; border-radius: 10px;")
        formLayout = QVBoxLayout(formFrame)
        formLayout.setContentsMargins(20, 20, 20, 20)
        formLayout.setSpacing(15)

        # Username
        usernameLabel = QLabel("Username:")
        usernameLabel.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        usernameLabel.setStyleSheet("color: #333333;")
        formLayout.addWidget(usernameLabel)

        self.usernameInput = QLineEdit()
        self.usernameInput.setFixedHeight(40)
        self.usernameInput.setStyleSheet("""
            QLineEdit {
                background-color: #f5f0e8; border: 2px solid #d0d0d0;
                border-radius: 5px; padding-left: 10px;
                color: #333333;
            }
            QLineEdit:focus { border: 2px solid #f4d03f; }
        """)
        formLayout.addWidget(self.usernameInput)

        # Password
        passwordLabel = QLabel("Password (leave blank to keep current):")
        passwordLabel.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        passwordLabel.setStyleSheet("color: #333333;")
        formLayout.addWidget(passwordLabel)

        self.passwordInput = QLineEdit()
        self.passwordInput.setPlaceholderText("New password (optional)")
        self.passwordInput.setEchoMode(QLineEdit.EchoMode.Password)
        self.passwordInput.setFixedHeight(40)
        self.passwordInput.setStyleSheet("""
            QLineEdit {
                background-color: #f5f0e8; border: 2px solid #d0d0d0;
                border-radius: 5px; padding-left: 10px;
                color: #333333;
            }
            QLineEdit:focus { border: 2px solid #f4d03f; }
            QLineEdit::placeholder { color: #888888; }
        """)
        formLayout.addWidget(self.passwordInput)

        # Full Name
        nameLabel = QLabel("Full Name:")
        nameLabel.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        nameLabel.setStyleSheet("color: #333333;")
        formLayout.addWidget(nameLabel)

        self.fullNameInput = QLineEdit()
        self.fullNameInput.setFixedHeight(40)
        self.fullNameInput.setStyleSheet("""
            QLineEdit {
                background-color: #f5f0e8; border: 2px solid #d0d0d0;
                border-radius: 5px; padding-left: 10px;
                color: #333333;
            }
            QLineEdit:focus { border: 2px solid #f4d03f; }
        """)
        formLayout.addWidget(self.fullNameInput)

        # Role
        roleLabel = QLabel("Role:")
        roleLabel.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        roleLabel.setStyleSheet("color: #333333;")
        formLayout.addWidget(roleLabel)

        roleLayout = QHBoxLayout()
        self.roleGroup = QButtonGroup(self)

        self.adminRadio = QRadioButton("Admin")
        self.cashierRadio = QRadioButton("Cashier")

        radio_style = """
            QRadioButton {
                color: #333333; font-size: 12px; font-weight: bold;
            }
            QRadioButton::indicator {
                width: 16px; height: 16px; border: 3px solid #1a4d2e;
                border-radius: 10px; background: white;
            }
            QRadioButton::indicator:checked {
                background-color: #1a4d2e; border: 3px solid #f4d03f;
            }
        """
        self.adminRadio.setStyleSheet(radio_style)
        self.cashierRadio.setStyleSheet(radio_style)

        self.roleGroup.addButton(self.adminRadio, 1)
        self.roleGroup.addButton(self.cashierRadio, 2)

        roleLayout.addWidget(self.adminRadio)
        roleLayout.addWidget(self.cashierRadio)
        roleLayout.addStretch()
        formLayout.addLayout(roleLayout)

        # Shift
        shiftLabel = QLabel("Shift:")
        shiftLabel.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        shiftLabel.setStyleSheet("color: #333333;")
        formLayout.addWidget(shiftLabel)

        self.shiftCombo = QComboBox()
        self.shiftCombo.addItems(["morning", "afternoon", "evening", "night"])
        self.shiftCombo.setFixedHeight(40)
        self.shiftCombo.setStyleSheet("""
            QComboBox {
                background-color: #f5f0e8; border: 2px solid #d0d0d0;
                border-radius: 5px; padding-left: 10px;
                color: #333333;
            }
            QComboBox QAbstractItemView {
                background-color: white;
                color: #333333;
                selection-background-color: #f4d03f;
            }
        """)
        formLayout.addWidget(self.shiftCombo)

        # Status
        statusLabel = QLabel("Status:")
        statusLabel.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        statusLabel.setStyleSheet("color: #333333;")
        formLayout.addWidget(statusLabel)

        statusLayout = QHBoxLayout()
        self.statusGroup = QButtonGroup(self)

        self.activeRadio = QRadioButton("Active")
        self.inactiveRadio = QRadioButton("Inactive")

        self.activeRadio.setStyleSheet(radio_style)
        self.inactiveRadio.setStyleSheet(radio_style)

        self.statusGroup.addButton(self.activeRadio, 1)
        self.statusGroup.addButton(self.inactiveRadio, 2)

        statusLayout.addWidget(self.activeRadio)
        statusLayout.addWidget(self.inactiveRadio)
        statusLayout.addStretch()
        formLayout.addLayout(statusLayout)

        layout.addWidget(formFrame)

        # Buttons
        buttonsLayout = QHBoxLayout()

        cancelButton = QPushButton("Cancel")
        cancelButton.setFixedHeight(45)
        cancelButton.setFixedWidth(120)
        cancelButton.setStyleSheet("""
            QPushButton {
                background-color: #666666; color: white; border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #777777; }
        """)
        cancelButton.clicked.connect(self.reject)
        buttonsLayout.addWidget(cancelButton)

        buttonsLayout.addStretch()

        self.submitButton = QPushButton("Update User")
        self.submitButton.setFixedHeight(45)
        self.submitButton.setFixedWidth(130)
        self.submitButton.setStyleSheet("""
            QPushButton {
                background-color: #1a4d2e; color: white; border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #234d35; }
        """)
        buttonsLayout.addWidget(self.submitButton)

        layout.addLayout(buttonsLayout)

    def populate_form(self, data: dict):
        """Fill form with user data"""
        self.usernameInput.setText(data.get('username', ''))
        self.fullNameInput.setText(data.get('full_name', ''))

        # Role
        if data.get('role') == 'admin':
            self.adminRadio.setChecked(True)
        else:
            self.cashierRadio.setChecked(True)

        # Shift
        shift = data.get('shift', 'morning')
        index = self.shiftCombo.findText(shift)
        if index >= 0:
            self.shiftCombo.setCurrentIndex(index)

        # Status
        if data.get('is_active', 1) == 1:
            self.activeRadio.setChecked(True)
        else:
            self.inactiveRadio.setChecked(True)

    def get_user_data(self):
        """Get updated form data"""
        role = "admin" if self.adminRadio.isChecked() else "cashier"
        is_active = 1 if self.activeRadio.isChecked() else 0
        password = self.passwordInput.text().strip() or None

        return {
            'username': self.usernameInput.text().strip(),
            'password': password,
            'full_name': self.fullNameInput.text().strip(),
            'role': role,
            'shift': self.shiftCombo.currentText(),
            'is_active': is_active
        }