from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor, QPainter, QLinearGradient
from PyQt6.QtWidgets import (
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QWidget,
    QGraphicsDropShadowEffect
)

class GlassLoginWindow(QWidget):
    switch_to_signin = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.initUI()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        gradient = QLinearGradient(0, 0, self.width(), self.height())
        gradient.setColorAt(0.0, QColor(79, 70, 229))  # Índigo vibrante
        gradient.setColorAt(1.0, QColor(59, 130, 246)) # Azul brilhante
        painter.fillRect(self.rect(), gradient)

    def initUI(self):
        main_layout = QVBoxLayout(self)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        card = QWidget(self)
        card.setFixedSize(460, 580)
        card.setObjectName("GlassCard")
        
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(40)
        shadow.setColor(QColor(0, 0, 0, 60))
        shadow.setOffset(0, 12)
        card.setGraphicsEffect(shadow)

        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(40, 35, 40, 35)
        card_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        title_label = QLabel("Bem Vindo")
        title_label.setObjectName("TitleLabel")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        subtitle_label = QLabel("Pronto para dar seus primeiros passos?")
        subtitle_label.setObjectName("SubtitleLabel")
        subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Campo E-mail
        email_label = QLabel("Insira seu E-mail")
        email_label.setObjectName("FieldLabel")
        self.email_input = QLineEdit()
        self.email_input.setObjectName("InputField")
        self.email_input.setPlaceholderText("seu@email.com")

        # Campo Senha
        senha_label = QLabel("Insira sua Senha")
        senha_label.setObjectName("FieldLabel")
        self.senha_input = QLineEdit()
        self.senha_input.setObjectName("InputField")
        self.senha_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.senha_input.setPlaceholderText("••••••••")

        self.btn_entrar = QPushButton("Entrar")
        self.btn_entrar.setObjectName("LoginButton")
        self.btn_entrar.setCursor(Qt.CursorShape.PointingHandCursor)

        footer_layout = QHBoxLayout()
        footer_label = QLabel("Não está cadastrado ainda?")
        footer_label.setObjectName("FooterLabel")
        
        self.btn_signin = QPushButton("Sign in")
        self.btn_signin.setObjectName("LinkButton")
        self.btn_signin.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_signin.clicked.connect(self.switch_to_signin.emit)

        footer_layout.addWidget(footer_label)
        footer_layout.addWidget(self.btn_signin)
        footer_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        footer_layout.setSpacing(5)

        card_layout.addWidget(title_label)
        card_layout.addWidget(subtitle_label)
        card_layout.addSpacing(10)
        card_layout.addWidget(email_label)
        card_layout.addWidget(self.email_input)
        card_layout.addSpacing(8)
        card_layout.addWidget(senha_label)
        card_layout.addWidget(self.senha_input)
        card_layout.addSpacing(18)
        card_layout.addWidget(self.btn_entrar)
        card_layout.addSpacing(12)
        card_layout.addLayout(footer_layout)

        main_layout.addWidget(card)