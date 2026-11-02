import os
import sys
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor, QPainter, QLinearGradient
from PyQt6.QtWidgets import (
    QLabel,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QWidget,
    QTableWidget,
    QTableWidgetItem,
    QGraphicsDropShadowEffect,
    QHeaderView,
    QMessageBox,
)

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from client_api import api
from utils import format_currency, format_datetime


class AnomaliesWindow(QWidget):
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
        main_layout.setContentsMargins(40, 30, 40, 30)

        card = QWidget(self)
        card.setObjectName("GlassCard")

        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(40)
        shadow.setColor(QColor(0, 0, 0, 60))
        shadow.setOffset(0, 12)
        card.setGraphicsEffect(shadow)

        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(30, 25, 30, 25)

        # Cabeçalho
        top = QHBoxLayout()
        title_box = QVBoxLayout()
        title = QLabel("Central de Auditoria de Anomalias & Fraudes")
        title.setObjectName("TitleLabel")
        subtitle = QLabel("Monitoramento focado em transações de alto risco (ATENÇÃO e SUSPEITAS)")
        subtitle.setObjectName("SubtitleLabel")
        title_box.addWidget(title)
        title_box.addWidget(subtitle)

        self.btn_refresh = QPushButton("🔄 Atualizar Anomalias")
        self.btn_refresh.setObjectName("LoginButton")
        self.btn_refresh.clicked.connect(self.carregar_anomalias)

        self.btn_voltar = QPushButton("Voltar ao Dashboard")
        self.btn_voltar.setObjectName("LinkButton")
        self.btn_voltar.clicked.connect(self.switch_to_dashboard.emit)

        top.addLayout(title_box)
        top.addStretch()
        top.addWidget(self.btn_refresh)
        top.addWidget(self.btn_voltar)

        # Cartões de Métricas
        metrics_layout = QHBoxLayout()
        metrics_layout.setSpacing(15)

        self.card_suspeitas = self._criar_card_metrica("Transações Suspeitas", "0", "#ef4444")
        self.card_atencao = self._criar_card_metrica("Transações sob Atenção", "0", "#f59e0b")
        self.card_alertas = self._criar_card_metrica("Alertas de Regras Gerados", "0", "#38bdf8")

        metrics_layout.addWidget(self.card_suspeitas)
        metrics_layout.addWidget(self.card_atencao)
        metrics_layout.addWidget(self.card_alertas)

        # Tabela de Anomalias
        self.table = QTableWidget(0, 8)
        self.table.setObjectName("GlassTable")
        self.table.setHorizontalHeaderLabels([
            "ID Tx", "Cliente ID", "Valor", "Tipo", "Destino", "Score de Risco", "Classificação", "Ações"
        ])
        self.table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeMode.Stretch)

        card_layout.addLayout(top)
        card_layout.addSpacing(15)
        card_layout.addLayout(metrics_layout)
        card_layout.addSpacing(15)
        card_layout.addWidget(self.table)

        main_layout.addWidget(card)

    def _criar_card_metrica(self, titulo: str, valor_inicial: str, cor: str) -> QWidget:
        w = QWidget()
        w.setObjectName("GlassCard")
        w.setStyleSheet(f"border-left: 4px solid {cor}; padding: 10px;")
        lay = QVBoxLayout(w)
        lbl_t = QLabel(titulo)
        lbl_t.setStyleSheet("color: rgba(255, 255, 255, 0.8); font-size: 12px; font-weight: 600;")
        lbl_v = QLabel(valor_inicial)
        lbl_v.setObjectName("MetricVal")
        lbl_v.setStyleSheet(f"color: {cor}; font-size: 24px; font-weight: bold;")
        lay.addWidget(lbl_t)
        lay.addWidget(lbl_v)
        return w

    def carregar_anomalias(self):
        # Carrega transações suspeitas
        s_ok, tx_susp = api.list_transactions(classification="SUSPICIOUS")
        a_ok, tx_aten = api.list_transactions(classification="ATTENTION")
        al_ok, alertas = api.list_alerts()

        susp_list = tx_susp if s_ok and isinstance(tx_susp, list) else []
        aten_list = tx_aten if a_ok and isinstance(tx_aten, list) else []
        alertas_list = alertas if al_ok and isinstance(alertas, list) else []

        # Atualiza métricas
        self.card_suspeitas.findChild(QLabel, "MetricVal").setText(str(len(susp_list)))
        self.card_atencao.findChild(QLabel, "MetricVal").setText(str(len(aten_list)))
        self.card_alertas.findChild(QLabel, "MetricVal").setText(str(len(alertas_list)))

        todas = susp_list + aten_list
        self.table.setRowCount(len(todas))

        for row, tx in enumerate(todas):
            self.table.setItem(row, 0, QTableWidgetItem(str(tx.get("id", ""))))
            self.table.setItem(row, 1, QTableWidgetItem(str(tx.get("client_id", ""))))
            self.table.setItem(row, 2, QTableWidgetItem(format_currency(tx.get("amount"))))
            self.table.setItem(row, 3, QTableWidgetItem(str(tx.get("transaction_type", ""))))
            self.table.setItem(row, 4, QTableWidgetItem(str(tx.get("destination", ""))))

            score = tx.get("risk_score", 0)
            score_item = QTableWidgetItem(f"{score}/100")
            self.table.setItem(row, 5, score_item)

            c = tx.get("classification", "")
            class_item = QTableWidgetItem(c)
            if c == "SUSPICIOUS":
                class_item.setForeground(QColor("#ef4444"))
                score_item.setForeground(QColor("#ef4444"))
            else:
                class_item.setForeground(QColor("#f59e0b"))
                score_item.setForeground(QColor("#f59e0b"))
            self.table.setItem(row, 6, class_item)

            btn = QPushButton("Ver Auditoria")
            btn.setObjectName("LinkButton")
            btn.clicked.connect(lambda _, t=tx: self._mostrar_auditoria(t))
            self.table.setCellWidget(row, 7, btn)

    def _mostrar_auditoria(self, tx):
        from Screens_Project.main_dashboard import TransactionAlertsDialog
        dialog = TransactionAlertsDialog(self, tx_data=tx)
        dialog.exec()

