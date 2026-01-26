import sys
from PyQt6.QtWidgets import QApplication

from Controller.Cashier.TransactionController import TransactionController

def main():
    """Main application entry point"""
    app = QApplication(sys.argv)

    view = TransactionController()
    view.open_transaction()

    sys.exit(app.exec())

if __name__ == "__main__":
    main()