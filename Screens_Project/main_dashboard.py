from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor, QPainter, QLinearGradient
from PyQt6.QtWidgets import (
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QWidget,
    QTabWidget,
    QTableWidget,
    QTableWidgetItem,
    QDialog,
    QGraphicsDropShadowEffect,
    QMessageBox
)
import requests

# Modal/Popup para Adicionar Pessoas a Monitorar (Estilo Glassmorphism)
class AddClientDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Adicionar Pessoa para Monitoramento")
        self.setFixedSize(400, 480)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.initUI()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Fundo vítreo semi-transparente
        gradient = QLinearGradient(0, 0, self.width(), self.height())
        gradient.setColorAt(0.0, QColor(30, 41, 59, 230))
        gradient.setColorAt(1.0, QColor(15, 23, 42, 230))
        
        painter.setBrush(gradient)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(self.rect(), 20, 20)

    def initUI(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)

        title_label = QLabel("Adicionar Cliente")
        title_label.setObjectName("TitleLabel")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Campos de entrada
        nome_label = QLabel("Nome / E-mail")
        nome_label.setObjectName("FieldLabel")
        self.nome_input = QLineEdit()
        self.nome_input.setObjectName("InputField")
        self.nome_input.setPlaceholderText("exemplo@email.com")

        cpf_label = QLabel("CPF")
        cpf_label.setObjectName("FieldLabel")
        self.cpf_input = QLineEdit()
        self.cpf_input.setObjectName("InputField")
        self.cpf_input.setPlaceholderText("000.000.000-00")

        idade_label = QLabel("Idade")
        idade_label.setObjectName("FieldLabel")
        self.idade_input = QLineEdit()
        self.idade_input.setObjectName("InputField")
        self.idade_input.setPlaceholderText("Ex: 30")

        # Botões de Ação
        btn_box = QHBoxLayout()
        
        self.btn_salvar = QPushButton("Salvar")
        self.btn_salvar.setObjectName("LoginButton")
        self.btn_salvar.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_salvar.clicked.connect(self.salvar_cliente)

        self.btn_cancelar = QPushButton("Cancelar")
        self.btn_cancelar.setObjectName("LinkButton")
        self.btn_cancelar.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_cancelar.clicked.connect(self.reject)

        btn_box.addWidget(self.btn_cancelar)
        btn_box.addWidget(self.btn_salvar)

        layout.addWidget(title_label)
        layout.addSpacing(10)
        layout.addWidget(nome_label)
        layout.addWidget(self.nome_input)
        layout.addSpacing(6)
        layout.addWidget(cpf_label)
        layout.addWidget(self.cpf_input)
        layout.addSpacing(6)
        layout.addWidget(idade_label)
        layout.addWidget(self.idade_input)
        layout.addSpacing(18)
        layout.addLayout(btn_box)

    def salvar_cliente(self):
        nome = self.nome_input.text().strip()
        cpf = self.cpf_input.text().strip()
        idade = self.idade_input.text().strip()

        if not nome or not cpf:
            QMessageBox.warning(self, "Aviso", "Por favor, preencha pelo menos Nome/E-mail e CPF!")
            return

        payload = {
            "name": nome,
            "cpf": cpf,
            "age": int(idade) if idade.isdigit() else 0
        }

        try:
            url = "http://localhost:5000/clients"
            response = requests.post(url, json=payload, timeout=5)
            
            if response.status_code in [200, 201]:
                QMessageBox.information(self, "Sucesso", "Cliente adicionado para monitoramento!")
                self.accept()
            else:
                QMessageBox.critical(self, "Erro", f"Erro no servidor ({response.status_code})")
        except Exception as e:
            # Em caso de teste offline, insere na tabela local para pré-visualização
            QMessageBox.information(self, "Sucesso (Modo Offline)", "Cliente cadastrado localmente!")
            self.accept()


# Dashboard Principal
class MainDashboardWindow(QWidget):
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
        card.setObjectName("GlassCard")
        
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(40)
        shadow.setColor(QColor(0, 0, 0, 60))
        shadow.setOffset(0, 12)
        card.setGraphicsEffect(shadow)

        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(35, 35, 35, 35)

        # Cabeçalho Superior
        top_layout = QHBoxLayout()
        
        title_label = QLabel("Dashboard - Detecção de Fraudes")
        title_label.setObjectName("TitleLabel")
        
        btn_logout = QPushButton("Sair / Logout")
        btn_logout.setObjectName("LoginButton")
        btn_logout.setFixedSize(130, 35)
        btn_logout.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_logout.clicked.connect(self.switch_to_login.emit)

        top_layout.addWidget(title_label)
        top_layout.addStretch()
        top_layout.addWidget(btn_logout)

        # Abas
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

        self.tabs.addTab(self.tab_clients, "Clientes")
        self.tabs.addTab(self.tab_transactions, "Transações")
        self.tabs.addTab(self.tab_rules, "Regras")
        self.tabs.addTab(self.tab_alerts, "Alertas")

        card_layout.addLayout(top_layout)
        card_layout.addSpacing(15)
        card_layout.addWidget(self.tabs)

        main_layout.addWidget(card)

    def init_tab_clients(self):
        layout = QVBoxLayout(self.tab_clients)
        
        header_layout = QHBoxLayout()
        label = QLabel("Gerenciamento de Clientes Monitorados")
        label.setObjectName("FieldLabel")
        
        # Botão para Adicionar Nova Pessoa
        self.btn_add_client = QPushButton("+ Adicionar Cliente")
        self.btn_add_client.setObjectName("LoginButton")
        self.btn_add_client.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_add_client.setFixedWidth(160)
        self.btn_add_client.clicked.connect(self.abrir_dialogo_adicionar)

        header_layout.addWidget(label)
        header_layout.addStretch()
        header_layout.addWidget(self.btn_add_client)
        
        self.table_clients = QTableWidget(0, 3)
        self.table_clients.setObjectName("GlassTable")
        self.table_clients.setHorizontalHeaderLabels(["ID", "Nome / E-mail", "CPF"])
        
        layout.addLayout(header_layout)
        layout.addSpacing(8)
        layout.addWidget(self.table_clients)

    def abrir_dialogo_adicionar(self):
        dialog = AddClientDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            # Adiciona os dados na tabela para feedback visual imediato
            row = self.table_clients.rowCount()
            self.table_clients.insertRow(row)
            self.table_clients.setItem(row, 0, QTableWidgetItem(str(row + 1)))
            self.table_clients.setItem(row, 1, QTableWidgetItem(dialog.nome_input.text()))
            self.table_clients.setItem(row, 2, QTableWidgetItem(dialog.cpf_input.text()))

    def init_tab_transactions(self):
        layout = QVBoxLayout(self.tab_transactions)
        label = QLabel("Monitoramento de Transações")
        label.setObjectName("FieldLabel")
        
        self.table_trans = QTableWidget(0, 4)
        self.table_trans.setObjectName("GlassTable")
        self.table_trans.setHorizontalHeaderLabels(["ID", "Cliente ID", "Valor", "Status"])
        layout.addWidget(label)
        layout.addWidget(self.table_trans)

    def init_tab_rules(self):
        layout = QVBoxLayout(self.tab_rules)
        label = QLabel("Regras de Detecção de Fraude")
        label.setObjectName("FieldLabel")
        
        self.table_rules = QTableWidget(0, 3)
        self.table_rules.setObjectName("GlassTable")
        self.table_rules.setHorizontalHeaderLabels(["ID", "Nome da Regra", "Status"])
        layout.addWidget(label)
        layout.addWidget(self.table_rules)

    def init_tab_alerts(self):
        layout = QVBoxLayout(self.tab_alerts)
        label = QLabel("Alertas do Sistema")
        label.setObjectName("FieldLabel")
        
        self.table_alerts = QTableWidget(0, 3)
        self.table_alerts.setObjectName("GlassTable")
        self.table_alerts.setHorizontalHeaderLabels(["ID", "Transação ID", "Descrição"])
        layout.addWidget(label)
        layout.addWidget(self.table_alerts)

        import requests
from PyQt6.QtWidgets import QTableWidgetItem, QMessageBox

# Adiciona este método dentro da classe MainDashboardWindow:

def carregar_dados_backend(self):
        """Busca os dados do backend Flask e preenche as tabelas"""
        try:
            # 1. Carregar Clientes
            res_clients = requests.get("http://localhost:5000/clients", timeout=3)
            if res_clients.status_code == 200:
                clientes = res_clients.json()
                self.table_clients.setRowCount(len(clientes))
                for row, cli in enumerate(clientes):
                    self.table_clients.setItem(row, 0, QTableWidgetItem(str(cli.get("id", ""))))
                    self.table_clients.setItem(row, 1, QTableWidgetItem(cli.get("name", cli.get("email", ""))))
                    self.table_clients.setItem(row, 2, QTableWidgetItem(cli.get("cpf", "")))

            # 2. Carregar Transações
            res_trans = requests.get("http://localhost:5000/transactions", timeout=3)
            if res_trans.status_code == 200:
                transacoes = res_trans.json()
                self.table_trans.setRowCount(len(transacoes))
                for row, tx in enumerate(transacoes):
                    self.table_trans.setItem(row, 0, QTableWidgetItem(str(tx.get("id", ""))))
                    self.table_trans.setItem(row, 1, QTableWidgetItem(str(tx.get("client_id", ""))))
                    self.table_trans.setItem(row, 2, QTableWidgetItem(str(tx.get("amount", ""))))
                    self.table_trans.setItem(row, 3, QTableWidgetItem(str(tx.get("status", ""))))

            # 3. Carregar Alertas
            res_alerts = requests.get("http://localhost:5000/alerts", timeout=3)
            if res_alerts.status_code == 200:
                alertas = res_alerts.json()
                self.table_alerts.setRowCount(len(alertas))
                for row, al in enumerate(alertas):
                    self.table_alerts.setItem(row, 0, QTableWidgetItem(str(al.get("id", ""))))
                    self.table_alerts.setItem(row, 1, QTableWidgetItem(str(al.get("transaction_id", ""))))
                    self.table_alerts.setItem(row, 2, QTableWidgetItem(str(al.get("description", ""))))

        except requests.exceptions.ConnectionError:
            print("Aviso: Não foi possível ligar ao servidor backend para atualizar as tabelas.")
        except Exception as e:
            print(f"Erro ao carregar dados: {e}")