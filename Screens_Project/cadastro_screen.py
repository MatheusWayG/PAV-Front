from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor, QPainter, QLinearGradient
from PyQt6.QtWidgets import (
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
    QGraphicsDropShadowEffect
)

class CadastroWindow(QWidget):
    switch_to_login = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.initUI()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        gradient = QLinearGradient(0, 0, self.width(), self.height())
        gradient.setColorAt(0.0, QColor(59, 130, 246))
        gradient.setColorAt(1.0, QColor(79, 70, 229))
        painter.fillRect(self.rect(), gradient)

    def initUI(self):
        main_layout = QVBoxLayout(self)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        card = QWidget(self)
        card.setFixedSize(460, 620)  # Cartão levemente maior para acomodar a idade
        card.setObjectName("GlassCard")

        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(40)
        shadow.setColor(QColor(0, 0, 0, 60))
        shadow.setOffset(0, 12)
        card.setGraphicsEffect(shadow)

        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(40, 30, 40, 30)
        card_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        title_label = QLabel("Criar Conta")
        title_label.setObjectName("TitleLabel")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        subtitle_label = QLabel("Preencha os dados para se cadastrar")
        subtitle_label.setObjectName("SubtitleLabel")
        subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Campo E-mail
        email_label = QLabel("Insira seu E-mail")
        email_label.setObjectName("FieldLabel")
        self.email_input = QLineEdit()
        self.email_input.setObjectName("InputField")
        self.email_input.setPlaceholderText("seu@email.com")

        # Campo Idade
        idade_label = QLabel("Insira sua Idade")
        idade_label.setObjectName("FieldLabel")
        self.idade_input = QLineEdit()
        self.idade_input.setObjectName("InputField")
        self.idade_input.setPlaceholderText("Ex: 25")

        # Campo Senha
        senha_label = QLabel("Insira sua Senha")
        senha_label.setObjectName("FieldLabel")
        self.senha_input = QLineEdit()
        self.senha_input.setObjectName("InputField")
        self.senha_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.senha_input.setPlaceholderText("••••••••")

        self.btn_cadastrar = QPushButton("Cadastrar")
        self.btn_cadastrar.setObjectName("LoginButton")
        self.btn_cadastrar.setCursor(Qt.CursorShape.PointingHandCursor)

        self.btn_voltar = QPushButton("Voltar ao Login")
        self.btn_voltar.setObjectName("LinkButton")
        self.btn_voltar.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_voltar.clicked.connect(self.switch_to_login.emit)

        card_layout.addWidget(title_label)
        card_layout.addWidget(subtitle_label)
        card_layout.addSpacing(8)
        card_layout.addWidget(email_label)
        card_layout.addWidget(self.email_input)
        card_layout.addSpacing(6)
        card_layout.addWidget(idade_label)
        card_layout.addWidget(self.idade_input)
        card_layout.addSpacing(6)
        card_layout.addWidget(senha_label)
        card_layout.addWidget(self.senha_input)
        card_layout.addSpacing(14)
        card_layout.addWidget(self.btn_cadastrar)
        card_layout.addSpacing(10)
        card_layout.addWidget(self.btn_voltar, alignment=Qt.AlignmentFlag.AlignCenter)

        main_layout.addWidget(card)