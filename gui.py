import sys
from PySide6.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QHBoxLayout, 
    QPushButton, QFrame
)
from PySide6.QtCore import Qt, QTimer, Slot
from PySide6.QtGui import QFont

class AssistantOverlay(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        # Frameless, Stays On Top, Tool Window (Doesn't create extra taskbar icons)
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool |
            Qt.WindowType.WindowDoesNotAcceptFocus  # Prevents stealing focus on show
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating, True) # Ensures underlying window stays active
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)

        self.default_width = 560
        self.default_height = 140
        self.resize(self.default_width, self.default_height)

        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(8, 8, 8, 8)

        # Main Card Frame
        self.card = QFrame(self)
        self.card.setObjectName("MainCard")
        self.card.setStyleSheet("""
            #MainCard {
                background-color: #0E1117;
                border: 2px solid #00E5FF;
                border-radius: 18px;
            }
        """)

        card_layout = QVBoxLayout(self.card)
        card_layout.setContentsMargins(22, 16, 22, 16)
        card_layout.setSpacing(8)

        # Top Header Bar
        header_layout = QHBoxLayout()
        header_layout.setSpacing(12)

        self.badge = QLabel("● LISTENING")
        self.badge.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
        self.badge.setStyleSheet("""
            background-color: rgba(0, 229, 255, 0.15);
            color: #00E5FF;
            padding: 4px 10px;
            border-radius: 8px;
            border: 1px solid rgba(0, 229, 255, 0.3);
        """)

        self.close_btn = QPushButton("✕")
        self.close_btn.setFixedSize(28, 28)
        self.close_btn.setFocusPolicy(Qt.FocusPolicy.NoFocus)  # Keep focus off close button
        self.close_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.close_btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(255, 255, 255, 0.08);
                color: #A0AEC0;
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 14px;
                font-size: 13px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #FF3B30;
                color: #FFFFFF;
                border: 1px solid #FF3B30;
            }
        """)
        self.close_btn.clicked.connect(self.dismiss)

        header_layout.addWidget(self.badge)
        header_layout.addStretch()
        header_layout.addWidget(self.close_btn)

        # Main Title
        self.title_label = QLabel("Sky Voice Assistant")
        self.title_label.setFont(QFont("Segoe UI", 15, QFont.Weight.Bold))
        self.title_label.setStyleSheet("color: #FFFFFF; border: none; background: transparent;")

        # Subtitle / Summary Content
        self.sub_label = QLabel("Say your command clearly...")
        self.sub_label.setFont(QFont("Segoe UI", 11))
        self.sub_label.setStyleSheet("color: #CBD5E1; border: none; background: transparent; line-height: 140%;")
        self.sub_label.setWordWrap(True)
        self.sub_label.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)

        card_layout.addLayout(header_layout)
        card_layout.addWidget(self.title_label)
        card_layout.addWidget(self.sub_label, 1)

        root_layout.addWidget(self.card)

        self.hide_timer = QTimer(self)
        self.hide_timer.setSingleShot(True)
        self.hide_timer.timeout.connect(self.hide)

        self.center_on_screen()

    def center_on_screen(self):
        screen = self.screen().geometry()
        x = (screen.width() - self.width()) // 2
        y = screen.height() - self.height() - 100
        self.move(x, y)

    @Slot(str, str)
    def update_status(self, title: str, subtitle: str = ""):
        self.hide_timer.stop()
        self.title_label.setText(title)
        self.sub_label.setText(subtitle)

        # Expand window height dynamically for longer answer summaries
        if len(subtitle) > 80 or "says:" in title.lower():
            self.resize(620, 240)
            self.badge.setText("💡 ANSWER")
            self.badge.setStyleSheet("""
                background-color: rgba(168, 85, 247, 0.15);
                color: #C084FC;
                padding: 4px 10px;
                border-radius: 8px;
                border: 1px solid rgba(168, 85, 247, 0.4);
            """)
        elif "listening" in title.lower():
            self.resize(self.default_width, self.default_height)
            self.badge.setText("● LISTENING")
            self.badge.setStyleSheet("""
                background-color: rgba(0, 229, 255, 0.15);
                color: #00E5FF;
                padding: 4px 10px;
                border-radius: 8px;
                border: 1px solid rgba(0, 229, 255, 0.4);
            """)
        elif "executing" in title.lower() or "processing" in title.lower():
            self.resize(self.default_width, self.default_height)
            self.badge.setText("⚡ PROCESSING")
            self.badge.setStyleSheet("""
                background-color: rgba(52, 199, 89, 0.15);
                color: #34C759;
                padding: 4px 10px;
                border-radius: 8px;
                border: 1px solid rgba(52, 199, 89, 0.4);
            """)
        elif "cancel" in title.lower():
            self.resize(self.default_width, self.default_height)
            self.badge.setText("✕ STOPPED")
            self.badge.setStyleSheet("""
                background-color: rgba(255, 59, 48, 0.15);
                color: #FF3B30;
                padding: 4px 10px;
                border-radius: 8px;
                border: 1px solid rgba(255, 59, 48, 0.4);
            """)

        self.center_on_screen()
        
        # Display the overlay over all windows WITHOUT snatching focus
        self.show()

    @Slot(int)
    def schedule_hide(self, delay_ms: int = 2400):
        self.hide_timer.start(delay_ms)

    def dismiss(self):
        self.hide_timer.stop()
        self.hide()