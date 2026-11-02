import os
import sys
import time
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor, QPainter, QLinearGradient
from PyQt6.QtWidgets import (
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
    QWidget,
    QGraphicsDropShadowEffect,
    QMessageBox,
    QFrame,
)

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from client_api import api


class SettingsWindow(QWidget):
    switch_to_dashboard = pyqtSignal()

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
        main_layout.setContentsMargins(40, 40, 40, 40)

        card = QWidget(self)
        card.setFixedSize(540, 620)
        card.setObjectName("GlassCard")

        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(40)
        shadow.setColor(QColor(0, 0, 0, 60))
        shadow.setOffset(0, 12)
        card.setGraphicsEffect(shadow)

        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(35, 30, 35, 30)

        title = QLabel("Configurações do Sistema")
        title.setObjectName("TitleLabel")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        subtitle = QLabel("Parâmetros de Conexão com o Backend e Diagnóstico")
        subtitle.setObjectName("SubtitleLabel")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)

        form = QVBoxLayout()
        form.setSpacing(8)

        lbl_url = QLabel("Endereço Base da API REST (FastAPI):")
        lbl_url.setObjectName("FieldLabel")

        self.input_url = QLineEdit()
        self.input_url.setObjectName("InputField")
        self.input_url.setText(api.base_url)

        self.btn_salvar_url = QPushButton("Atualizar Endereço da API")
        self.btn_salvar_url.setObjectName("LoginButton")
        self.btn_salvar_url.clicked.connect(self.salvar_url)

        self.btn_testar = QPushButton("⚡ Testar Conexão com Servidor (Health Check)")
        self.btn_testar.setObjectName("LoginButton")
        self.btn_testar.clicked.connect(self.testar_conexao)

        self.lbl_status_conexao = QLabel("Status: Aguardando teste de conexão...")
        self.lbl_status_conexao.setStyleSheet("color: rgba(255, 255, 255, 0.85); font-weight: 600; font-size: 13px;")

        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setStyleSheet("color: rgba(255, 255, 255, 0.2);")

        lbl_info_title = QLabel("Informações de Arquitetura:")
        lbl_info_title.setObjectName("FieldLabel")

        info_text = QLabel(
            "• <b>Back-end:</b> FastAPI 0.149 + SQLAlchemy 2.1 + PostgreSQL 16<br>"
            "• <b>Front-end:</b> PyQt6 6.11 (Python 3.14)<br>"
            "• <b>Segurança:</b> JWT Bearer Tokens (HS256) & Hash Scrypt<br>"
            "• <b>Motor Heurístico:</b> 7 Regras de Detecção de Anomalias Financeiras<br>"
            "• <b>Porta da API:</b> 8000 | <b>Porta do Banco:</b> 5432"
        )
        info_text.setStyleSheet("color: rgba(255, 255, 255, 0.85); font-size: 12px; line-height: 1.5;")

        self.btn_voltar = QPushButton("Voltar ao Dashboard")
        self.btn_voltar.setObjectName("LinkButton")
        self.btn_voltar.clicked.connect(self.switch_to_dashboard.emit)

        card_layout.addWidget(title)
        card_layout.addWidget(subtitle)
        card_layout.addSpacing(15)
        card_layout.addWidget(lbl_url)
        card_layout.addWidget(self.input_url)
        card_layout.addWidget(self.btn_salvar_url)
        card_layout.addSpacing(10)
        card_layout.addWidget(self.btn_testar)
        card_layout.addWidget(self.lbl_status_conexao)
        card_layout.addSpacing(15)
        card_layout.addWidget(line)
        card_layout.addSpacing(10)
        card_layout.addWidget(lbl_info_title)
        card_layout.addWidget(info_text)
        card_layout.addSpacing(20)
        card_layout.addWidget(self.btn_voltar, alignment=Qt.AlignmentFlag.AlignCenter)

        main_layout.addWidget(card)

    def salvar_url(self):
        nova_url = self.input_url.text().strip()
        if not nova_url.startswith("http://") and not nova_url.startswith("https://"):
            QMessageBox.warning(self, "URL Inválida", "A URL deve começar com http:// ou https://")
            return
        api.set_base_url(nova_url)
        QMessageBox.information(self, "Sucesso", f"Endereço da API atualizado para:\n{nova_url}")

    def testar_conexao(self):
        self.lbl_status_conexao.setText("Testando conexão com o backend...")
        t0 = time.time()
        success, res = api.health_check()
        latencia_ms = int((time.time() - t0) * 1000)

        if success:
            self.lbl_status_conexao.setText(f"✅ Conectado com sucesso! Resposta: {res} ({latencia_ms} ms)")
            self.lbl_status_conexao.setStyleSheet("color: #10b981; font-weight: bold; font-size: 13px;")
            QMessageBox.information(
                self,
                "Conexão Bem-Sucedida",
                f"O backend FastAPI respondeu normalmente!\n\n"
                f"• Endpoint: {api.base_url}/\n"
                f"• Resposta: {res}\n"
                f"• Latência: {latencia_ms} ms",
            )
        else:
            self.lbl_status_conexao.setText(f"❌ Falha na conexão com {api.base_url}")
            self.lbl_status_conexao.setStyleSheet("color: #ef4444; font-weight: bold; font-size: 13px;")
            QMessageBox.critical(
                self,
                "Falha na Conexão",
                f"Não foi possível conectar ao backend em {api.base_url}:\n\n{res}\n\n"
                "Verifique se o backend FastAPI foi iniciado com 'docker compose up' ou 'uvicorn app:app --reload'.",
            )

