import os
import sys
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor, QPainter, QLinearGradient
from PyQt6.QtWidgets import (
    QLabel,
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
from utils import CpfValidator, format_currency, format_datetime


class ProfileWindow(QWidget):
    switch_to_dashboard = pyqtSignal()
    switch_to_login = pyqtSignal()

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
        card.setFixedSize(560, 680)
        card.setObjectName("GlassCard")

        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(40)
        shadow.setColor(QColor(0, 0, 0, 60))
        shadow.setOffset(0, 12)
        card.setGraphicsEffect(shadow)

        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(40, 35, 40, 35)

        title = QLabel("Meu Perfil de Cliente")
        title.setObjectName("TitleLabel")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        subtitle = QLabel("Parâmetros de referência utilizados para detecção de anomalias")
        subtitle.setObjectName("SubtitleLabel")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.info_grid = QGridLayout()
        self.info_grid.setVerticalSpacing(12)
        self.info_grid.setHorizontalSpacing(15)

        self.lbl_nome = QLabel("-")
        self.lbl_nome.setObjectName("DevLabel")
        self.lbl_cpf = QLabel("-")
        self.lbl_cpf.setObjectName("DevLabel")
        self.lbl_renda = QLabel("-")
        self.lbl_renda.setObjectName("DevLabel")
        self.lbl_cidade = QLabel("-")
        self.lbl_cidade.setObjectName("DevLabel")
        self.lbl_horario = QLabel("-")
        self.lbl_horario.setObjectName("DevLabel")
        self.lbl_status = QLabel("-")
        self.lbl_status.setObjectName("DevLabel")
        self.lbl_criado_em = QLabel("-")
        self.lbl_criado_em.setObjectName("DevLabel")

        # Labels de Título
        self.info_grid.addWidget(self._make_label("Nome Completo:"), 0, 0)
        self.info_grid.addWidget(self.lbl_nome, 0, 1)

        self.info_grid.addWidget(self._make_label("CPF:"), 1, 0)
        self.info_grid.addWidget(self.lbl_cpf, 1, 1)

        self.info_grid.addWidget(self._make_label("Renda Mensal Declarada:"), 2, 0)
        self.info_grid.addWidget(self.lbl_renda, 2, 1)

        self.info_grid.addWidget(self._make_label("Cidade Habitual:"), 3, 0)
        self.info_grid.addWidget(self.lbl_cidade, 3, 1)

        self.info_grid.addWidget(self._make_label("Janela Habitual de Operações:"), 4, 0)
        self.info_grid.addWidget(self.lbl_horario, 4, 1)

        self.info_grid.addWidget(self._make_label("Status da Conta:"), 5, 0)
        self.info_grid.addWidget(self.lbl_status, 5, 1)

        self.info_grid.addWidget(self._make_label("Data de Cadastro:"), 6, 0)
        self.info_grid.addWidget(self.lbl_criado_em, 6, 1)

        # Divisor
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setStyleSheet("color: rgba(255, 255, 255, 0.2);")

        # Seção de resumo de segurança
        sec_title = QLabel("Comportamento Padrão Monitorado:")
        sec_title.setObjectName("FieldLabel")

        self.sec_desc = QLabel(
            "Transações fora do seu horário habitual, em outras cidades ou com valores "
            "incompatíveis com a renda declarada receberão pontuação de risco adicional "
            "e poderão ser classificadas como ATENÇÃO ou SUSPEITA."
        )
        self.sec_desc.setWordWrap(True)
        self.sec_desc.setStyleSheet("color: rgba(255, 255, 255, 0.75); font-size: 12px; line-height: 1.4;")

        btn_box = QHBoxLayout()
        self.btn_voltar = QPushButton("Voltar ao Dashboard")
        self.btn_voltar.setObjectName("LoginButton")
        self.btn_voltar.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_voltar.clicked.connect(self.switch_to_dashboard.emit)

        btn_box.addWidget(self.btn_voltar)

        card_layout.addWidget(title)
        card_layout.addWidget(subtitle)
        card_layout.addSpacing(15)
        card_layout.addLayout(self.info_grid)
        card_layout.addSpacing(10)
        card_layout.addWidget(line)
        card_layout.addSpacing(8)
        card_layout.addWidget(sec_title)
        card_layout.addWidget(self.sec_desc)
        card_layout.addSpacing(20)
        card_layout.addLayout(btn_box)

        main_layout.addWidget(card)

    def _make_label(self, text: str) -> QLabel:
        lbl = QLabel(text)
        lbl.setObjectName("FieldLabel")
        return lbl

    def carregar_perfil(self):
        """Busca o perfil atualizado do backend via /auth/me."""
        success, me = api.get_me()
        if success and isinstance(me, dict):
            api.set_current_user(me)
            self.lbl_nome.setText(me.get("name", "-"))
            self.lbl_cpf.setText(CpfValidator.format_cpf(me.get("cpf", "-")))
            self.lbl_renda.setText(format_currency(me.get("monthly_income")))
            self.lbl_cidade.setText(me.get("usual_city", "-"))

            ini = me.get("usual_start_time", "")[:5]
            fim = me.get("usual_end_time", "")[:5]
            self.lbl_horario.setText(f"{ini} às {fim}")

            ativo = me.get("active", True)
            self.lbl_status.setText("Ativo (Monitorado)" if ativo else "Inativo")
            self.lbl_status.setStyleSheet("color: #10b981; font-weight: bold;" if ativo else "color: #ef4444; font-weight: bold;")

            self.lbl_criado_em.setText(format_datetime(me.get("created_at")))
        else:
            QMessageBox.warning(self, "Aviso", f"Não foi possível carregar os dados do perfil:\n{me}")

