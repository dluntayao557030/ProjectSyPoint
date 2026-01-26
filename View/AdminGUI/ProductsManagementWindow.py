from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame,
    QTableWidget, QHeaderView, QLineEdit, QComboBox,
    QDialog, QDoubleSpinBox
)
from PyQt6.QtGui import QFont, QPixmap, QColor


class AdminProductsView(QWidget):
    """Admin Product Management Window with Filters"""

    def __init__(self, current_user: dict = None):
        super().__init__()
        self.current_user = current_user or {}
        self.showMaximized()
        self.setWindowTitle("SyPoint POS - Product Management")
        palette = self.palette()
        palette.setColor(self.backgroundRole(), QColor("#f5f0e8"))
        self.setPalette(palette)
        self.setAutoFillBackground(True)

        self.selected_product_id = None
        self.selected_product_data = None

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

        # Header with filters
        headerLayout = QVBoxLayout()

        # Title row
        titleRow = QHBoxLayout()
        titleLabel = QLabel("Product Management")
        titleLabel.setFont(QFont("Arial", 28, QFont.Weight.Bold))
        titleLabel.setStyleSheet("color: #1a1a1a;")
        titleRow.addWidget(titleLabel)
        titleRow.addStretch()
        headerLayout.addLayout(titleRow)

        # Subtitle
        subtitleLabel = QLabel("Manage products, categories, and inventory")
        subtitleLabel.setFont(QFont("Arial", 12))
        subtitleLabel.setStyleSheet("color: #666666;")
        headerLayout.addWidget(subtitleLabel)

        headerLayout.addSpacing(15)

        # Filter Row
        filterLayout = QHBoxLayout()

        # Search
        self.searchInput = QLineEdit()
        self.searchInput.setPlaceholderText("🔍 Search products...")
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
        filterLayout.addWidget(self.searchInput)

        # Category Filter
        categoryLabel = QLabel("Category:")
        categoryLabel.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        categoryLabel.setStyleSheet("color: #333333;")
        filterLayout.addWidget(categoryLabel)

        self.categoryFilter = QComboBox()
        self.categoryFilter.setFixedWidth(180)
        self.categoryFilter.setFixedHeight(40)
        self.categoryFilter.setStyleSheet("""
            QComboBox {
                background-color: white; border: 2px solid #d0d0d0;
                border-radius: 5px; padding-left: 10px; font-size: 12px;
                color: #333333;
            }
            QComboBox QAbstractItemView {
                background-color: white;
                color: #333333;
                selection-background-color: #f4d03f;
            }
        """)
        filterLayout.addWidget(self.categoryFilter)

        # Status Filter
        statusLabel = QLabel("Status:")
        statusLabel.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        statusLabel.setStyleSheet("color: #333333;")
        filterLayout.addWidget(statusLabel)

        self.statusFilter = QComboBox()
        self.statusFilter.addItems(["All", "Active", "Archived"])
        self.statusFilter.setFixedWidth(120)
        self.statusFilter.setFixedHeight(40)
        self.statusFilter.setStyleSheet("""
            QComboBox {
                background-color: white; border: 2px solid #d0d0d0;
                border-radius: 5px; padding-left: 10px; font-size: 12px;
                color: #333333;
            }
            QComboBox QAbstractItemView {
                background-color: white;
                color: #333333;
                selection-background-color: #f4d03f;
            }
        """)
        filterLayout.addWidget(self.statusFilter)

        # Apply Filter Button
        self.applyFilterButton = QPushButton("Apply Filters")
        self.applyFilterButton.setFixedHeight(40)
        self.applyFilterButton.setFixedWidth(130)
        self.applyFilterButton.setStyleSheet("""
            QPushButton {
                background-color: #1a4d2e; color: white; border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #234d35; }
        """)
        filterLayout.addWidget(self.applyFilterButton)

        filterLayout.addStretch()
        headerLayout.addLayout(filterLayout)

        contentLayout.addLayout(headerLayout)

        # Products Table - REMOVED "Product ID" column
        self.productsTable = QTableWidget()
        self.productsTable.setColumnCount(6)  # Changed from 7 to 6
        self.productsTable.setHorizontalHeaderLabels([
            "Reference", "Product Name", "Category", "Price", "Status", "Created"
        ])
        self.productsTable.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.productsTable.verticalHeader().setVisible(False)
        self.productsTable.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.productsTable.setStyleSheet("""
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
        contentLayout.addWidget(self.productsTable)

        # Action Buttons
        actionsLayout = QHBoxLayout()
        actionsLayout.addStretch()

        self.addCategoryButton = QPushButton("📁 Add Category")
        self.addCategoryButton.setFixedHeight(45)
        self.addCategoryButton.setFixedWidth(160)
        self.addCategoryButton.setStyleSheet("""
            QPushButton {
                background-color: #666666; color: white; border-radius: 8px;
                font-weight: bold; font-size: 12px;
            }
            QPushButton:hover { background-color: #777777; }
        """)
        actionsLayout.addWidget(self.addCategoryButton)

        self.addProductButton = QPushButton("➕ Add Product")
        self.addProductButton.setFixedHeight(45)
        self.addProductButton.setFixedWidth(160)
        self.addProductButton.setStyleSheet("""
            QPushButton {
                background-color: #1a4d2e; color: white; border-radius: 8px;
                font-weight: bold; font-size: 13px;
            }
            QPushButton:hover { background-color: #234d35; }
        """)
        actionsLayout.addWidget(self.addProductButton)

        self.editProductButton = QPushButton("✏️ Edit Product")
        self.editProductButton.setFixedHeight(45)
        self.editProductButton.setFixedWidth(160)
        self.editProductButton.setStyleSheet("""
            QPushButton {
                background-color: #f4d03f; color: #1a1a1a; border-radius: 8px;
                font-weight: bold; font-size: 13px;
            }
            QPushButton:hover { background-color: #f5e05d; }
        """)
        actionsLayout.addWidget(self.editProductButton)

        self.archiveProductButton = QPushButton("🗄️ Archive Product")
        self.archiveProductButton.setFixedHeight(45)
        self.archiveProductButton.setFixedWidth(170)
        self.archiveProductButton.setStyleSheet("""
            QPushButton {
                background-color: #d32f2f; color: white; border-radius: 8px;
                font-weight: bold; font-size: 12px;
            }
            QPushButton:hover { background-color: #c62828; }
        """)
        actionsLayout.addWidget(self.archiveProductButton)

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
        self.productsButton = self._create_sidebar_button("📦 Manage Products", active=True)
        self.reportsButton = self._create_sidebar_button("📊 Sales Report", active=False)
        self.usersButton = self._create_sidebar_button("👥 User Management", active=False)
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
        """Clear selected product"""
        self.selected_product_id = None
        self.selected_product_data = None


class AddCategoryDialog(QDialog):
    """Dialog for adding new category"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(450, 250)
        self.setWindowTitle("Add Category")
        self.setModal(True)
        self.setStyleSheet("background-color: #f5f0e8;")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)

        # Title
        title = QLabel("Add New Category")
        title.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        title.setStyleSheet("color: #1a1a1a;")
        layout.addWidget(title)

        # Category Name
        nameLabel = QLabel("Category Name:")
        nameLabel.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        nameLabel.setStyleSheet("color: #333333;")
        layout.addWidget(nameLabel)

        self.categoryNameInput = QLineEdit()
        self.categoryNameInput.setPlaceholderText("Enter category name")
        self.categoryNameInput.setFixedHeight(40)
        self.categoryNameInput.setStyleSheet("""
            QLineEdit {
                background-color: white; border: 2px solid #d0d0d0;
                border-radius: 5px; padding-left: 10px;
                color: #333333;
            }
            QLineEdit:focus { border: 2px solid #f4d03f; }
            QLineEdit::placeholder { color: #888888; }
        """)
        layout.addWidget(self.categoryNameInput)

        # Buttons
        buttonsLayout = QHBoxLayout()

        cancelButton = QPushButton("Cancel")
        cancelButton.setFixedHeight(40)
        cancelButton.setStyleSheet("""
            QPushButton {
                background-color: #666666; color: white; border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #777777; }
        """)
        cancelButton.clicked.connect(self.reject)
        buttonsLayout.addWidget(cancelButton)

        self.submitButton = QPushButton("Add Category")
        self.submitButton.setFixedHeight(40)
        self.submitButton.setStyleSheet("""
            QPushButton {
                background-color: #1a4d2e; color: white; border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #234d35; }
        """)
        buttonsLayout.addWidget(self.submitButton)

        layout.addLayout(buttonsLayout)

    def get_category_name(self):
        """Get category name"""
        return self.categoryNameInput.text().strip()


class AddProductDialog(QDialog):
    """Dialog for adding new product"""

    def __init__(self, categories: list, parent=None):
        super().__init__(parent)
        self.setFixedSize(550, 600)
        self.setWindowTitle("Add Product")
        self.setModal(True)
        self.setStyleSheet("background-color: #f5f0e8;")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)

        # Title
        title = QLabel("Add New Product")
        title.setFont(QFont("Arial", 20, QFont.Weight.Bold))
        title.setStyleSheet("color: #1a1a1a;")
        layout.addWidget(title)

        # Form
        formFrame = QFrame()
        formFrame.setStyleSheet("background-color: white; border-radius: 10px;")
        formLayout = QVBoxLayout(formFrame)
        formLayout.setContentsMargins(20, 20, 20, 20)
        formLayout.setSpacing(15)

        # Reference Number
        refLabel = QLabel("Reference Number:")
        refLabel.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        refLabel.setStyleSheet("color: #333333;")
        formLayout.addWidget(refLabel)

        self.referenceInput = QLineEdit()
        self.referenceInput.setPlaceholderText("e.g., PRO-001")
        self.referenceInput.setFixedHeight(40)
        self.referenceInput.setStyleSheet("""
            QLineEdit {
                background-color: #f5f0e8; border: 2px solid #d0d0d0;
                border-radius: 5px; padding-left: 10px;
                color: #333333;
            }
            QLineEdit:focus { border: 2px solid #f4d03f; }
            QLineEdit::placeholder { color: #888888; }
        """)
        formLayout.addWidget(self.referenceInput)

        # Product Name
        nameLabel = QLabel("Product Name:")
        nameLabel.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        nameLabel.setStyleSheet("color: #333333;")
        formLayout.addWidget(nameLabel)

        self.productNameInput = QLineEdit()
        self.productNameInput.setPlaceholderText("Enter product name")
        self.productNameInput.setFixedHeight(40)
        self.productNameInput.setStyleSheet("""
            QLineEdit {
                background-color: #f5f0e8; border: 2px solid #d0d0d0;
                border-radius: 5px; padding-left: 10px;
                color: #333333;
            }
            QLineEdit:focus { border: 2px solid #f4d03f; }
            QLineEdit::placeholder { color: #888888; }
        """)
        formLayout.addWidget(self.productNameInput)

        # Price
        priceLabel = QLabel("Price (PHP):")
        priceLabel.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        priceLabel.setStyleSheet("color: #333333;")
        formLayout.addWidget(priceLabel)

        self.priceInput = QDoubleSpinBox()
        self.priceInput.setRange(0.01, 999999.99)
        self.priceInput.setDecimals(2)
        self.priceInput.setPrefix("PHP ")
        self.priceInput.setFixedHeight(40)
        self.priceInput.setStyleSheet("""
            QDoubleSpinBox {
                background-color: #f5f0e8; border: 2px solid #d0d0d0;
                border-radius: 5px; padding-left: 10px;
                color: #333333;
            }
        """)
        formLayout.addWidget(self.priceInput)

        # Category
        categoryLabel = QLabel("Category:")
        categoryLabel.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        categoryLabel.setStyleSheet("color: #333333;")
        formLayout.addWidget(categoryLabel)

        self.categoryCombo = QComboBox()
        for cat in categories:
            self.categoryCombo.addItem(cat['category_name'], cat['category_id'])
        self.categoryCombo.setFixedHeight(40)
        self.categoryCombo.setStyleSheet("""
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
        formLayout.addWidget(self.categoryCombo)

        layout.addWidget(formFrame)

        # Buttons
        buttonsLayout = QHBoxLayout()

        cancelButton = QPushButton("Cancel")
        cancelButton.setFixedHeight(45)
        cancelButton.setStyleSheet("""
            QPushButton {
                background-color: #666666; color: white; border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #777777; }
        """)
        cancelButton.clicked.connect(self.reject)
        buttonsLayout.addWidget(cancelButton)

        self.submitButton = QPushButton("Add Product")
        self.submitButton.setFixedHeight(45)
        self.submitButton.setStyleSheet("""
            QPushButton {
                background-color: #1a4d2e; color: white; border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #234d35; }
        """)
        buttonsLayout.addWidget(self.submitButton)

        layout.addLayout(buttonsLayout)

    def get_product_data(self):
        """Get product data"""
        return {
            'reference_number': self.referenceInput.text().strip().upper(),
            'product_name': self.productNameInput.text().strip(),
            'price': self.priceInput.value(),
            'category_id': self.categoryCombo.currentData()
        }


class EditProductDialog(QDialog):
    """Dialog for editing existing product"""

    def __init__(self, categories: list, parent=None):
        super().__init__(parent)
        self.setFixedSize(550, 650)
        self.setWindowTitle("Edit Product")
        self.setModal(True)
        self.setStyleSheet("background-color: #f5f0e8;")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)

        # Title
        title = QLabel("Edit Product")
        title.setFont(QFont("Arial", 20, QFont.Weight.Bold))
        title.setStyleSheet("color: #1a1a1a;")
        layout.addWidget(title)

        # Form
        formFrame = QFrame()
        formFrame.setStyleSheet("background-color: white; border-radius: 10px;")
        formLayout = QVBoxLayout(formFrame)
        formLayout.setContentsMargins(20, 20, 20, 20)
        formLayout.setSpacing(15)

        # Reference Number
        refLabel = QLabel("Reference Number:")
        refLabel.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        refLabel.setStyleSheet("color: #333333;")
        formLayout.addWidget(refLabel)

        self.referenceInput = QLineEdit()
        self.referenceInput.setFixedHeight(40)
        self.referenceInput.setStyleSheet("""
            QLineEdit {
                background-color: #f5f0e8; border: 2px solid #d0d0d0;
                border-radius: 5px; padding-left: 10px;
                color: #333333;
            }
            QLineEdit:focus { border: 2px solid #f4d03f; }
        """)
        formLayout.addWidget(self.referenceInput)

        # Product Name
        nameLabel = QLabel("Product Name:")
        nameLabel.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        nameLabel.setStyleSheet("color: #333333;")
        formLayout.addWidget(nameLabel)

        self.productNameInput = QLineEdit()
        self.productNameInput.setFixedHeight(40)
        self.productNameInput.setStyleSheet("""
            QLineEdit {
                background-color: #f5f0e8; border: 2px solid #d0d0d0;
                border-radius: 5px; padding-left: 10px;
                color: #333333;
            }
            QLineEdit:focus { border: 2px solid #f4d03f; }
        """)
        formLayout.addWidget(self.productNameInput)

        # Price
        priceLabel = QLabel("Price (PHP):")
        priceLabel.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        priceLabel.setStyleSheet("color: #333333;")
        formLayout.addWidget(priceLabel)

        self.priceInput = QDoubleSpinBox()
        self.priceInput.setRange(0.01, 999999.99)
        self.priceInput.setDecimals(2)
        self.priceInput.setPrefix("PHP ")
        self.priceInput.setFixedHeight(40)
        self.priceInput.setStyleSheet("""
            QDoubleSpinBox {
                background-color: #f5f0e8; border: 2px solid #d0d0d0;
                border-radius: 5px; padding-left: 10px;
                color: #333333;
            }
        """)
        formLayout.addWidget(self.priceInput)

        # Category
        categoryLabel = QLabel("Category:")
        categoryLabel.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        categoryLabel.setStyleSheet("color: #333333;")
        formLayout.addWidget(categoryLabel)

        self.categoryCombo = QComboBox()
        for cat in categories:
            self.categoryCombo.addItem(cat['category_name'], cat['category_id'])
        self.categoryCombo.setFixedHeight(40)
        self.categoryCombo.setStyleSheet("""
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
        formLayout.addWidget(self.categoryCombo)

        layout.addWidget(formFrame)

        # Buttons
        buttonsLayout = QHBoxLayout()

        cancelButton = QPushButton("Cancel")
        cancelButton.setFixedHeight(45)
        cancelButton.setStyleSheet("""
            QPushButton {
                background-color: #666666; color: white; border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #777777; }
        """)
        cancelButton.clicked.connect(self.reject)
        buttonsLayout.addWidget(cancelButton)

        self.submitButton = QPushButton("Update Product")
        self.submitButton.setFixedHeight(45)
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
        """Fill form with product data"""
        self.referenceInput.setText(data.get('reference_number', ''))
        self.productNameInput.setText(data.get('product_name', ''))
        self.priceInput.setValue(float(data.get('price', 0)))

        # Set category
        category_id = data.get('category_id')
        index = self.categoryCombo.findData(category_id)
        if index >= 0:
            self.categoryCombo.setCurrentIndex(index)

    def get_product_data(self):
        """Get updated product data"""
        return {
            'reference_number': self.referenceInput.text().strip().upper(),
            'product_name': self.productNameInput.text().strip(),
            'price': self.priceInput.value(),
            'category_id': self.categoryCombo.currentData()
        }