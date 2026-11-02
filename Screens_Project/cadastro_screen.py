import os
import re
import sys
from PyQt6.QtCore import Qt, pyqtSignal, QTime
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
    QTimeEdit,
    QScrollArea,
)

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from client_api import api
from utils import CpfValidator


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
        main_layout.setContentsMargins(20, 20, 20, 20)

        card = QWidget(self)
        card.setFixedSize(540, 720)
        card.setObjectName("GlassCard")

        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(40)
        shadow.setColor(QColor(0, 0, 0, 60))
        shadow.setOffset(0, 12)
        card.setGraphicsEffect(shadow)

        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(35, 25, 35, 25)

        title_label = QLabel("Criar Conta")
        title_label.setObjectName("TitleLabel")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        subtitle_label = QLabel("Cadastre seu perfil financeiro para monitoramento")
        subtitle_label.setObjectName("SubtitleLabel")
        subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        form_layout = QGridLayout()
        form_layout.setVerticalSpacing(8)
        form_layout.setHorizontalSpacing(14)

        # Nome
        nome_label = QLabel("Nome Completo *")
        nome_label.setObjectName("FieldLabel")
        self.nome_input = QLineEdit()
        self.nome_input.setObjectName("InputField")
        self.nome_input.setPlaceholderText("Ex: Maria de Souza")
        form_layout.addWidget(nome_label, 0, 0, 1, 2)
        form_layout.addWidget(self.nome_input, 1, 0, 1, 2)

        # CPF
        cpf_label = QLabel("CPF *")
        cpf_label.setObjectName("FieldLabel")
        self.cpf_input = QLineEdit()
        self.cpf_input.setObjectName("InputField")
        self.cpf_input.setPlaceholderText("000.000.000-00")
        form_layout.addWidget(cpf_label, 2, 0)
        form_layout.addWidget(self.cpf_input, 3, 0)

        # Senha
        senha_label = QLabel("Senha (mínimo 6 dígitos) *")
        senha_label.setObjectName("FieldLabel")
        self.senha_input = QLineEdit()
        self.senha_input.setObjectName("InputField")
        self.senha_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.senha_input.setPlaceholderText("••••••••")
        form_layout.addWidget(senha_label, 2, 1)
        form_layout.addWidget(self.senha_input, 3, 1)

        # Renda Mensal
        renda_label = QLabel("Renda Mensal Estimada (R$) *")
        renda_label.setObjectName("FieldLabel")
        self.renda_input = QLineEdit()
        self.renda_input.setObjectName("InputField")
        self.renda_input.setPlaceholderText("Ex: 5000.00")
        form_layout.addWidget(renda_label, 4, 0)
        form_layout.addWidget(self.renda_input, 5, 0)

        # Cidade Habitual
        cidade_label = QLabel("Cidade Habitual de Operação *")
        cidade_label.setObjectName("FieldLabel")
        self.cidade_input = QLineEdit()
        self.cidade_input.setObjectName("InputField")
        self.cidade_input.setPlaceholderText("Ex: Rio de Janeiro")
        form_layout.addWidget(cidade_label, 4, 1)
        form_layout.addWidget(self.cidade_input, 5, 1)

        # Horário Início Habitual
        hora_ini_label = QLabel("Horário Inicial Habitual *")
        hora_ini_label.setObjectName("FieldLabel")
        self.hora_ini_input = QTimeEdit()
        self.hora_ini_input.setObjectName("InputField")
        self.hora_ini_input.setTime(QTime(8, 0))
        self.hora_ini_input.setDisplayFormat("HH:mm")
        form_layout.addWidget(hora_ini_label, 6, 0)
        form_layout.addWidget(self.hora_ini_input, 7, 0)

        # Horário Fim Habitual
        hora_fim_label = QLabel("Horário Final Habitual *")
        hora_fim_label.setObjectName("FieldLabel")
        self.hora_fim_input = QTimeEdit()
        self.hora_fim_input.setObjectName("InputField")
        self.hora_fim_input.setTime(QTime(18, 0))
        self.hora_fim_input.setDisplayFormat("HH:mm")
        form_layout.addWidget(hora_fim_label, 6, 1)
        form_layout.addWidget(self.hora_fim_input, 7, 1)

        # Botões
        self.btn_cadastrar = QPushButton("Finalizar Cadastro")
        self.btn_cadastrar.setObjectName("LoginButton")
        self.btn_cadastrar.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_cadastrar.clicked.connect(self.realizar_cadastro)

        self.btn_voltar = QPushButton("Já possui conta? Voltar ao Login")
        self.btn_voltar.setObjectName("LinkButton")
        self.btn_voltar.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_voltar.clicked.connect(self.switch_to_login.emit)

        card_layout.addWidget(title_label)
        card_layout.addWidget(subtitle_label)
        card_layout.addSpacing(10)
        card_layout.addLayout(form_layout)
        card_layout.addSpacing(18)
        card_layout.addWidget(self.btn_cadastrar)
        card_layout.addSpacing(8)
        card_layout.addWidget(self.btn_voltar, alignment=Qt.AlignmentFlag.AlignCenter)

        main_layout.addWidget(card)

    def realizar_cadastro(self):
        nome = self.nome_input.text().strip()
        raw_cpf = self.cpf_input.text().strip()
        senha = self.senha_input.text().strip()
        renda_text = self.renda_input.text().strip().replace("R$", "").replace(".", "").replace(",", ".")
        cidade = self.cidade_input.text().strip()
        hora_ini = self.hora_ini_input.time().toString("HH:mm:ss")
        hora_fim = self.hora_fim_input.time().toString("HH:mm:ss")

        # Validações prévias no cliente
        if not nome or not raw_cpf or not senha or not renda_text or not cidade:
            QMessageBox.warning(self, "Aviso", "Por favor, preencha todos os campos obrigatórios!")
            return

        if len(nome) < 3:
            QMessageBox.warning(self, "Aviso", "O nome completo deve conter pelo menos 3 caracteres.")
            return

        if not CpfValidator.is_valid(raw_cpf):
            QMessageBox.warning(self, "CPF Inválido", "O CPF informado não é válido. Verifique os dígitos informados.")
            return

        if len(senha) < 6:
            QMessageBox.warning(self, "Senha Fraca", "A senha de acesso deve possuir pelo menos 6 caracteres.")
            return

        try:
            renda_val = float(renda_text)
            if renda_val <= 0:
                raise ValueError()
        except ValueError:
            QMessageBox.warning(self, "Renda Inválida", "Informe uma renda mensal válida superior a R$ 0,00.")
            return

        if len(cidade) < 2:
            QMessageBox.warning(self, "Cidade Inválida", "Informe a cidade habitual de operação.")
            return

        cpf_norm = CpfValidator.normalize(raw_cpf)

        payload = {
            "name": nome,
            "cpf": cpf_norm,
            "password": senha,
            "monthly_income": renda_val,
            "usual_city": cidade,
            "usual_start_time": hora_ini,
            "usual_end_time": hora_fim,
        }

        self.btn_cadastrar.setEnabled(False)
        self.btn_cadastrar.setText("Cadastrando...")

        try:
            success, result = api.create_client(payload)
            if success:
                QMessageBox.information(
                    self,
                    "Sucesso!",
                    "Cliente cadastrado com sucesso no sistema!\n\n"
                    "Agora você já pode realizar o login utilizando seu CPF e senha.",
                )
                self.limpar_formulario()
                self.switch_to_login.emit()
            else:
                QMessageBox.critical(
                    self,
                    "Erro ao Cadastrar",
                    f"Não foi possível concluir o cadastro:\n\n{result}",
                )
        except Exception as e:
            QMessageBox.critical(self, "Erro Inesperado", f"Ocorreu um erro inesperado:\n{str(e)}")
        finally:
            self.btn_cadastrar.setEnabled(True)
            self.btn_cadastrar.setText("Finalizar Cadastro")

    def limpar_formulario(self):
        self.nome_input.clear()
        self.cpf_input.clear()
        self.senha_input.clear()
        self.renda_input.clear()
        self.cidade_input.clear()
        self.hora_ini_input.setTime(QTime(8, 0))
        self.hora_fim_input.setTime(QTime(18, 0))
