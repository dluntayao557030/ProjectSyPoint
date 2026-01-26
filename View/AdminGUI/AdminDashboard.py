from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame,
    QGridLayout, QComboBox, QTableWidget, QTableWidgetItem, QHeaderView,
    QDialog, QScrollArea
)
from PyQt6.QtGui import QFont, QPixmap, QCursor
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure


class AdminDashboardView(QWidget):
    """Admin Dashboard with KPIs and Charts - Recent Transactions Removed"""

    def __init__(self, current_user: dict = None):
        super().__init__()
        self.current_user = current_user or {}
        self.showMaximized()
        self.setWindowTitle("SyPoint POS - Admin Dashboard")

        # Main layout
        mainLayout = QHBoxLayout(self)
        mainLayout.setContentsMargins(0, 0, 0, 0)
        mainLayout.setSpacing(0)

        # Sidebar
        sidebar = self._build_sidebar()

        # Content Area with Scroll - Fixed background color
        scrollArea = QScrollArea()
        scrollArea.setWidgetResizable(True)
        scrollArea.setStyleSheet("QScrollArea { border: none; }")

        contentWidget = QWidget()
        contentWidget.setStyleSheet("background-color: #f5f0e8;")  # Fixed: Set background on content widget
        contentLayout = QVBoxLayout(contentWidget)
        contentLayout.setContentsMargins(40, 40, 40, 40)
        contentLayout.setSpacing(30)

        # Header
        headerLayout = QHBoxLayout()
        titleLabel = QLabel("Dashboard")
        titleLabel.setFont(QFont("Arial", 28, QFont.Weight.Bold))
        titleLabel.setStyleSheet("color: #1a1a1a;")
        headerLayout.addWidget(titleLabel)
        headerLayout.addStretch()

        # Date filter for charts
        filterLabel = QLabel("Sales Chart:")
        filterLabel.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        filterLabel.setStyleSheet("color: #666666;")
        headerLayout.addWidget(filterLabel)

        self.chartFilterCombo = QComboBox()
        self.chartFilterCombo.addItems([
            "Last 7 Days",
            "Last 30 Days",
            "This Month",
            "Last Month"
        ])
        self.chartFilterCombo.setFixedHeight(35)
        self.chartFilterCombo.setFixedWidth(150)

        self.chartFilterCombo.setStyleSheet("""
            QComboBox {
                background-color: white;
                border: 2px solid #d0d0d0;
                border-radius: 5px;
                padding-left: 10px;
                font-size: 12px;
                color: black;
            }

            QComboBox QAbstractItemView {
                background-color: white;
                color: black;
                selection-background-color: #e6e6e6;
                selection-color: black;
            }
        """)

        headerLayout.addWidget(self.chartFilterCombo)

        contentLayout.addLayout(headerLayout)

        # KPI Cards Grid (Clickable)
        kpiGrid = QGridLayout()
        kpiGrid.setSpacing(20)

        self.totalSalesCard = self._create_kpi_card("Total Sales Today", "PHP 0.00", "💰")
        self.transactionsCard = self._create_kpi_card("Transactions Today", "0", "🧾")
        self.productsCard = self._create_kpi_card("Products Sold Today", "0", "📦")
        self.avgSaleCard = self._create_kpi_card("Average Sale", "PHP 0.00", "📊")

        kpiGrid.addWidget(self.totalSalesCard, 0, 0)
        kpiGrid.addWidget(self.transactionsCard, 0, 1)
        kpiGrid.addWidget(self.productsCard, 1, 0)
        kpiGrid.addWidget(self.avgSaleCard, 1, 1)

        contentLayout.addLayout(kpiGrid)

        # Sales Chart
        chartFrame = QFrame()
        chartFrame.setStyleSheet("background-color: white; border-radius: 15px;")
        chartLayout = QVBoxLayout(chartFrame)
        chartLayout.setContentsMargins(20, 20, 20, 20)

        chartTitle = QLabel("Sales Trend")
        chartTitle.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        chartTitle.setStyleSheet("color: #1a1a1a;")
        chartLayout.addWidget(chartTitle)

        # Matplotlib canvas
        self.figure = Figure(figsize=(10, 4))
        self.canvas = FigureCanvas(self.figure)
        self.canvas.setStyleSheet("background-color: white;")
        chartLayout.addWidget(self.canvas)

        contentLayout.addWidget(chartFrame)
        contentLayout.addStretch()

        scrollArea.setWidget(contentWidget)

        mainLayout.addWidget(sidebar)
        mainLayout.addWidget(scrollArea)

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

        full_name = self.current_user.get('full_name', 'ADMIN').upper()
        userLabel = QLabel(full_name)
        userLabel.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        userLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        userLabel.setStyleSheet("color: white;")
        sidebarLayout.addWidget(userLabel)

        sidebarLayout.addSpacing(40)

        # Navigation
        self.dashboardButton = self._create_sidebar_button("🏠 Dashboard", active=True)
        self.productsButton = self._create_sidebar_button("📦 Manage Products", active=False)
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
        btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
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

    def _create_kpi_card(self, title: str, value: str, icon: str):
        """Create clickable KPI card"""
        card = QFrame()
        card.setFixedHeight(140)
        card.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        card.setStyleSheet("""
            QFrame {
                background-color: white; border-radius: 15px;
            }
            QFrame:hover {
                background-color: #f9f9f9;
            }
        """)
        layout = QVBoxLayout(card)
        layout.setContentsMargins(20, 15, 20, 15)
        layout.setSpacing(5)

        # Icon and title
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

        # Hint
        hintLabel = QLabel("Click to view details")
        hintLabel.setObjectName("hintLabel")
        hintLabel.setFont(QFont("Arial", 9))
        hintLabel.setStyleSheet("color: #999999;")
        layout.addWidget(hintLabel)

        layout.addStretch()
        return card

    def update_kpi(self, card_name: str, value: str):
        """Update KPI card value"""
        card = getattr(self, f"{card_name}Card", None)
        if card:
            lbl = card.findChild(QLabel, "valueLabel")
            if lbl:
                lbl.setText(value)

    def plot_sales_chart(self, dates: list, sales: list, title: str = "Sales Trend"):
        """Plot sales line chart"""
        self.figure.clear()
        ax = self.figure.add_subplot(111)

        ax.plot(dates, sales, marker='o', linewidth=2, color='#1a4d2e', markersize=6)
        ax.fill_between(dates, sales, alpha=0.2, color='#1a4d2e')

        ax.set_title(title, fontsize=14, fontweight='bold', pad=15)
        ax.set_xlabel('Date', fontsize=11)
        ax.set_ylabel('Sales (PHP)', fontsize=11)
        ax.grid(True, alpha=0.3, linestyle='--')
        ax.tick_params(axis='x', rotation=45)

        self.figure.tight_layout()
        self.canvas.draw()


class KPIDetailDialog(QDialog):
    """Dialog to show detailed data when KPI is clicked - NO IDs SHOWN"""

    def __init__(self, title: str, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"{title} - Details")
        self.setFixedSize(800, 600)
        self.setModal(True)
        self.setStyleSheet("background-color: #f5f0e8;")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)

        # Title
        titleLabel = QLabel(title)
        titleLabel.setFont(QFont("Arial", 20, QFont.Weight.Bold))
        titleLabel.setStyleSheet("color: #1a1a1a;")
        layout.addWidget(titleLabel)

        # Table
        self.detailTable = QTableWidget()
        self.detailTable.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.detailTable.verticalHeader().setVisible(False)
        self.detailTable.setStyleSheet("""
            QTableWidget {
                background-color: white; border-radius: 10px; gridline-color: #e0e0e0;
            }
            QHeaderView::section {
                background-color: #0d3b2b; color: white; font-weight: bold; padding: 10px;
            }
        """)
        layout.addWidget(self.detailTable)

        # Close button
        closeBtn = QPushButton("Close")
        closeBtn.setFixedHeight(40)
        closeBtn.setFixedWidth(120)
        closeBtn.setStyleSheet("""
            QPushButton {
                background-color: #1a4d2e; color: white; border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #234d35; }
        """)
        closeBtn.clicked.connect(self.close)
        layout.addWidget(closeBtn, alignment=Qt.AlignmentFlag.AlignRight)

    def populate_table(self, columns: list, data: list):
        """Populate detail table"""
        self.detailTable.setColumnCount(len(columns))
        self.detailTable.setHorizontalHeaderLabels(columns)
        self.detailTable.setRowCount(len(data))

        for r, row in enumerate(data):
            for c, val in enumerate(row):
                item = QTableWidgetItem(str(val))
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.detailTable.setItem(r, c, item)