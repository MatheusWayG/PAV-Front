from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor, QPainter, QLinearGradient
from PyQt6.QtWidgets import (
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
    QGraphicsDropShadowEffect
)

class CreditosWindow(QWidget):
    switch_to_login = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.initUI()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Gradiente em tons de verde claro elegante (Glassmorphism)
        gradient = QLinearGradient(0, 0, self.width(), self.height())
        gradient.setColorAt(0.0, QColor(52, 211, 153))  # Verde claro vibrante
        gradient.setColorAt(1.0, QColor(4, 120, 87))    # Verde esmeralda suave
        
        painter.fillRect(self.rect(), gradient)

    def initUI(self):
        main_layout = QVBoxLayout(self)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        card = QWidget(self)
        card.setFixedSize(460, 520)
        card.setObjectName("GlassCard")

        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(40)
        shadow.setColor(QColor(0, 0, 0, 60))
        shadow.setOffset(0, 12)
        card.setGraphicsEffect(shadow)

        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(40, 35, 40, 35)
        card_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        title_label = QLabel("Créditos")
        title_label.setObjectName("TitleLabel")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        subtitle_label = QLabel("Desenvolvido por:")
        subtitle_label.setObjectName("SubtitleLabel")
        subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Nomes dos desenvolvedores destacados
        dev1_label = QLabel("Matheus Wayand Grotz")
        dev1_label.setObjectName("DevLabel")
        dev1_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        dev2_label = QLabel("Elton Kasesky")
        dev2_label.setObjectName("DevLabel")
        dev2_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.btn_voltar = QPushButton("Voltar ao Login")
        self.btn_voltar.setObjectName("LoginButton")
        self.btn_voltar.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_voltar.clicked.connect(self.switch_to_login.emit)

        card_layout.addWidget(title_label)
        card_layout.addWidget(subtitle_label)
        card_layout.addSpacing(25)
        card_layout.addWidget(dev1_label)
        card_layout.addSpacing(10)
        card_layout.addWidget(dev2_label)
        card_layout.addSpacing(35)
        card_layout.addWidget(self.btn_voltar)

        main_layout.addWidget(card)