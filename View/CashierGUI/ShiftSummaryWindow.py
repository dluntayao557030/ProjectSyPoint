from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame,
    QTableWidget, QTableWidgetItem, QHeaderView, QGridLayout
)
from PyQt6.QtGui import QFont, QPixmap, QColor


class ShiftSummaryView(QWidget):
    """Shift Summary Window for Cashiers"""

    def __init__(self, current_user: dict = None):
        super().__init__()
        self.current_user = current_user or {}
        self.showMaximized()
        self.setWindowTitle("SyPoint POS - Shift Summary")
        palette = self.palette()
        palette.setColor(self.backgroundRole(), QColor("#f5f0e8"))
        self.setPalette(palette)
        self.setAutoFillBackground(True)

        mainLayout = QHBoxLayout(self)
        mainLayout.setContentsMargins(0, 0, 0, 0)
        mainLayout.setSpacing(0)

        # Sidebar
        sidebar = self._build_sidebar()

        # Content Area
        contentArea = QWidget()
        contentLayout = QVBoxLayout(contentArea)
        contentLayout.setContentsMargins(40, 40, 40, 40)
        contentLayout.setSpacing(30)

        # Header
        headerLayout = QHBoxLayout()
        titleLabel = QLabel("Shift Summary")
        titleLabel.setFont(QFont("Arial", 28, QFont.Weight.Bold))
        titleLabel.setStyleSheet("color: #1a1a1a;")
        headerLayout.addWidget(titleLabel)

        headerLayout.addStretch()

        # Print button
        self.printButton = QPushButton("🖨️ Print Summary")
        self.printButton.setFixedHeight(45)
        self.printButton.setStyleSheet("""
            QPushButton {
                background-color: #1a4d2e; color: white; border-radius: 8px;
                font-weight: bold; font-size: 13px; padding: 0 20px;
            }
            QPushButton:hover { background-color: #234d35; }
        """)
        headerLayout.addWidget(self.printButton)

        contentLayout.addLayout(headerLayout)

        # KPI Cards
        kpiLayout = QGridLayout()
        kpiLayout.setSpacing(20)

        self.salesCard = self._create_kpi_card("Total Sales", "PHP 0.00", "💰")
        self.itemsCard = self._create_kpi_card("Items Sold", "0", "📦")
        self.transactionsCard = self._create_kpi_card("Transactions", "0", "🧾")
        self.avgCard = self._create_kpi_card("Avg per Sale", "PHP 0.00", "📊")

        kpiLayout.addWidget(self.salesCard, 0, 0)
        kpiLayout.addWidget(self.itemsCard, 0, 1)
        kpiLayout.addWidget(self.transactionsCard, 1, 0)
        kpiLayout.addWidget(self.avgCard, 1, 1)

        contentLayout.addLayout(kpiLayout)

        # Additional Info Cards Row
        infoLayout = QHBoxLayout()
        infoLayout.setSpacing(20)

        # Payment Methods Breakdown
        self.paymentFrame = self._create_info_card("Payment Methods Breakdown")
        infoLayout.addWidget(self.paymentFrame)

        # Top Products
        self.topProductsFrame = self._create_info_card("Top 5 Products Sold")
        infoLayout.addWidget(self.topProductsFrame)

        contentLayout.addLayout(infoLayout)

        # Transactions Table
        tableLabel = QLabel("Shift Transactions")
        tableLabel.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        tableLabel.setStyleSheet("color: #1a1a1a;")
        contentLayout.addWidget(tableLabel)

        self.transactionsTable = QTableWidget()
        self.transactionsTable.setColumnCount(6)
        self.transactionsTable.setHorizontalHeaderLabels([
            "Transaction ID", "Time", "Items", "Total", "Payment", "Discount"
        ])
        self.transactionsTable.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.transactionsTable.verticalHeader().setVisible(False)
        self.transactionsTable.setStyleSheet("""
            QTableWidget {
                background-color: white; border-radius: 10px; gridline-color: #e0e0e0;
            }
            QHeaderView::section {
                background-color: #0d3b2b; color: white; font-weight: bold; padding: 12px;
            }
        """)
        contentLayout.addWidget(self.transactionsTable)

        mainLayout.addWidget(sidebar)
        mainLayout.addWidget(contentArea)

    def _build_sidebar(self):
        """Build unified sidebar"""
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

        full_name = f"{self.current_user.get('full_name', 'CASHIER')}".strip().upper()
        userLabel = QLabel(full_name)
        userLabel.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        userLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        userLabel.setStyleSheet("color: white;")
        userLabel.setWordWrap(True)
        sidebarLayout.addWidget(userLabel)

        sidebarLayout.addSpacing(40)

        # Navigation
        self.transactionButton = self._create_sidebar_button("💳 Transaction", active=False)
        self.shiftSummaryButton = self._create_sidebar_button("📊 Shift", active=True)
        self.logoutButton = self._create_sidebar_button("🚪 Logout", active=False)

        sidebarLayout.addWidget(self.transactionButton)
        sidebarLayout.addWidget(self.shiftSummaryButton)
        sidebarLayout.addWidget(self.logoutButton)
        sidebarLayout.addStretch()

        return sidebar

    def _create_sidebar_button(self, text: str, active: bool = False):
        """Create sidebar button"""
        btn = QPushButton(text)
        btn.setFont(QFont("Arial", 11))
        btn.setFixedHeight(45)
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        if active:
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #f4d03f; color: #1a1a1a; font-weight: bold;
                    border-radius: 8px; text-align: left; padding-left: 20px;
                }
                QPushButton:hover { background-color: #f5e05d; }
            """)
        else:
            btn.setStyleSheet("""
                QPushButton {
                    background-color: transparent; color: white;
                    border-radius: 8px; text-align: left; padding-left: 20px;
                }
                QPushButton:hover { background-color: #1a5040; }
            """)
        return btn

    def _create_kpi_card(self, title: str, value: str, icon: str):
        """Create KPI card"""
        card = QFrame()
        card.setFixedHeight(140)
        card.setStyleSheet("background-color: white; border-radius: 15px;")
        layout = QVBoxLayout(card)
        layout.setContentsMargins(20, 15, 20, 15)
        layout.setSpacing(5)

        # Icon and title row
        topRow = QHBoxLayout()
        iconLabel = QLabel(icon)
        iconLabel.setFont(QFont("Arial", 24))
        topRow.addWidget(iconLabel)

        titleLabel = QLabel(title)
        titleLabel.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        titleLabel.setStyleSheet("color: #666666;")
        topRow.addWidget(titleLabel)
        topRow.addStretch()

        layout.addLayout(topRow)

        # Value
        valueLabel = QLabel(value)
        valueLabel.setObjectName("valueLabel")
        valueLabel.setFont(QFont("Arial", 26, QFont.Weight.Bold))
        valueLabel.setStyleSheet("color: #1a4d2e;")
        layout.addWidget(valueLabel)

        layout.addStretch()
        return card

    def _create_info_card(self, title: str):
        """Create info card for additional details"""
        card = QFrame()
        card.setStyleSheet("background-color: white; border-radius: 15px;")
        layout = QVBoxLayout(card)
        layout.setContentsMargins(20, 15, 20, 15)
        layout.setSpacing(10)

        titleLabel = QLabel(title)
        titleLabel.setFont(QFont("Arial", 13, QFont.Weight.Bold))
        titleLabel.setStyleSheet("color: #1a1a1a;")
        layout.addWidget(titleLabel)

        # Content label (will be updated by controller)
        contentLabel = QLabel("Loading...")
        contentLabel.setObjectName("contentLabel")
        contentLabel.setFont(QFont("Arial", 11))
        contentLabel.setStyleSheet("color: #333333;")
        contentLabel.setWordWrap(True)
        layout.addWidget(contentLabel)

        layout.addStretch()
        return card

    # Public update methods
    def update_kpi(self, card_name: str, value: str):
        """Update KPI card value"""
        card = getattr(self, f"{card_name}Card", None)
        if card:
            lbl = card.findChild(QLabel, "valueLabel")
            if lbl:
                lbl.setText(value)

    @staticmethod
    def update_info_card(frame, content: str):
        """Update info card content"""
        lbl = frame.findChild(QLabel, "contentLabel")
        if lbl:
            lbl.setText(content)

    def update_transactions_table(self, data: list):
        """Update transactions table"""
        if not data:
            self.transactionsTable.setRowCount(1)
            item = QTableWidgetItem("No transactions in this shift")
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.transactionsTable.setItem(0, 0, item)
            self.transactionsTable.setSpan(0, 0, 1, 6)
            return

        self.transactionsTable.clearSpans()
        self.transactionsTable.setRowCount(len(data))
        for r, row in enumerate(data):
            for c, val in enumerate(row):
                item = QTableWidgetItem(str(val))
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.transactionsTable.setItem(r, c, item)