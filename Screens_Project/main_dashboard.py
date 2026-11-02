import os
import sys
from datetime import datetime
from PyQt6.QtCore import Qt, pyqtSignal, QTime, QDateTime
from PyQt6.QtGui import QColor, QPainter, QLinearGradient, QFont
from PyQt6.QtWidgets import (
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
    QWidget,
    QTabWidget,
    QTableWidget,
    QTableWidgetItem,
    QDialog,
    QGraphicsDropShadowEffect,
    QMessageBox,
    QComboBox,
    QDateTimeEdit,
    QTimeEdit,
    QCheckBox,
    QHeaderView,
    QFrame,
    QTextEdit,
)

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from client_api import api
from utils import CpfValidator, format_currency, format_datetime, criar_botao_acao


# ============================================================================
# MODAIS: CLIENTES
# ============================================================================

class ClientFormDialog(QDialog):
    """Modal de criação ou edição de cliente em conformidade com ClientCreate/ClientUpdate."""

    def __init__(self, parent=None, client_data=None):
        super().__init__(parent)
        self.client_data = client_data
        self.is_edit = client_data is not None
        self.setWindowTitle("Editar Cliente" if self.is_edit else "Novo Cliente")
        self.setFixedSize(520, 680)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.initUI()
        if self.is_edit:
            self.preencher_dados()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        gradient = QLinearGradient(0, 0, self.width(), self.height())
        gradient.setColorAt(0.0, QColor(25, 30, 50, 245))
        gradient.setColorAt(1.0, QColor(15, 20, 35, 245))
        painter.setBrush(gradient)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(self.rect(), 20, 20)

    def initUI(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 25, 30, 25)

        title = QLabel("Editar Cliente" if self.is_edit else "Cadastrar Novo Cliente")
        title.setObjectName("TitleLabel")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        form = QGridLayout()
        form.setVerticalSpacing(8)
        form.setHorizontalSpacing(12)

        # Nome
        form.addWidget(QLabel("Nome Completo:"), 0, 0, 1, 2)
        self.nome_input = QLineEdit()
        self.nome_input.setObjectName("InputField")
        self.nome_input.setPlaceholderText("Ex: Carlos Drummond")
        form.addWidget(self.nome_input, 1, 0, 1, 2)

        # CPF
        form.addWidget(QLabel("CPF:"), 2, 0)
        self.cpf_input = QLineEdit()
        self.cpf_input.setObjectName("InputField")
        self.cpf_input.setPlaceholderText("000.000.000-00")
        form.addWidget(self.cpf_input, 3, 0)

        # Senha
        self.senha_label = QLabel("Nova Senha (opcional):" if self.is_edit else "Senha de Acesso *:")
        form.addWidget(self.senha_label, 2, 1)
        self.senha_input = QLineEdit()
        self.senha_input.setObjectName("InputField")
        self.senha_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.senha_input.setPlaceholderText("Mínimo 6 dígitos")
        form.addWidget(self.senha_input, 3, 1)

        # Renda Mensal
        form.addWidget(QLabel("Renda Mensal Declarada (R$):"), 4, 0)
        self.renda_input = QLineEdit()
        self.renda_input.setObjectName("InputField")
        self.renda_input.setPlaceholderText("Ex: 5000.00")
        form.addWidget(self.renda_input, 5, 0)

        # Cidade Habitual
        form.addWidget(QLabel("Cidade Habitual:"), 4, 1)
        self.cidade_input = QLineEdit()
        self.cidade_input.setObjectName("InputField")
        self.cidade_input.setPlaceholderText("Ex: Niterói")
        form.addWidget(self.cidade_input, 5, 1)

        # Horário Início
        form.addWidget(QLabel("Horário Inicial:"), 6, 0)
        self.hora_ini = QTimeEdit()
        self.hora_ini.setObjectName("InputField")
        self.hora_ini.setTime(QTime(8, 0))
        self.hora_ini.setDisplayFormat("HH:mm")
        form.addWidget(self.hora_ini, 7, 0)

        # Horário Fim
        form.addWidget(QLabel("Horário Final:"), 6, 1)
        self.hora_fim = QTimeEdit()
        self.hora_fim.setObjectName("InputField")
        self.hora_fim.setTime(QTime(18, 0))
        self.hora_fim.setDisplayFormat("HH:mm")
        form.addWidget(self.hora_fim, 7, 1)

        # Status Ativo (apenas na edição)
        self.chk_ativo = QCheckBox("Cliente Ativo no Monitoramento")
        self.chk_ativo.setChecked(True)
        self.chk_ativo.setStyleSheet("color: white; font-weight: bold; font-size: 13px;")
        if not self.is_edit:
            self.chk_ativo.setVisible(False)
        form.addWidget(self.chk_ativo, 8, 0, 1, 2)

        btn_box = QHBoxLayout()
        self.btn_cancelar = QPushButton("Cancelar")
        self.btn_cancelar.setObjectName("LinkButton")
        self.btn_cancelar.clicked.connect(self.reject)

        self.btn_salvar = QPushButton("Salvar Alterações" if self.is_edit else "Cadastrar Cliente")
        self.btn_salvar.setObjectName("LoginButton")
        self.btn_salvar.clicked.connect(self.salvar)

        btn_box.addWidget(self.btn_cancelar)
        btn_box.addWidget(self.btn_salvar)

        layout.addWidget(title)
        layout.addSpacing(10)
        layout.addLayout(form)
        layout.addSpacing(15)
        layout.addLayout(btn_box)

    def preencher_dados(self):
        c = self.client_data
        self.nome_input.setText(c.get("name", ""))
        self.cpf_input.setText(CpfValidator.format_cpf(c.get("cpf", "")))
        self.renda_input.setText(str(c.get("monthly_income", "")))
        self.cidade_input.setText(c.get("usual_city", ""))

        ini = c.get("usual_start_time", "08:00:00")
        fim = c.get("usual_end_time", "18:00:00")
        try:
            self.hora_ini.setTime(QTime.fromString(ini[:5], "HH:mm"))
            self.hora_fim.setTime(QTime.fromString(fim[:5], "HH:mm"))
        except Exception:
            pass

        self.chk_ativo.setChecked(bool(c.get("active", True)))

    def salvar(self):
        nome = self.nome_input.text().strip()
        raw_cpf = self.cpf_input.text().strip()
        senha = self.senha_input.text().strip()
        renda_text = self.renda_input.text().strip().replace("R$", "").replace(".", "").replace(",", ".")
        cidade = self.cidade_input.text().strip()
        hora_ini = self.hora_ini.time().toString("HH:mm:ss")
        hora_fim = self.hora_fim.time().toString("HH:mm:ss")

        if not nome or not raw_cpf or not renda_text or not cidade:
            QMessageBox.warning(self, "Aviso", "Preencha os campos obrigatórios (Nome, CPF, Renda e Cidade)!")
            return

        if not CpfValidator.is_valid(raw_cpf):
            QMessageBox.warning(self, "CPF Inválido", "O CPF informado é inválido perante o algoritmo da Receita Federal.")
            return

        if not self.is_edit and (not senha or len(senha) < 6):
            QMessageBox.warning(self, "Senha Obrigatória", "A senha de cadastro inicial deve ter pelo menos 6 caracteres.")
            return

        if self.is_edit and senha and len(senha) < 6:
            QMessageBox.warning(self, "Senha Inválida", "A nova senha deve ter no mínimo 6 caracteres.")
            return

        try:
            renda_val = float(renda_text)
            if renda_val <= 0:
                raise ValueError()
        except ValueError:
            QMessageBox.warning(self, "Renda Inválida", "Informe uma renda mensal válida superior a R$ 0,00.")
            return

        payload = {
            "name": nome,
            "cpf": CpfValidator.normalize(raw_cpf),
            "monthly_income": renda_val,
            "usual_city": cidade,
            "usual_start_time": hora_ini,
            "usual_end_time": hora_fim,
        }

        if not self.is_edit:
            payload["password"] = senha
            success, res = api.create_client(payload)
        else:
            payload["active"] = self.chk_ativo.isChecked()
            if senha:
                payload["password"] = senha
            success, res = api.update_client(self.client_data["id"], payload)

        if success:
            QMessageBox.information(
                self,
                "Sucesso",
                "Cliente atualizado com sucesso!" if self.is_edit else "Cliente cadastrado com sucesso!",
            )
            self.accept()
        else:
            QMessageBox.critical(self, "Erro na Operação", f"Não foi possível salvar o cliente:\n\n{res}")


# ============================================================================
# MODAIS: TRANSAÇÕES & ANÁLISE DE FRAUDE
# ============================================================================

class TransactionCreateDialog(QDialog):
    """Modal para registrar uma nova transação financeira e submeter ao motor de anomalias."""

    def __init__(self, parent=None, default_client_id=None):
        super().__init__(parent)
        self.default_client_id = default_client_id
        self.setWindowTitle("Nova Transação")
        self.setFixedSize(500, 600)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.created_transaction = None
        self.initUI()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        gradient = QLinearGradient(0, 0, self.width(), self.height())
        gradient.setColorAt(0.0, QColor(25, 30, 50, 245))
        gradient.setColorAt(1.0, QColor(15, 20, 35, 245))
        painter.setBrush(gradient)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(self.rect(), 20, 20)

    def initUI(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 25, 30, 25)

        title = QLabel("Registrar Transação Financeira")
        title.setObjectName("TitleLabel")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        subtitle = QLabel("A operação será avaliada pelo motor de detecção em tempo real")
        subtitle.setObjectName("SubtitleLabel")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)

        form = QGridLayout()
        form.setVerticalSpacing(8)
        form.setHorizontalSpacing(12)

        # Cliente ID
        form.addWidget(QLabel("ID do Cliente:"), 0, 0)
        self.client_id_input = QLineEdit()
        self.client_id_input.setObjectName("InputField")
        if self.default_client_id:
            self.client_id_input.setText(str(self.default_client_id))
        self.client_id_input.setPlaceholderText("Ex: 1")
        form.addWidget(self.client_id_input, 1, 0)

        # Tipo de Transação
        form.addWidget(QLabel("Tipo de Transação:"), 0, 1)
        self.tipo_combo = QComboBox()
        self.tipo_combo.setObjectName("InputField")
        self.tipo_combo.addItems(["PIX", "TED", "CARD", "WITHDRAWAL", "BOLETO"])
        form.addWidget(self.tipo_combo, 1, 1)

        # Valor
        form.addWidget(QLabel("Valor da Operação (R$):"), 2, 0)
        self.valor_input = QLineEdit()
        self.valor_input.setObjectName("InputField")
        self.valor_input.setPlaceholderText("Ex: 1500.00")
        form.addWidget(self.valor_input, 3, 0)

        # Destinatário
        form.addWidget(QLabel("Destinatário / Favorecido:"), 2, 1)
        self.destino_input = QLineEdit()
        self.destino_input.setObjectName("InputField")
        self.destino_input.setPlaceholderText("Ex: Loja Eletrônicos XYZ")
        form.addWidget(self.destino_input, 3, 1)

        # Localização da Operação
        form.addWidget(QLabel("Localização (Cidade/UF):"), 4, 0)
        self.local_input = QLineEdit()
        self.local_input.setObjectName("InputField")
        self.local_input.setPlaceholderText("Ex: São Paulo")
        form.addWidget(self.local_input, 5, 0)

        # Data e Hora da Ocorrência
        form.addWidget(QLabel("Data e Hora da Operação:"), 4, 1)
        self.data_input = QDateTimeEdit()
        self.data_input.setObjectName("InputField")
        self.data_input.setDateTime(QDateTime.currentDateTime())
        self.data_input.setDisplayFormat("dd/MM/yyyy HH:mm:ss")
        self.data_input.setCalendarPopup(True)
        form.addWidget(self.data_input, 5, 1)

        btn_box = QHBoxLayout()
        self.btn_cancelar = QPushButton("Cancelar")
        self.btn_cancelar.setObjectName("LinkButton")
        self.btn_cancelar.clicked.connect(self.reject)

        self.btn_salvar = QPushButton("Submeter Operação")
        self.btn_salvar.setObjectName("LoginButton")
        self.btn_salvar.clicked.connect(self.salvar)

        btn_box.addWidget(self.btn_cancelar)
        btn_box.addWidget(self.btn_salvar)

        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addSpacing(10)
        layout.addLayout(form)
        layout.addSpacing(20)
        layout.addLayout(btn_box)

    def salvar(self):
        cid_text = self.client_id_input.text().strip()
        tipo = self.tipo_combo.currentText()
        valor_text = self.valor_input.text().strip().replace("R$", "").replace(".", "").replace(",", ".")
        destino = self.destino_input.text().strip()
        local = self.local_input.text().strip()
        dt_ocorreu = self.data_input.dateTime().toPyDateTime()

        if not cid_text or not valor_text or not destino or not local:
            QMessageBox.warning(self, "Aviso", "Por favor, preencha todos os campos da transação!")
            return

        try:
            cid = int(cid_text)
            if cid <= 0:
                raise ValueError()
        except ValueError:
            QMessageBox.warning(self, "ID Inválido", "O ID do Cliente deve ser um número inteiro positivo.")
            return

        try:
            valor = float(valor_text)
            if valor <= 0:
                raise ValueError()
        except ValueError:
            QMessageBox.warning(self, "Valor Inválido", "O valor da transação deve ser estritamente positivo (> R$ 0,00).")
            return

        # Backend regra: a data da transação não pode estar no futuro (tolerância de 1 min)
        if dt_ocorreu > datetime.now():
            dt_ocorreu = datetime.now()

        payload = {
            "client_id": cid,
            "amount": valor,
            "transaction_type": tipo,
            "destination": destino,
            "location": local,
            "occurred_at": dt_ocorreu.isoformat(),
        }

        success, res = api.create_transaction(payload)
        if success and isinstance(res, dict):
            self.created_transaction = res
            score = res.get("risk_score", 0)
            classif = res.get("classification", "NORMAL")
            alerts = res.get("alerts", [])

            msg = (
                f"Transação #{res.get('id')} processada com sucesso!\n\n"
                f"• Score de Risco Atribuído: {score}/100\n"
                f"• Classificação Final: {classif}\n"
                f"• Alertas Disparados: {len(alerts)}\n"
            )
            if alerts:
                msg += "\nRegras acionadas:\n"
                for al in alerts:
                    msg += f"  - [{al.get('rule_code')}]: {al.get('reason')} (+{al.get('points')} pts)\n"

            QMessageBox.information(self, "Análise do Motor Concluída", msg)
            self.accept()
        else:
            QMessageBox.critical(
                self,
                "Erro ao Processar Transação",
                f"Não foi possível registrar a transação:\n\n{res}",
            )


class TransactionAlertsDialog(QDialog):
    """Modal para visualização detalhada do Score de Risco e dos Alertas de uma Transação."""

    def __init__(self, parent=None, tx_data=None):
        super().__init__(parent)
        self.tx = tx_data or {}
        self.setWindowTitle(f"Auditoria da Transação #{self.tx.get('id')}")
        self.setFixedSize(560, 520)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.initUI()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        gradient = QLinearGradient(0, 0, self.width(), self.height())
        gradient.setColorAt(0.0, QColor(25, 30, 50, 245))
        gradient.setColorAt(1.0, QColor(15, 20, 35, 245))
        painter.setBrush(gradient)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(self.rect(), 20, 20)

    def initUI(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 25, 30, 25)

        title = QLabel(f"Auditoria de Risco - Transação #{self.tx.get('id')}")
        title.setObjectName("TitleLabel")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        classif = self.tx.get("classification", "NORMAL")
        score = self.tx.get("risk_score", 0)

        # Badge de risco
        badge = QLabel(f"CLASSIFICAÇÃO: {classif}  |  SCORE: {score}/100")
        badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        if classif == "SUSPICIOUS":
            badge.setStyleSheet("background-color: #ef4444; color: white; font-weight: bold; padding: 8px; border-radius: 8px;")
        elif classif == "ATTENTION":
            badge.setStyleSheet("background-color: #f59e0b; color: white; font-weight: bold; padding: 8px; border-radius: 8px;")
        else:
            badge.setStyleSheet("background-color: #10b981; color: white; font-weight: bold; padding: 8px; border-radius: 8px;")

        # Detalhes da operação
        info = QLabel(
            f"<b>Cliente ID:</b> {self.tx.get('client_id')} &nbsp;|&nbsp; "
            f"<b>Valor:</b> {format_currency(self.tx.get('amount'))} &nbsp;|&nbsp; "
            f"<b>Tipo:</b> {self.tx.get('transaction_type')}<br>"
            f"<b>Destino:</b> {self.tx.get('destination')}<br>"
            f"<b>Localidade:</b> {self.tx.get('location')} &nbsp;|&nbsp; "
            f"<b>Data:</b> {format_datetime(self.tx.get('occurred_at'))}"
        )
        info.setStyleSheet("color: white; font-size: 13px; line-height: 1.4;")

        alerts_title = QLabel("Regras Violadas e Alertas Gerados:")
        alerts_title.setObjectName("FieldLabel")

        self.table_alerts = QTableWidget(0, 3)
        self.table_alerts.setObjectName("GlassTable")
        self.table_alerts.setHorizontalHeaderLabels(["Código da Regra", "Pontos", "Motivo da Anomalia"])
        self.table_alerts.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)

        alerts = self.tx.get("alerts", [])
        self.table_alerts.setRowCount(len(alerts))
        for row, al in enumerate(alerts):
            self.table_alerts.setItem(row, 0, QTableWidgetItem(str(al.get("rule_code", ""))))
            self.table_alerts.setItem(row, 1, QTableWidgetItem(f"+{al.get('points', 0)}"))
            self.table_alerts.setItem(row, 2, QTableWidgetItem(str(al.get("reason", ""))))

        btn_fechar = QPushButton("Fechar")
        btn_fechar.setObjectName("LoginButton")
        btn_fechar.clicked.connect(self.accept)

        layout.addWidget(title)
        layout.addSpacing(6)
        layout.addWidget(badge)
        layout.addSpacing(10)
        layout.addWidget(info)
        layout.addSpacing(10)
        layout.addWidget(alerts_title)
        layout.addWidget(self.table_alerts)
        layout.addSpacing(12)
        layout.addWidget(btn_fechar)


# ============================================================================
# MODAIS: REGRAS DE DETECÇÃO
# ============================================================================

class RuleFormDialog(QDialog):
    """Modal para cadastro e edição de regras de detecção de fraudes."""

    def __init__(self, parent=None, rule_data=None):
        super().__init__(parent)
        self.rule = rule_data
        self.is_edit = rule_data is not None
        self.setWindowTitle("Editar Regra" if self.is_edit else "Nova Regra")
        self.setFixedSize(480, 560)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.initUI()
        if self.is_edit:
            self.preencher_dados()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        gradient = QLinearGradient(0, 0, self.width(), self.height())
        gradient.setColorAt(0.0, QColor(25, 30, 50, 245))
        gradient.setColorAt(1.0, QColor(15, 20, 35, 245))
        painter.setBrush(gradient)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(self.rect(), 20, 20)

    def initUI(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 25, 30, 25)

        title = QLabel("Editar Regra de Detecção" if self.is_edit else "Criar Nova Regra")
        title.setObjectName("TitleLabel")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        form = QGridLayout()
        form.setVerticalSpacing(8)
        form.setHorizontalSpacing(12)

        # Código (A-Z com _)
        form.addWidget(QLabel("Código Identificador (ex: PIX_SUSPEITO):"), 0, 0, 1, 2)
        self.codigo_input = QLineEdit()
        self.codigo_input.setObjectName("InputField")
        self.codigo_input.setPlaceholderText("MAIÚSCULAS_COM_UNDERLINE")
        if self.is_edit:
            self.codigo_input.setEnabled(False)  # Código é imutável
        form.addWidget(self.codigo_input, 1, 0, 1, 2)

        # Nome
        form.addWidget(QLabel("Nome da Regra:"), 2, 0, 1, 2)
        self.nome_input = QLineEdit()
        self.nome_input.setObjectName("InputField")
        self.nome_input.setPlaceholderText("Ex: Valor Acentuado")
        form.addWidget(self.nome_input, 3, 0, 1, 2)

        # Peso (1 a 100)
        form.addWidget(QLabel("Peso (Pontos de Risco 1 a 100):"), 4, 0)
        self.peso_input = QLineEdit()
        self.peso_input.setObjectName("InputField")
        self.peso_input.setPlaceholderText("Ex: 25")
        form.addWidget(self.peso_input, 5, 0)

        # Limite / Threshold
        form.addWidget(QLabel("Limite / Threshold (opcional):"), 4, 1)
        self.limite_input = QLineEdit()
        self.limite_input.setObjectName("InputField")
        self.limite_input.setPlaceholderText("Ex: 3 ou 0.50")
        form.addWidget(self.limite_input, 5, 1)

        # Janela de Tempo (minutos)
        form.addWidget(QLabel("Janela em Minutos (opcional):"), 6, 0)
        self.janela_input = QLineEdit()
        self.janela_input.setObjectName("InputField")
        self.janela_input.setPlaceholderText("Ex: 60")
        form.addWidget(self.janela_input, 7, 0)

        # Status Ativo
        self.chk_ativo = QCheckBox("Regra Ativa no Motor de Fraude")
        self.chk_ativo.setChecked(True)
        self.chk_ativo.setStyleSheet("color: white; font-weight: bold;")
        form.addWidget(self.chk_ativo, 7, 1)

        # Descrição
        form.addWidget(QLabel("Descrição da Anomalia:"), 8, 0, 1, 2)
        self.desc_input = QTextEdit()
        self.desc_input.setObjectName("InputField")
        self.desc_input.setFixedHeight(70)
        self.desc_input.setPlaceholderText("Explique quando esta anomalia deve ser disparada...")
        form.addWidget(self.desc_input, 9, 0, 1, 2)

        btn_box = QHBoxLayout()
        self.btn_cancelar = QPushButton("Cancelar")
        self.btn_cancelar.setObjectName("LinkButton")
        self.btn_cancelar.clicked.connect(self.reject)

        self.btn_salvar = QPushButton("Salvar Regra")
        self.btn_salvar.setObjectName("LoginButton")
        self.btn_salvar.clicked.connect(self.salvar)

        btn_box.addWidget(self.btn_cancelar)
        btn_box.addWidget(self.btn_salvar)

        layout.addWidget(title)
        layout.addSpacing(6)
        layout.addLayout(form)
        layout.addSpacing(14)
        layout.addLayout(btn_box)

    def preencher_dados(self):
        r = self.rule
        self.codigo_input.setText(r.get("code", ""))
        self.nome_input.setText(r.get("name", ""))
        self.peso_input.setText(str(r.get("weight", "")))
        th = r.get("threshold")
        self.limite_input.setText(str(th) if th is not None else "")
        w = r.get("window_minutes")
        self.janela_input.setText(str(w) if w is not None else "")
        self.desc_input.setText(r.get("description", "") or "")
        self.chk_ativo.setChecked(bool(r.get("active", True)))

    def salvar(self):
        codigo = self.codigo_input.text().strip().upper()
        nome = self.nome_input.text().strip()
        peso_text = self.peso_input.text().strip()
        limite_text = self.limite_input.text().strip()
        janela_text = self.janela_input.text().strip()
        desc = self.desc_input.toPlainText().strip()
        ativo = self.chk_ativo.isChecked()

        if not nome or not peso_text:
            QMessageBox.warning(self, "Aviso", "Nome e Peso da regra são obrigatórios!")
            return

        if not self.is_edit and not codigo:
            QMessageBox.warning(self, "Aviso", "O código identificador é obrigatório!")
            return

        try:
            peso = int(peso_text)
            if not (1 <= peso <= 100):
                raise ValueError()
        except ValueError:
            QMessageBox.warning(self, "Peso Inválido", "O peso deve ser um número inteiro entre 1 e 100.")
            return

        limite = None
        if limite_text:
            try:
                limite = float(limite_text)
            except ValueError:
                QMessageBox.warning(self, "Limite Inválido", "O limite deve ser numérico.")
                return

        janela = None
        if janela_text:
            try:
                janela = int(janela_text)
                if janela <= 0:
                    raise ValueError()
            except ValueError:
                QMessageBox.warning(self, "Janela Inválida", "A janela deve ser um número inteiro positivo de minutos.")
                return

        payload = {
            "name": nome,
            "weight": peso,
            "threshold": limite,
            "window_minutes": janela,
            "description": desc or None,
        }

        if not self.is_edit:
            payload["code"] = codigo
            success, res = api.create_rule(payload)
        else:
            payload["active"] = ativo
            success, res = api.update_rule(self.rule["id"], payload)

        if success:
            QMessageBox.information(self, "Sucesso", "Regra salva com sucesso!")
            self.accept()
        else:
            QMessageBox.critical(self, "Erro", f"Não foi possível salvar a regra:\n\n{res}")


# ============================================================================
# TELA PRINCIPAL: DASHBOARD
# ============================================================================

class MainDashboardWindow(QWidget):
    switch_to_login = pyqtSignal()
    switch_to_profile = pyqtSignal()
    switch_to_settings = pyqtSignal()

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
        main_layout.setContentsMargins(30, 25, 30, 25)

        card = QWidget(self)
        card.setObjectName("GlassCard")

        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(40)
        shadow.setColor(QColor(0, 0, 0, 60))
        shadow.setOffset(0, 12)
        card.setGraphicsEffect(shadow)

        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(30, 25, 30, 25)

        # ----------------------------------------------------
        # Cabeçalho Superior do Dashboard
        # ----------------------------------------------------
        top_layout = QHBoxLayout()

        title_box = QVBoxLayout()
        title_label = QLabel("Dashboard - Detecção de Anomalias Financeiras")
        title_label.setObjectName("TitleLabel")
        self.user_chip = QLabel("Sessão ativa: Carregando...")
        self.user_chip.setStyleSheet("color: rgba(255, 255, 255, 0.85); font-size: 13px; font-weight: 500;")
        title_box.addWidget(title_label)
        title_box.addWidget(self.user_chip)

        actions_box = QHBoxLayout()
        actions_box.setSpacing(8)

        self.btn_refresh = QPushButton("🔄 Recarregar")
        self.btn_refresh.setObjectName("LoginButton")
        self.btn_refresh.setFixedHeight(34)
        self.btn_refresh.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_refresh.clicked.connect(self.carregar_dados_backend)

        self.btn_perfil = QPushButton("👤 Perfil")
        self.btn_perfil.setObjectName("LoginButton")
        self.btn_perfil.setFixedHeight(34)
        self.btn_perfil.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_perfil.clicked.connect(self.switch_to_profile.emit)

        self.btn_settings = QPushButton("⚙️ Configurações")
        self.btn_settings.setObjectName("LoginButton")
        self.btn_settings.setFixedHeight(34)
        self.btn_settings.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_settings.clicked.connect(self.switch_to_settings.emit)

        self.btn_logout = QPushButton("🚪 Sair")
        self.btn_logout.setObjectName("LinkButton")
        self.btn_logout.setFixedHeight(34)
        self.btn_logout.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_logout.clicked.connect(self.fazer_logout)

        actions_box.addWidget(self.btn_refresh)
        actions_box.addWidget(self.btn_perfil)
        actions_box.addWidget(self.btn_settings)
        actions_box.addWidget(self.btn_logout)

        top_layout.addLayout(title_box)
        top_layout.addStretch()
        top_layout.addLayout(actions_box)

        # ----------------------------------------------------
        # Abas de Navegação
        # ----------------------------------------------------
        self.tabs = QTabWidget()
        self.tabs.setObjectName("GlassTabs")

        self.tab_clients = QWidget()
        self.init_tab_clients()

        self.tab_transactions = QWidget()
        self.init_tab_transactions()

        self.tab_rules = QWidget()
        self.init_tab_rules()

        self.tab_alerts = QWidget()
        self.init_tab_alerts()

        self.tabs.addTab(self.tab_clients, "👥 Clientes Monitorados")
        self.tabs.addTab(self.tab_transactions, "💳 Transações & Fraude")
        self.tabs.addTab(self.tab_rules, "🛡️ Regras de Detecção")
        self.tabs.addTab(self.tab_alerts, "🚨 Central de Alertas")

        card_layout.addLayout(top_layout)
        card_layout.addSpacing(15)
        card_layout.addWidget(self.tabs)

        main_layout.addWidget(card)

    def atualizar_usuario_logado(self, user_data=None):
        """Atualiza o banner com as informações do cliente logado."""
        user = user_data or api.current_user or {}
        if user:
            nome = user.get("name", "Cliente")
            cpf = CpfValidator.format_cpf(user.get("cpf", ""))
            cidade = user.get("usual_city", "")
            self.user_chip.setText(f"Usuário Ativo: <b>{nome}</b> (CPF: {cpf}) | Cidade Habitual: {cidade}")
        else:
            self.user_chip.setText("Conectado ao Backend em http://127.0.0.1:8000")

    def fazer_logout(self):
        """Limpa a sessão e retorna à tela de login."""
        api.logout()
        self.switch_to_login.emit()

    # ========================================================================
    # ABA 1: CLIENTES
    # ========================================================================
    def init_tab_clients(self):
        layout = QVBoxLayout(self.tab_clients)
        layout.setContentsMargins(15, 15, 15, 15)

        header = QHBoxLayout()
        desc = QLabel("Gerenciamento e Perfil de Clientes Monitorados:")
        desc.setObjectName("FieldLabel")

        self.btn_add_client = QPushButton("+ Novo Cliente")
        self.btn_add_client.setObjectName("LoginButton")
        self.btn_add_client.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_add_client.setFixedWidth(150)
        self.btn_add_client.clicked.connect(self.abrir_dialogo_adicionar_cliente)

        header.addWidget(desc)
        header.addStretch()
        header.addWidget(self.btn_add_client)

        self.table_clients = QTableWidget(0, 8)
        self.table_clients.setObjectName("GlassTable")
        self.table_clients.setHorizontalHeaderLabels([
            "ID", "Nome", "CPF", "Renda Mensal", "Cidade Habitual", "Horário Habitual", "Status", "Ações"
        ])
        self.table_clients.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.table_clients.verticalHeader().setDefaultSectionSize(44)
        self.table_clients.verticalHeader().setVisible(False)
        self.table_clients.setColumnWidth(0, 45)
        self.table_clients.setColumnWidth(2, 115)
        self.table_clients.setColumnWidth(3, 105)
        self.table_clients.setColumnWidth(4, 115)
        self.table_clients.setColumnWidth(5, 110)
        self.table_clients.setColumnWidth(6, 75)
        self.table_clients.setColumnWidth(7, 225)

        layout.addLayout(header)
        layout.addSpacing(8)
        layout.addWidget(self.table_clients)

    def abrir_dialogo_adicionar_cliente(self):
        dialog = ClientFormDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.carregar_clientes()

    def abrir_dialogo_editar_cliente(self, client_data):
        dialog = ClientFormDialog(self, client_data=client_data)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.carregar_clientes()

    def alternar_status_cliente(self, client_data):
        novo_status = not client_data.get("active", True)
        cid = client_data["id"]
        payload = {
            "name": client_data["name"],
            "cpf": client_data["cpf"],
            "monthly_income": float(client_data["monthly_income"]),
            "usual_city": client_data["usual_city"],
            "usual_start_time": client_data["usual_start_time"],
            "usual_end_time": client_data["usual_end_time"],
            "active": novo_status,
        }
        success, res = api.update_client(cid, payload)
        if success:
            self.carregar_clientes()
        else:
            QMessageBox.critical(self, "Erro", f"Não foi possível alterar status do cliente:\n{res}")

    def excluir_cliente(self, client_data):
        cid = client_data["id"]
        nome = client_data.get("name", "")
        resp = QMessageBox.question(
            self,
            "Confirmar Exclusão",
            f"Deseja realmente excluir o cliente #{cid} ({nome})?\n\n"
            "Atenção: clientes que possuem transações vinculadas não podem ser excluídos fisicamente.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if resp == QMessageBox.StandardButton.Yes:
            success, res = api.delete_client(cid)
            if success:
                QMessageBox.information(self, "Sucesso", "Cliente excluído com sucesso!")
                self.carregar_clientes()
            else:
                QMessageBox.critical(
                    self,
                    "Não Foi Possível Excluir",
                    f"{res}\n\n"
                    "Dica da Regra de Negócio: Em vez de excluir, utilize a opção 'Desativar' para manter a integridade do histórico financeiro.",
                )

    # ========================================================================
    # ABA 2: TRANSAÇÕES
    # ========================================================================
    def init_tab_transactions(self):
        layout = QVBoxLayout(self.tab_transactions)
        layout.setContentsMargins(15, 15, 15, 15)

        header = QHBoxLayout()
        header.setSpacing(10)

        lbl_filtro = QLabel("Filtrar por Classificação:")
        lbl_filtro.setObjectName("FieldLabel")

        self.filtro_classif = QComboBox()
        self.filtro_classif.setObjectName("InputField")
        self.filtro_classif.addItems(["TODAS", "NORMAL", "ATTENTION", "SUSPICIOUS"])
        self.filtro_classif.currentTextChanged.connect(self.carregar_transacoes)

        self.btn_add_trans = QPushButton("+ Nova Transação")
        self.btn_add_trans.setObjectName("LoginButton")
        self.btn_add_trans.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_add_trans.setFixedWidth(160)
        self.btn_add_trans.clicked.connect(self.abrir_dialogo_nova_transacao)

        header.addWidget(lbl_filtro)
        header.addWidget(self.filtro_classif)
        header.addStretch()
        header.addWidget(self.btn_add_trans)

        self.table_trans = QTableWidget(0, 10)
        self.table_trans.setObjectName("GlassTable")
        self.table_trans.setHorizontalHeaderLabels([
            "ID", "Cliente ID", "Valor", "Tipo", "Destino", "Localidade", "Data/Hora", "Score de Risco", "Classificação", "Ações"
        ])
        self.table_trans.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeMode.Stretch)
        self.table_trans.verticalHeader().setDefaultSectionSize(44)
        self.table_trans.verticalHeader().setVisible(False)
        self.table_trans.setColumnWidth(0, 45)
        self.table_trans.setColumnWidth(1, 70)
        self.table_trans.setColumnWidth(2, 100)
        self.table_trans.setColumnWidth(3, 80)
        self.table_trans.setColumnWidth(5, 110)
        self.table_trans.setColumnWidth(6, 125)
        self.table_trans.setColumnWidth(7, 75)
        self.table_trans.setColumnWidth(8, 100)
        self.table_trans.setColumnWidth(9, 180)

        layout.addLayout(header)
        layout.addSpacing(8)
        layout.addWidget(self.table_trans)

    def abrir_dialogo_nova_transacao(self):
        default_id = api.current_user.get("id") if api.current_user else None
        dialog = TransactionCreateDialog(self, default_client_id=default_id)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.carregar_transacoes()
            self.carregar_alertas()

    def ver_detalhes_transacao(self, tx_data):
        dialog = TransactionAlertsDialog(self, tx_data=tx_data)
        dialog.exec()

    def excluir_transacao(self, tx_data):
        tid = tx_data["id"]
        resp = QMessageBox.question(
            self,
            "Confirmar Exclusão",
            f"Deseja realmente excluir a transação #{tid}?\nTodos os alertas associados também serão removidos.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if resp == QMessageBox.StandardButton.Yes:
            success, res = api.delete_transaction(tid)
            if success:
                QMessageBox.information(self, "Sucesso", "Transação excluída!")
                self.carregar_transacoes()
                self.carregar_alertas()
            else:
                QMessageBox.critical(self, "Erro", f"Não foi possível excluir a transação:\n{res}")

    # ========================================================================
    # ABA 3: REGRAS
    # ========================================================================
    def init_tab_rules(self):
        layout = QVBoxLayout(self.tab_rules)
        layout.setContentsMargins(15, 15, 15, 15)

        header = QHBoxLayout()
        desc = QLabel("Regras Ativas do Motor de Anomalias Financeiras:")
        desc.setObjectName("FieldLabel")

        self.btn_add_rule = QPushButton("+ Nova Regra")
        self.btn_add_rule.setObjectName("LoginButton")
        self.btn_add_rule.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_add_rule.setFixedWidth(150)
        self.btn_add_rule.clicked.connect(self.abrir_dialogo_nova_regra)

        header.addWidget(desc)
        header.addStretch()
        header.addWidget(self.btn_add_rule)

        self.table_rules = QTableWidget(0, 8)
        self.table_rules.setObjectName("GlassTable")
        self.table_rules.setHorizontalHeaderLabels([
            "ID", "Código", "Nome da Regra", "Peso (Pontos)", "Limite (Threshold)", "Janela (min)", "Status", "Ações"
        ])
        self.table_rules.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        self.table_rules.verticalHeader().setDefaultSectionSize(44)
        self.table_rules.verticalHeader().setVisible(False)
        self.table_rules.setColumnWidth(0, 45)
        self.table_rules.setColumnWidth(1, 140)
        self.table_rules.setColumnWidth(3, 80)
        self.table_rules.setColumnWidth(4, 80)
        self.table_rules.setColumnWidth(5, 80)
        self.table_rules.setColumnWidth(6, 75)
        self.table_rules.setColumnWidth(7, 225)

        layout.addLayout(header)
        layout.addSpacing(8)
        layout.addWidget(self.table_rules)

    def abrir_dialogo_nova_regra(self):
        dialog = RuleFormDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.carregar_regras()

    def abrir_dialogo_editar_regra(self, rule_data):
        dialog = RuleFormDialog(self, rule_data=rule_data)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.carregar_regras()

    def alternar_status_regra(self, rule_data):
        novo_status = not rule_data.get("active", True)
        rid = rule_data["id"]
        payload = {
            "name": rule_data["name"],
            "description": rule_data.get("description"),
            "weight": rule_data["weight"],
            "threshold": rule_data.get("threshold"),
            "window_minutes": rule_data.get("window_minutes"),
            "active": novo_status,
        }
        success, res = api.update_rule(rid, payload)
        if success:
            self.carregar_regras()
        else:
            QMessageBox.critical(self, "Erro", f"Não foi possível alterar status da regra:\n{res}")

    def excluir_regra(self, rule_data):
        rid = rule_data["id"]
        resp = QMessageBox.question(
            self,
            "Confirmar Exclusão",
            f"Deseja excluir a regra #{rid} ({rule_data.get('code')})?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if resp == QMessageBox.StandardButton.Yes:
            success, res = api.delete_rule(rid)
            if success:
                QMessageBox.information(self, "Sucesso", "Regra excluída!")
                self.carregar_regras()
            else:
                QMessageBox.critical(self, "Erro", f"Não foi possível excluir a regra:\n{res}")

    # ========================================================================
    # ABA 4: ALERTAS
    # ========================================================================
    def init_tab_alerts(self):
        layout = QVBoxLayout(self.tab_alerts)
        layout.setContentsMargins(15, 15, 15, 15)

        header = QHBoxLayout()
        desc = QLabel("Alertas de Inconsistência e Violações de Regras Gerados:")
        desc.setObjectName("FieldLabel")

        header.addWidget(desc)
        header.addStretch()

        self.table_alerts = QTableWidget(0, 6)
        self.table_alerts.setObjectName("GlassTable")
        self.table_alerts.setHorizontalHeaderLabels([
            "ID", "Transação ID", "Regra", "Pontos", "Motivo da Detecção", "Data/Hora"
        ])
        self.table_alerts.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeMode.Stretch)
        self.table_alerts.verticalHeader().setDefaultSectionSize(44)
        self.table_alerts.verticalHeader().setVisible(False)
        self.table_alerts.setColumnWidth(0, 50)
        self.table_alerts.setColumnWidth(1, 95)
        self.table_alerts.setColumnWidth(2, 160)
        self.table_alerts.setColumnWidth(3, 80)
        self.table_alerts.setColumnWidth(5, 130)

        layout.addLayout(header)
        layout.addSpacing(8)
        layout.addWidget(self.table_alerts)

    # ========================================================================
    # CARREGAMENTO DE DADOS (INTEGRAÇÃO COMPLETA COM BACKEND FASTAPI)
    # ========================================================================
    def carregar_dados_backend(self):
        """Atualiza todas as abas buscando dados frescos da API."""
        self.atualizar_usuario_logado()
        self.carregar_clientes()
        self.carregar_transacoes()
        self.carregar_regras()
        self.carregar_alertas()

    def carregar_clientes(self):
        success, clientes = api.list_clients(skip=0, limit=100)
        if not success:
            print(f"Erro ao carregar clientes: {clientes}")
            return

        self.table_clients.setRowCount(len(clientes))
        for row, cli in enumerate(clientes):
            self.table_clients.setItem(row, 0, QTableWidgetItem(str(cli.get("id", ""))))
            self.table_clients.setItem(row, 1, QTableWidgetItem(cli.get("name", "")))
            self.table_clients.setItem(row, 2, QTableWidgetItem(CpfValidator.format_cpf(cli.get("cpf", ""))))
            self.table_clients.setItem(row, 3, QTableWidgetItem(format_currency(cli.get("monthly_income"))))
            self.table_clients.setItem(row, 4, QTableWidgetItem(cli.get("usual_city", "")))

            ini = cli.get("usual_start_time", "")[:5]
            fim = cli.get("usual_end_time", "")[:5]
            self.table_clients.setItem(row, 5, QTableWidgetItem(f"{ini} às {fim}"))

            ativo = cli.get("active", True)
            status_item = QTableWidgetItem("Ativo" if ativo else "Inativo")
            status_item.setForeground(QColor("#10b981" if ativo else "#ef4444"))
            self.table_clients.setItem(row, 6, status_item)

            # Ações
            actions_widget = QWidget()
            act_layout = QHBoxLayout(actions_widget)
            act_layout.setContentsMargins(6, 2, 6, 2)
            act_layout.setSpacing(6)
            act_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

            btn_edit = criar_botao_acao("Editar", "blue", lambda _, c=cli: self.abrir_dialogo_editar_cliente(c))
            btn_toggle = criar_botao_acao(
                "Desativar" if ativo else "Ativar",
                "amber" if ativo else "green",
                lambda _, c=cli: self.alternar_status_cliente(c)
            )
            btn_del = criar_botao_acao("Excluir", "red", lambda _, c=cli: self.excluir_cliente(c))

            act_layout.addWidget(btn_edit)
            act_layout.addWidget(btn_toggle)
            act_layout.addWidget(btn_del)
            self.table_clients.setCellWidget(row, 7, actions_widget)

    def carregar_transacoes(self):
        classif = self.filtro_classif.currentText()
        success, transacoes = api.list_transactions(classification=classif, skip=0, limit=100)
        if not success:
            print(f"Erro ao carregar transações: {transacoes}")
            return

        self.table_trans.setRowCount(len(transacoes))
        for row, tx in enumerate(transacoes):
            self.table_trans.setItem(row, 0, QTableWidgetItem(str(tx.get("id", ""))))
            self.table_trans.setItem(row, 1, QTableWidgetItem(str(tx.get("client_id", ""))))
            self.table_trans.setItem(row, 2, QTableWidgetItem(format_currency(tx.get("amount"))))
            self.table_trans.setItem(row, 3, QTableWidgetItem(str(tx.get("transaction_type", ""))))
            self.table_trans.setItem(row, 4, QTableWidgetItem(str(tx.get("destination", ""))))
            self.table_trans.setItem(row, 5, QTableWidgetItem(str(tx.get("location", ""))))
            self.table_trans.setItem(row, 6, QTableWidgetItem(format_datetime(tx.get("occurred_at"))))

            score = tx.get("risk_score", 0)
            score_item = QTableWidgetItem(f"{score}/100")
            self.table_trans.setItem(row, 7, score_item)

            c = tx.get("classification", "NORMAL")
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

            font = class_item.font()
            font.setBold(True)
            class_item.setFont(font)
            score_item.setFont(font)
            self.table_trans.setItem(row, 8, class_item)

            # Ações
            actions_widget = QWidget()
            act_layout = QHBoxLayout(actions_widget)
            act_layout.setContentsMargins(6, 2, 6, 2)
            act_layout.setSpacing(6)
            act_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

            btn_alerts = criar_botao_acao("Ver Alertas", "purple", lambda _, t=tx: self.ver_detalhes_transacao(t))
            btn_del = criar_botao_acao("Excluir", "red", lambda _, t=tx: self.excluir_transacao(t))

            act_layout.addWidget(btn_alerts)
            act_layout.addWidget(btn_del)
            self.table_trans.setCellWidget(row, 9, actions_widget)

    def carregar_regras(self):
        success, regras = api.list_rules(skip=0, limit=100)
        if not success:
            print(f"Erro ao carregar regras: {regras}")
            return

        self.table_rules.setRowCount(len(regras))
        for row, r in enumerate(regras):
            self.table_rules.setItem(row, 0, QTableWidgetItem(str(r.get("id", ""))))
            self.table_rules.setItem(row, 1, QTableWidgetItem(str(r.get("code", ""))))
            self.table_rules.setItem(row, 2, QTableWidgetItem(str(r.get("name", ""))))
            self.table_rules.setItem(row, 3, QTableWidgetItem(f"{r.get('weight', 0)} pts"))

            th = r.get("threshold")
            self.table_rules.setItem(row, 4, QTableWidgetItem(str(th) if th is not None else "-"))

            w = r.get("window_minutes")
            self.table_rules.setItem(row, 5, QTableWidgetItem(f"{w} min" if w else "-"))

            ativo = r.get("active", True)
            status_item = QTableWidgetItem("Ativa" if ativo else "Inativa")
            status_item.setForeground(QColor("#10b981" if ativo else "#ef4444"))
            self.table_rules.setItem(row, 6, status_item)

            # Ações
            actions_widget = QWidget()
            act_layout = QHBoxLayout(actions_widget)
            act_layout.setContentsMargins(6, 2, 6, 2)
            act_layout.setSpacing(6)
            act_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

            btn_edit = criar_botao_acao("Editar", "blue", lambda _, reg=r: self.abrir_dialogo_editar_regra(reg))
            btn_toggle = criar_botao_acao(
                "Desativar" if ativo else "Ativar",
                "amber" if ativo else "green",
                lambda _, reg=r: self.alternar_status_regra(reg)
            )
            btn_del = criar_botao_acao("Excluir", "red", lambda _, reg=r: self.excluir_regra(reg))

            act_layout.addWidget(btn_edit)
            act_layout.addWidget(btn_toggle)
            act_layout.addWidget(btn_del)
            self.table_rules.setCellWidget(row, 7, actions_widget)

    def carregar_alertas(self):
        success, alertas = api.list_alerts(skip=0, limit=100)
        if not success:
            print(f"Erro ao carregar alertas: {alertas}")
            return

        self.table_alerts.setRowCount(len(alertas))
        for row, al in enumerate(alertas):
            self.table_alerts.setItem(row, 0, QTableWidgetItem(str(al.get("id", ""))))
            self.table_alerts.setItem(row, 1, QTableWidgetItem(str(al.get("transaction_id", ""))))
            self.table_alerts.setItem(row, 2, QTableWidgetItem(str(al.get("rule_code", ""))))

            pts_item = QTableWidgetItem(f"+{al.get('points', 0)} pts")
            pts_item.setForeground(QColor("#ef4444"))
            self.table_alerts.setItem(row, 3, pts_item)

            self.table_alerts.setItem(row, 4, QTableWidgetItem(str(al.get("reason", ""))))
            self.table_alerts.setItem(row, 5, QTableWidgetItem(format_datetime(al.get("created_at"))))
