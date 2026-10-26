from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor, QPainter, QLinearGradient
from PyQt6.QtWidgets import (
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
    QGraphicsDropShadowEffect,
    QMessageBox
)
import requests

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
        card.setFixedSize(460, 620)
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

        email_label = QLabel("Insira seu E-mail")
        email_label.setObjectName("FieldLabel")
        self.email_input = QLineEdit()
        self.email_input.setObjectName("InputField")
        self.email_input.setPlaceholderText("seu@email.com")

        idade_label = QLabel("Insira sua Idade")
        idade_label.setObjectName("FieldLabel")
        self.idade_input = QLineEdit()
        self.idade_input.setObjectName("InputField")
        self.idade_input.setPlaceholderText("Ex: 25")

        senha_label = QLabel("Insira sua Senha")
        senha_label.setObjectName("FieldLabel")
        self.senha_input = QLineEdit()
        self.senha_input.setObjectName("InputField")
        self.senha_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.senha_input.setPlaceholderText("••••••••")

        self.btn_cadastrar = QPushButton("Cadastrar")
        self.btn_cadastrar.setObjectName("LoginButton")
        self.btn_cadastrar.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_cadastrar.clicked.connect(self.realizar_cadastro)

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

    def realizar_cadastro(self):
        email = self.email_input.text().strip()
        idade = self.idade_input.text().strip()
        senha = self.senha_input.text().strip()

        if not email or not idade or not senha:
            QMessageBox.warning(self, "Aviso", "Por favor, preencha todos os campos!")
            return

        try:
            # Comunicação com a rota de clientes do backend Flask
            url = "http://localhost:5000/clients"
            payload = {
                "email": email,
                "age": int(idade) if idade.isdigit() else idade,
                "password": senha
            }
            response = requests.post(url, json=payload, timeout=5)
            
            if response.status_code in [200, 201]:
                QMessageBox.information(self, "Sucesso", "Cadastro realizado com sucesso!")
                self.switch_to_login.emit()
            else:
                try:
                    error_msg = response.json().get("error", "Erro ao cadastrar.")
                except:
                    error_msg = response.text
                QMessageBox.critical(self, "Erro", f"Falha no cadastro: {error_msg}")
        except requests.exceptions.ConnectionError:
            QMessageBox.critical(self, "Erro de Conexão", "Não foi possível conectar ao servidor backend. Verifique se o Flask está rodando.")
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Ocorreu um erro inesperado: {str(e)}")