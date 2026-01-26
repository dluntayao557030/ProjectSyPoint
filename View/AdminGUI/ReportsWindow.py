from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame,
    QComboBox, QDateEdit, QTableWidget, QTableWidgetItem, QHeaderView,
    QDialog, QTextEdit, QCalendarWidget
)
from PyQt6.QtGui import QFont, QPixmap, QColor
from PyQt6.QtCore import QDate


class AdminReportsView(QWidget):
    """Admin Reports Window with Report Generation"""

    def __init__(self, current_user: dict = None):
        super().__init__()
        self.current_user = current_user or {}
        self.showMaximized()
        self.setWindowTitle("SyPoint POS - Sales Reports")
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
        contentLayout = QHBoxLayout(contentArea)
        contentLayout.setContentsMargins(30, 30, 30, 30)
        contentLayout.setSpacing(20)

        # Left Panel - Report Generator
        leftPanel = self._build_left_panel()

        # Right Panel - Report Preview
        rightPanel = self._build_right_panel()

        contentLayout.addWidget(leftPanel, 1)
        contentLayout.addWidget(rightPanel, 2)

        mainLayout.addWidget(sidebar)
        mainLayout.addWidget(contentArea)

        self.current_report_type = None
        self.current_report_data = []

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
        self.reportsButton = self._create_sidebar_button("📊 Sales Report", active=True)
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

    def _build_left_panel(self):
        """Build report generator panel"""
        panel = QFrame()
        panel.setFixedWidth(400)
        panel.setStyleSheet("background-color: white; border-radius: 15px;")
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(25, 25, 25, 25)
        layout.setSpacing(20)

        # Title
        title = QLabel("Report Generator")
        title.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        title.setStyleSheet("color: #1a1a1a;")
        layout.addWidget(title)

        subtitle = QLabel("Generate sales and performance reports")
        subtitle.setFont(QFont("Arial", 10))
        subtitle.setStyleSheet("color: #666666;")
        layout.addWidget(subtitle)

        layout.addSpacing(10)

        # Report Type
        typeLabel = QLabel("Report Type")
        typeLabel.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        typeLabel.setStyleSheet("color: #333333;")
        layout.addWidget(typeLabel)

        self.reportTypeCombo = QComboBox()
        self.reportTypeCombo.addItems([
            "-- Select Report Type --",
            "Daily Sales Report",
            "Shift Summary Report",
            "Cashier Performance Report",
            "Product Sales Report",
            "Discount Usage Report"
        ])
        self.reportTypeCombo.setFixedHeight(40)
        self.reportTypeCombo.setStyleSheet("""
            QComboBox {
                background-color: #f5f0e8; border: 2px solid #d0d0d0;
                border-radius: 5px; padding-left: 10px; font-size: 12px;
                color: #333333;
            }
            QComboBox QAbstractItemView {
                background-color: white;
                color: #333333;
                selection-background-color: #f4d03f;
            }
        """)
        layout.addWidget(self.reportTypeCombo)

        layout.addSpacing(15)

        # Date Filter
        dateLabel = QLabel("Date Range")
        dateLabel.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        dateLabel.setStyleSheet("color: #333333;")
        layout.addWidget(dateLabel)

        # From Date
        fromLabel = QLabel("From:")
        fromLabel.setFont(QFont("Arial", 10))
        fromLabel.setStyleSheet("color: #666666;")
        layout.addWidget(fromLabel)

        self.fromDateEdit = QDateEdit()
        self.fromDateEdit.setDate(QDate.currentDate().addDays(-7))
        self.fromDateEdit.setCalendarPopup(True)
        self.fromDateEdit.setFixedHeight(40)
        self.fromDateEdit.setStyleSheet("""
            QDateEdit {
                background-color: #f5f0e8; border: 2px solid #d0d0d0;
                border-radius: 5px; padding-left: 10px; font-size: 12px;
                color: #333333;
            }
            QDateEdit::down-arrow {
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid #333333;
                margin-right: 8px;
            }
        """)

        # Style the calendar popup
        calendar = QCalendarWidget()
        calendar.setStyleSheet("""
            QCalendarWidget {
                background-color: white;
                color: #333333;
            }
            QCalendarWidget QWidget {
                alternate-background-color: white;
            }
            QCalendarWidget QToolButton {
                background-color: #f5f0e8;
                color: #333333;
                font-weight: bold;
                border-radius: 4px;
                padding: 5px;
            }
            QCalendarWidget QMenu {
                background-color: white;
                color: #333333;
            }
            QCalendarWidget QSpinBox {
                background-color: #f5f0e8;
                color: #333333;
                border: 1px solid #d0d0d0;
                border-radius: 3px;
                padding: 3px;
            }
            QCalendarWidget QAbstractItemView:enabled {
                color: #333333;
                background-color: white;
                selection-background-color: #1a4d2e;
                selection-color: white;
            }
            QCalendarWidget QAbstractItemView:disabled {
                color: #999999;
            }
        """)
        self.fromDateEdit.setCalendarWidget(calendar)

        layout.addWidget(self.fromDateEdit)

        # To Date
        toLabel = QLabel("To:")
        toLabel.setFont(QFont("Arial", 10))
        toLabel.setStyleSheet("color: #666666;")
        layout.addWidget(toLabel)

        self.toDateEdit = QDateEdit()
        self.toDateEdit.setDate(QDate.currentDate())
        self.toDateEdit.setCalendarPopup(True)
        self.toDateEdit.setFixedHeight(40)
        self.toDateEdit.setStyleSheet("""
            QDateEdit {
                background-color: #f5f0e8; border: 2px solid #d0d0d0;
                border-radius: 5px; padding-left: 10px; font-size: 12px;
                color: #333333;
            }
            QDateEdit::down-arrow {
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid #333333;
                margin-right: 8px;
            }
        """)

        # Style the calendar popup for To Date
        calendar_to = QCalendarWidget()
        calendar_to.setStyleSheet("""
            QCalendarWidget {
                background-color: white;
                color: #333333;
            }
            QCalendarWidget QWidget {
                alternate-background-color: white;
            }
            QCalendarWidget QToolButton {
                background-color: #f5f0e8;
                color: #333333;
                font-weight: bold;
                border-radius: 4px;
                padding: 5px;
            }
            QCalendarWidget QMenu {
                background-color: white;
                color: #333333;
            }
            QCalendarWidget QSpinBox {
                background-color: #f5f0e8;
                color: #333333;
                border: 1px solid #d0d0d0;
                border-radius: 3px;
                padding: 3px;
            }
            QCalendarWidget QAbstractItemView:enabled {
                color: #333333;
                background-color: white;
                selection-background-color: #1a4d2e;
                selection-color: white;
            }
            QCalendarWidget QAbstractItemView:disabled {
                color: #999999;
            }
        """)
        self.toDateEdit.setCalendarWidget(calendar_to)

        layout.addWidget(self.toDateEdit)

        layout.addSpacing(20)

        # Generate Button
        self.generateButton = QPushButton("Generate Report")
        self.generateButton.setFixedHeight(45)
        self.generateButton.setStyleSheet("""
            QPushButton {
                background-color: #1a4d2e; color: white; border-radius: 8px;
                font-weight: bold; font-size: 13px;
            }
            QPushButton:hover { background-color: #234d35; }
        """)
        layout.addWidget(self.generateButton)

        layout.addStretch()
        return panel

    def _build_right_panel(self):
        """Build report preview panel"""
        panel = QFrame()
        panel.setStyleSheet("background-color: white; border-radius: 15px;")
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(25, 25, 25, 25)
        layout.setSpacing(15)

        # Header
        headerLayout = QHBoxLayout()

        title = QLabel("Report Preview")
        title.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        title.setStyleSheet("color: #1a1a1a;")
        headerLayout.addWidget(title)

        headerLayout.addStretch()

        # Action buttons
        self.viewSummaryButton = QPushButton("📋 View Summary")
        self.viewSummaryButton.setFixedHeight(40)
        self.viewSummaryButton.setEnabled(False)
        self.viewSummaryButton.setStyleSheet("""
            QPushButton {
                background-color: #1a4d2e; color: white; border-radius: 5px;
                font-weight: bold; padding: 0 15px;
            }
            QPushButton:hover { background-color: #234d35; }
            QPushButton:disabled { background-color: #cccccc; color: #666666; }
        """)
        headerLayout.addWidget(self.viewSummaryButton)

        self.printButton = QPushButton("🖨️ Print Report")
        self.printButton.setFixedHeight(40)
        self.printButton.setEnabled(False)
        self.printButton.setStyleSheet("""
            QPushButton {
                background-color: #f4d03f; color: #1a1a1a; border-radius: 5px;
                font-weight: bold; padding: 0 15px;
            }
            QPushButton:hover { background-color: #f5e05d; }
            QPushButton:disabled { background-color: #cccccc; color: #666666; }
        """)
        headerLayout.addWidget(self.printButton)

        layout.addLayout(headerLayout)

        # Table
        self.reportTable = QTableWidget()
        self.reportTable.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.reportTable.verticalHeader().setVisible(False)
        self.reportTable.setStyleSheet("""
            QTableWidget {
                background-color: #f9f9f9; border-radius: 10px; gridline-color: #e0e0e0;
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

        # Initial empty state
        self.show_empty_state()

        layout.addWidget(self.reportTable)

        return panel

    def show_empty_state(self):
        """Show empty state message"""
        self.reportTable.setColumnCount(1)
        self.reportTable.setHorizontalHeaderLabels([""])
        self.reportTable.horizontalHeader().setVisible(False)
        self.reportTable.setRowCount(1)
        item = QTableWidgetItem("Select a report type and click Generate to view data")
        item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        item.setFont(QFont("Arial", 12))
        item.setForeground(QColor("#666666"))
        self.reportTable.setItem(0, 0, item)

    def populate_report_table(self, columns: list, data: list):
        """Populate report table"""
        if not data:
            self.reportTable.setColumnCount(1)
            self.reportTable.setHorizontalHeaderLabels([""])
            self.reportTable.horizontalHeader().setVisible(False)
            self.reportTable.setRowCount(1)
            item = QTableWidgetItem("No data found for the selected criteria")
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            item.setForeground(QColor("#666666"))
            item.setFont(QFont("Arial", 12))
            self.reportTable.setItem(0, 0, item)
            return

        self.reportTable.horizontalHeader().setVisible(True)
        self.reportTable.setColumnCount(len(columns))
        self.reportTable.setHorizontalHeaderLabels(columns)
        self.reportTable.setRowCount(len(data))

        for r, row in enumerate(data):
            for c, val in enumerate(row):
                item = QTableWidgetItem(str(val))
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

                # Color coding for monetary values
                if isinstance(val, str) and val.startswith("PHP"):
                    if "PHP 0.00" in val:
                        item.setForeground(QColor("#999999"))
                    else:
                        item.setForeground(QColor("#1a4d2e"))
                        item.setFont(QFont("Arial", 11, QFont.Weight.Bold))

                # Color coding for percentages
                elif isinstance(val, str) and "%" in val:
                    percentage = float(val.replace("%", "").strip())
                    if percentage > 0:
                        item.setForeground(QColor("#1a4d2e"))
                    else:
                        item.setForeground(QColor("#999999"))

                self.reportTable.setItem(r, c, item)


class ReportSummaryDialog(QDialog):
    """Dialog to show report summary statistics"""

    def __init__(self, report_type: str, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"{report_type} - Summary")
        self.setFixedSize(600, 500)
        self.setModal(True)
        self.setStyleSheet("background-color: #f5f0e8;")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)

        # Title
        title = QLabel(f"{report_type}")
        title.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        title.setStyleSheet("color: #1a1a1a;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        # Date range
        self.dateRangeLabel = QLabel()
        self.dateRangeLabel.setFont(QFont("Arial", 11))
        self.dateRangeLabel.setStyleSheet("color: #666666;")
        self.dateRangeLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.dateRangeLabel)

        # Summary frame
        summaryFrame = QFrame()
        summaryFrame.setStyleSheet("background-color: white; border-radius: 10px;")
        summaryLayout = QVBoxLayout(summaryFrame)
        summaryLayout.setContentsMargins(20, 20, 20, 20)
        summaryLayout.setSpacing(15)

        summaryTitle = QLabel("Summary Statistics")
        summaryTitle.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        summaryTitle.setStyleSheet("color: #1a1a1a;")
        summaryLayout.addWidget(summaryTitle)

        self.summaryText = QTextEdit()
        self.summaryText.setReadOnly(True)
        self.summaryText.setFont(QFont("Courier New", 10))
        self.summaryText.setStyleSheet("""
            QTextEdit {
                background-color: #f9f9f9; border: 1px solid #d0d0d0;
                border-radius: 5px; padding: 10px;
                color: #333333;
            }
        """)
        summaryLayout.addWidget(self.summaryText)

        layout.addWidget(summaryFrame)

        # Close button
        closeBtn = QPushButton("Close")
        closeBtn.setFixedHeight(40)
        closeBtn.setStyleSheet("""
            QPushButton {
                background-color: #1a4d2e; color: white; border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #234d35; }
        """)
        closeBtn.clicked.connect(self.close)
        layout.addWidget(closeBtn)

    def set_summary_data(self, date_range: str, summary_text: str):
        """Set summary data"""
        self.dateRangeLabel.setText(f"Date Range: {date_range}")
        self.summaryText.setPlainText(summary_text)