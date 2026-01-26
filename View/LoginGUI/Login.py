from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                              QLineEdit, QPushButton, QFrame)
from PyQt6.QtGui import QPixmap, QFont

class LoginView(QWidget):
    """
    Creates Login Window for POS System (SyPoint) with password visibility toggle.
    """
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SyPoint POS - Login")
        self.setStyleSheet("background-color: #f5f0e8;")

        # Main layout (horizontal split: logo left, login form right)
        mainLayout = QHBoxLayout(self)
        mainLayout.setContentsMargins(0, 0, 0, 0)

        # Left side - Logo
        leftWidget = QWidget()
        leftWidget.setStyleSheet("background-color: #f5f0e8;")
        leftLayout = QVBoxLayout(leftWidget)
        leftLayout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.logoLabel = QLabel()
        pixmap = QPixmap("../ImageResources/SyPointLogo.png")
        if not pixmap.isNull():
            scaled_pixmap = pixmap.scaled(400, 400, Qt.AspectRatioMode.KeepAspectRatio,
                                         Qt.TransformationMode.SmoothTransformation)
            self.logoLabel.setPixmap(scaled_pixmap)
        else:
            self.logoLabel.setText("SyPoint")
            self.logoLabel.setFont(QFont("Arial", 48, QFont.Weight.Bold))
            self.logoLabel.setStyleSheet("color: #1a4d2e;")
        leftLayout.addWidget(self.logoLabel)

        # Right side - Login Form
        rightWidget = QWidget()
        rightWidget.setStyleSheet("background-color: #f5f0e8;")
        rightLayout = QVBoxLayout(rightWidget)
        rightLayout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Login Card Container
        cardWidget = QWidget()
        cardWidget.setFixedSize(500, 420)
        cardLayout = QVBoxLayout(cardWidget)
        cardLayout.setContentsMargins(40, 40, 40, 40)
        cardLayout.setSpacing(20)

        # Login Title
        titleLabel = QLabel("LOG IN")
        titleLabel.setFont(QFont("Arial", 32, QFont.Weight.Bold))
        titleLabel.setStyleSheet("color: #1a4d2e;")
        titleLabel.setAlignment(Qt.AlignmentFlag.AlignLeft)
        cardLayout.addWidget(titleLabel)
        cardLayout.addSpacing(20)

        # Username Field
        self.usernameInput = QLineEdit()
        self.usernameInput.setPlaceholderText("Username")
        self.usernameInput.setFont(QFont("Arial", 12))
        self.usernameInput.setFixedHeight(45)
        self.usernameInput.setStyleSheet("""
            QLineEdit {
                background-color: #f4d03f;
                border: none;
                border-radius: 5px;
                padding-left: 15px;
                color: #1a1a1a;
            }
            QLineEdit::placeholder {
                color: #666666;
            }
        """)
        cardLayout.addWidget(self.usernameInput)

        # Password Field with Toggle Button
        passwordContainer = QWidget()
        passwordLayout = QHBoxLayout(passwordContainer)
        passwordLayout.setContentsMargins(0, 0, 0, 0)
        passwordLayout.setSpacing(8)

        self.passwordInput = QLineEdit()
        self.passwordInput.setPlaceholderText("Password")
        self.passwordInput.setFont(QFont("Arial", 12))
        self.passwordInput.setFixedHeight(45)
        self.passwordInput.setEchoMode(QLineEdit.EchoMode.Password)
        self.passwordInput.setStyleSheet("""
            QLineEdit {
                background-color: #f4d03f;
                border: none;
                border-radius: 5px;
                padding-left: 15px;
                padding-right: 15px;
                color: #1a1a1a;
            }
            QLineEdit::placeholder {
                color: #666666;
            }
        """)
        passwordLayout.addWidget(self.passwordInput)

        # Quick See Button
        self.togglePasswordButton = QPushButton("👁")
        self.togglePasswordButton.setFont(QFont("Arial", 14))
        self.togglePasswordButton.setFixedSize(45, 45)
        self.togglePasswordButton.setCursor(Qt.CursorShape.PointingHandCursor)
        self.togglePasswordButton.setCheckable(True)
        self.togglePasswordButton.setStyleSheet("""
            QPushButton {
                background-color: #1a4d2e;
                color: white;
                border: none;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #234d35;
            }
            QPushButton:pressed, QPushButton:checked {
                background-color: #0f3a20;
            }
        """)
        self.togglePasswordButton.clicked.connect(self.togglePasswordVisibility)
        passwordLayout.addWidget(self.togglePasswordButton)

        cardLayout.addWidget(passwordContainer)
        cardLayout.addSpacing(20)

        # Login Button
        self.loginButton = QPushButton("Log in")
        self.loginButton.setFont(QFont("Arial", 13, QFont.Weight.Bold))
        self.loginButton.setFixedHeight(45)
        self.loginButton.setCursor(Qt.CursorShape.PointingHandCursor)
        self.loginButton.setStyleSheet("""
            QPushButton {
                background-color: #1a4d2e;
                color: white;
                border: none;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #234d35;
            }
            QPushButton:pressed {
                background-color: #0f3a20;
            }
        """)
        cardLayout.addWidget(self.loginButton)

        rightLayout.addWidget(cardWidget)

        # Add both sides to main layout (50-50 split)
        mainLayout.addWidget(leftWidget, 1)
        mainLayout.addWidget(rightWidget, 1)

    def togglePasswordVisibility(self):
        """Toggle password visibility between hidden and visible"""
        if self.togglePasswordButton.isChecked():
            self.passwordInput.setEchoMode(QLineEdit.EchoMode.Normal)
            self.togglePasswordButton.setText("🙈")  # Hide icon
        else:
            self.passwordInput.setEchoMode(QLineEdit.EchoMode.Password)
            self.togglePasswordButton.setText("👁")  # Show icon


class LoginErrorPopup(QWidget):
    """
    Popup for unsuccessful login.
    """
    def __init__(self, errorType="empty", parent=None):
        super().__init__()
        self.parent_window = parent
        self.setFixedSize(400, 250)
        self.setWindowTitle("Login Failed")
        self.setWindowModality(Qt.WindowModality.ApplicationModal)

        # Center on parent window
        if parent:
            parent_geo = parent.geometry()
            x = parent_geo.x() + (parent_geo.width() - self.width()) // 2
            y = parent_geo.y() + (parent_geo.height() - self.height()) // 2
            self.move(x, y)

        # Background
        self.setStyleSheet("background-color: #f5f0e8;")

        # Main frame
        mainFrame = QFrame(self)
        mainFrame.setGeometry(10, 10, 380, 230)
        mainFrame.setStyleSheet("""
            QFrame {
                background-color: #fff8e1;
                border-radius: 15px;
            }
        """)

        # Error messages
        if errorType == "empty":
            mainMessage = "Missing Credentials"
            subMessage = "Please enter both username and password."
        else:  # invalid credentials
            mainMessage = "Login Failed"
            subMessage = "Invalid username or password."

        # Error Message
        messageLabel = QLabel(mainMessage, mainFrame)
        messageLabel.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        messageLabel.setStyleSheet("color: #d32f2f;")
        messageLabel.setGeometry(40, 80, 310, 30)
        messageLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Subtext
        subtextLabel = QLabel(subMessage, mainFrame)
        subtextLabel.setFont(QFont("Arial", 11))
        subtextLabel.setStyleSheet("color: #666666;")
        subtextLabel.setGeometry(40, 120, 310, 25)
        subtextLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Close Button
        self.closeButton = QPushButton("Close", mainFrame)
        self.closeButton.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        self.closeButton.setGeometry(140, 170, 100, 40)
        self.closeButton.setCursor(Qt.CursorShape.PointingHandCursor)
        self.closeButton.setStyleSheet("""
            QPushButton {
                background-color: #1a4d2e;
                color: white;
                border: none;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #234d35;
            }
        """)


class LoginSuccessPopup(QWidget):
    """
    Popup for successful login.
    """
    def __init__(self, user_name, role, parent=None):
        super().__init__()
        self.parent_window = parent
        self.user_name = user_name
        self.role = role
        self.setFixedSize(400, 250)
        self.setWindowTitle("Login Successful")
        self.setWindowModality(Qt.WindowModality.ApplicationModal)

        # Center on parent window
        if parent:
            parent_geo = parent.geometry()
            x = parent_geo.x() + (parent_geo.width() - self.width()) // 2
            y = parent_geo.y() + (parent_geo.height() - self.height()) // 2
            self.move(x, y)

        # Background
        self.setStyleSheet("background-color: #f5f0e8;")

        # Main frame
        mainFrame = QFrame(self)
        mainFrame.setGeometry(10, 10, 380, 230)
        mainFrame.setStyleSheet("""
            QFrame {
                background-color: #e8f5e9;
                border-radius: 15px;
            }
        """)

        # Success Message
        messageLabel = QLabel(f"Welcome {user_name}!", mainFrame)
        messageLabel.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        messageLabel.setStyleSheet("color: #2e7d32;")
        messageLabel.setGeometry(40, 80, 310, 30)
        messageLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Subtext
        subtextLabel = QLabel(f"You are logged in as {role.upper()}.", mainFrame)
        subtextLabel.setFont(QFont("Arial", 11))
        subtextLabel.setStyleSheet("color: #666666;")
        subtextLabel.setGeometry(40, 120, 310, 25)
        subtextLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Continue Button
        self.continueButton = QPushButton("Continue", mainFrame)
        self.continueButton.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        self.continueButton.setGeometry(140, 170, 100, 40)
        self.continueButton.setCursor(Qt.CursorShape.PointingHandCursor)
        self.continueButton.setStyleSheet("""
            QPushButton {
                background-color: #1a4d2e;
                color: white;
                border: none;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #234d35;
            }
        """)