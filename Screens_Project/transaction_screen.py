import os
import sys
from datetime import datetime
from PyQt6.QtCore import Qt, pyqtSignal, QDateTime
from PyQt6.QtGui import QColor, QPainter, QLinearGradient
from PyQt6.QtWidgets import (
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
    QWidget,
    QComboBox,
    QDateTimeEdit,
    QTableWidget,
    QTableWidgetItem,
    QGraphicsDropShadowEffect,
    QMessageBox,
    QHeaderView,
    QFrame,
)

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from client_api import api
from utils import format_currency, format_datetime, criar_botao_acao


class TransactionWindow(QWidget):
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

        # Topo
        top = QHBoxLayout()
        title_box = QVBoxLayout()
        title = QLabel("Simulador & Auditor de Transações em Tempo Real")
        title.setObjectName("TitleLabel")
        subtitle = QLabel("Submeta operações para verificação imediata das 7 regras heurísticas de fraude")
        subtitle.setObjectName("SubtitleLabel")
        title_box.addWidget(title)
        title_box.addWidget(subtitle)

        self.btn_voltar = QPushButton("Voltar ao Dashboard")
        self.btn_voltar.setObjectName("LinkButton")
        self.btn_voltar.clicked.connect(self.switch_to_dashboard.emit)

        top.addLayout(title_box)
        top.addStretch()
        top.addWidget(self.btn_voltar)

        # Formulário de Simulação Rápida
        form_frame = QWidget()
        form_frame.setObjectName("GlassCard")
        form_layout = QGridLayout(form_frame)
        form_layout.setContentsMargins(20, 15, 20, 15)

        form_layout.addWidget(QLabel("Cliente ID:"), 0, 0)
        self.input_client_id = QLineEdit()
        self.input_client_id.setObjectName("InputField")
        self.input_client_id.setPlaceholderText("ID do Cliente (ex: 1)")
        form_layout.addWidget(self.input_client_id, 1, 0)

        form_layout.addWidget(QLabel("Tipo de Transação:"), 0, 1)
        self.combo_tipo = QComboBox()
        self.combo_tipo.setObjectName("InputField")
        self.combo_tipo.addItems(["PIX", "TED", "CARD", "WITHDRAWAL", "BOLETO"])
        form_layout.addWidget(self.combo_tipo, 1, 1)

        form_layout.addWidget(QLabel("Valor da Operação (R$):"), 0, 2)
        self.input_valor = QLineEdit()
        self.input_valor.setObjectName("InputField")
        self.input_valor.setPlaceholderText("Ex: 3500.00")
        form_layout.addWidget(self.input_valor, 1, 2)

        form_layout.addWidget(QLabel("Destinatário:"), 2, 0)
        self.input_destino = QLineEdit()
        self.input_destino.setObjectName("InputField")
        self.input_destino.setPlaceholderText("Ex: Mercado Pago")
        form_layout.addWidget(self.input_destino, 3, 0)

        form_layout.addWidget(QLabel("Localidade:"), 2, 1)
        self.input_local = QLineEdit()
        self.input_local.setObjectName("InputField")
        self.input_local.setPlaceholderText("Ex: São Paulo")
        form_layout.addWidget(self.input_local, 3, 1)

        form_layout.addWidget(QLabel("Data/Hora da Operação:"), 2, 2)
        self.input_data = QDateTimeEdit()
        self.input_data.setObjectName("InputField")
        self.input_data.setDateTime(QDateTime.currentDateTime())
        self.input_data.setDisplayFormat("dd/MM/yyyy HH:mm:ss")
        form_layout.addWidget(self.input_data, 3, 2)

        self.btn_simular = QPushButton("⚡ Executar Análise Antifraude")
        self.btn_simular.setObjectName("LoginButton")
        self.btn_simular.setFixedHeight(38)
        self.btn_simular.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_simular.clicked.connect(self.executar_simulacao)
        form_layout.addWidget(self.btn_simular, 4, 0, 1, 3)

        # Histórico recente
        lbl_hist = QLabel("Últimas Operações Processadas:")
        lbl_hist.setObjectName("FieldLabel")

        self.table_hist = QTableWidget(0, 8)
        self.table_hist.setObjectName("GlassTable")
        self.table_hist.setHorizontalHeaderLabels([
            "ID", "Cliente ID", "Valor", "Tipo", "Destino", "Score", "Classificação", "Ações"
        ])
        self.table_hist.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeMode.Stretch)
        self.table_hist.verticalHeader().setDefaultSectionSize(44)
        self.table_hist.verticalHeader().setVisible(False)
        self.table_hist.setColumnWidth(0, 50)
        self.table_hist.setColumnWidth(1, 75)
        self.table_hist.setColumnWidth(2, 110)
        self.table_hist.setColumnWidth(3, 85)
        self.table_hist.setColumnWidth(5, 85)
        self.table_hist.setColumnWidth(6, 110)
        self.table_hist.setColumnWidth(7, 140)

        card_layout.addLayout(top)
        card_layout.addSpacing(10)
        card_layout.addWidget(form_frame)
        card_layout.addSpacing(12)
        card_layout.addWidget(lbl_hist)
        card_layout.addWidget(self.table_hist)

        main_layout.addWidget(card)

    def executar_simulacao(self):
        cid_text = self.input_client_id.text().strip()
        valor_text = self.input_valor.text().strip().replace("R$", "").replace(".", "").replace(",", ".")
        tipo = self.combo_tipo.currentText()
        destino = self.input_destino.text().strip()
        local = self.input_local.text().strip()
        dt = self.input_data.dateTime().toPyDateTime()

        if not cid_text or not valor_text or not destino or not local:
            QMessageBox.warning(self, "Aviso", "Preencha todos os campos da transação!")
            return

        try:
            cid = int(cid_text)
            valor = float(valor_text)
            if cid <= 0 or valor <= 0:
                raise ValueError()
        except ValueError:
            QMessageBox.warning(self, "Aviso", "Cliente ID e Valor devem ser numéricos positivos.")
            return

        if dt > datetime.now():
            dt = datetime.now()

        payload = {
            "client_id": cid,
            "amount": valor,
            "transaction_type": tipo,
            "destination": destino,
            "location": local,
            "occurred_at": dt.isoformat(),
        }

        success, res = api.create_transaction(payload)
        if success and isinstance(res, dict):
            score = res.get("risk_score", 0)
            classif = res.get("classification", "NORMAL")
            alerts = res.get("alerts", [])

            msg = (
                f"Resultado da Avaliação pelo Motor de Detecção:\n\n"
                f"• Transação ID: #{res.get('id')}\n"
                f"• Score de Risco: {score}/100\n"
                f"• Classificação: {classif}\n"
                f"• Total de Regras Violadas: {len(alerts)}\n"
            )
            if alerts:
                msg += "\nDetalhes dos Alertas:\n"
                for al in alerts:
                    msg += f"  - [{al.get('rule_code')}]: {al.get('reason')} (+{al.get('points')} pts)\n"

            QMessageBox.information(self, "Análise Concluída", msg)
            self.carregar_historico()
        else:
            QMessageBox.critical(self, "Erro", f"Falha ao processar transação:\n{res}")

    def carregar_historico(self):
        success, txs = api.list_transactions(limit=15)
        if not success or not isinstance(txs, list):
            return

        self.table_hist.setRowCount(len(txs))
        for row, tx in enumerate(txs):
            self.table_hist.setItem(row, 0, QTableWidgetItem(str(tx.get("id", ""))))
            self.table_hist.setItem(row, 1, QTableWidgetItem(str(tx.get("client_id", ""))))
            self.table_hist.setItem(row, 2, QTableWidgetItem(format_currency(tx.get("amount"))))
            self.table_hist.setItem(row, 3, QTableWidgetItem(str(tx.get("transaction_type", ""))))
            self.table_hist.setItem(row, 4, QTableWidgetItem(str(tx.get("destination", ""))))

            score = tx.get("risk_score", 0)
            score_item = QTableWidgetItem(f"{score}/100")
            self.table_hist.setItem(row, 5, score_item)

            c = tx.get("classification", "")
            class_item = QTableWidgetItem(c)
            if c == "SUSPICIOUS":
                class_item.setForeground(QColor("#ef4444"))
                score_item.setForeground(QColor("#ef4444"))
            elif c == "ATTENTION":
                class_item.setForeground(QColor("#f59e0b"))
                score_item.setForeground(QColor("#f59e0b"))
            else:
                class_item.setForeground(QColor("#10b981"))
                score_item.setForeground(QColor("#10b981"))
            self.table_hist.setItem(row, 6, class_item)

            btn = criar_botao_acao("Ver Auditoria", "purple", lambda _, t=tx: self._mostrar_auditoria(t))
            self.table_hist.setCellWidget(row, 7, btn)

    def _mostrar_auditoria(self, tx):
        from Screens_Project.main_dashboard import TransactionAlertsDialog
        dialog = TransactionAlertsDialog(self, tx_data=tx)
        dialog.exec()

