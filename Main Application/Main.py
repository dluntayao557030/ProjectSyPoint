"""
Main Application Entry Point for SyPoint POS System
"""

import sys
from PyQt6.QtWidgets import QApplication
from View.LoginGUI.Login import LoginView
from Model.Authentication.LoginModel import LoginModel
from Controller.Login.LoginController import LoginController

def main():
    """Main application entry point"""
    app = QApplication(sys.argv)

    # Initialize Model, View, and Controller
    model = LoginModel()
    view = LoginView()
    controller = LoginController(model, view)

    # Show login window
    view.showMaximized()

    sys.exit(app.exec())

if __name__ == "__main__":
    main()