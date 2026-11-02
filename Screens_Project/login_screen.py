import sys
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor, QPainter, QLinearGradient
from PyQt6.QtWidgets import (
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QWidget,
    QGraphicsDropShadowEffect,
    QMessageBox,
)

import sys
import os

# Adiciona o diretório raiz do front ao sys.path para importar client_api e utils
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from client_api import api
from utils import CpfValidator


class GlassLoginWindow(QWidget):
    switch_to_signin = pyqtSignal()
    switch_to_creditos = pyqtSignal()
    login_successful = pyqtSignal(dict)

    def __init__(self):
        super().__init__()
        self.initUI()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        gradient = QLinearGradient(0, 0, self.width(), self.height())
        gradient.setColorAt(0.0, QColor(79, 70, 229))
        gradient.setColorAt(1.0, QColor(59, 130, 246))
        painter.fillRect(self.rect(), gradient)

    def initUI(self):
        main_layout = QVBoxLayout(self)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        card = QWidget(self)
        card.setFixedSize(460, 600)
        card.setObjectName("GlassCard")

        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(40)
        shadow.setColor(QColor(0, 0, 0, 60))
        shadow.setOffset(0, 12)
        card.setGraphicsEffect(shadow)

        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(40, 30, 40, 30)
        card_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        title_label = QLabel("Bem-vindo")
        title_label.setObjectName("TitleLabel")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        subtitle_label = QLabel("Acesse o Sistema de Detecção de Anomalias")
        subtitle_label.setObjectName("SubtitleLabel")
        subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        cpf_label = QLabel("CPF (Apenas números ou formatado)")
        cpf_label.setObjectName("FieldLabel")
        self.cpf_input = QLineEdit()
        self.cpf_input.setObjectName("InputField")
        self.cpf_input.setPlaceholderText("000.000.000-00")
        self.cpf_input.returnPressed.connect(self.realizar_login)

        senha_label = QLabel("Senha de Acesso")
        senha_label.setObjectName("FieldLabel")
        self.senha_input = QLineEdit()
        self.senha_input.setObjectName("InputField")
        self.senha_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.senha_input.setPlaceholderText("••••••••")
        self.senha_input.returnPressed.connect(self.realizar_login)

        self.btn_entrar = QPushButton("Entrar")
        self.btn_entrar.setObjectName("LoginButton")
        self.btn_entrar.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_entrar.clicked.connect(self.realizar_login)

        # Botão de Créditos
        self.btn_creditos = QPushButton("Créditos do Projeto")
        self.btn_creditos.setObjectName("LinkButton")
        self.btn_creditos.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_creditos.clicked.connect(self.switch_to_creditos.emit)

        footer_layout = QHBoxLayout()
        footer_label = QLabel("Não tem uma conta cadastrada?")
        footer_label.setObjectName("FooterLabel")

        self.btn_signin = QPushButton("Cadastre-se")
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
        card_layout.addWidget(cpf_label)
        card_layout.addWidget(self.cpf_input)
        card_layout.addSpacing(8)
        card_layout.addWidget(senha_label)
        card_layout.addWidget(self.senha_input)
        card_layout.addSpacing(18)
        card_layout.addWidget(self.btn_entrar)
        card_layout.addSpacing(10)
        card_layout.addWidget(self.btn_creditos, alignment=Qt.AlignmentFlag.AlignCenter)
        card_layout.addSpacing(10)
        card_layout.addLayout(footer_layout)

        main_layout.addWidget(card)

    def realizar_login(self):
        username = self.cpf_input.text().strip()
        senha = self.senha_input.text().strip()

        if not username or not senha:
            QMessageBox.warning(self, "Campos Obrigatórios", "Por favor, preencha o CPF e a senha para entrar.")
            return

        self.btn_entrar.setEnabled(False)
        self.btn_entrar.setText("Autenticando...")

        try:
            success, result = api.login(username, senha)
            if success:
                self.senha_input.clear()
                user_data = api.current_user or {}
                self.login_successful.emit(user_data)
            else:
                QMessageBox.critical(
                    self,
                    "Falha no Login",
                    f"Não foi possível autenticar:\n\n{result}"
                )
        except Exception as e:
            QMessageBox.critical(self, "Erro Inesperado", f"Ocorreu um erro ao tentar conectar:\n{str(e)}")
        finally:
            self.btn_entrar.setEnabled(True)
            self.btn_entrar.setText("Entrar")
