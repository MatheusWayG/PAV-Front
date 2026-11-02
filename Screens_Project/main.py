import os
import sys
from PyQt6.QtWidgets import QApplication, QStackedWidget

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from login_screen import GlassLoginWindow
from cadastro_screen import CadastroWindow
from creditos_screen import CreditosWindow
from main_dashboard import MainDashboardWindow
from Profile_Screen import ProfileWindow
from anomalies_screen import AnomaliesWindow
from transaction_screen import TransactionWindow
from settings_screen import SettingsWindow


class MainWindow(QStackedWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PAV - Sistema Integrado de Detecção de Anomalias Financeiras")
        self.showMaximized()

        # Instanciação de todas as telas do sistema
        self.login_screen = GlassLoginWindow()
        self.cadastro_screen = CadastroWindow()
        self.creditos_screen = CreditosWindow()
        self.dashboard_screen = MainDashboardWindow()
        self.profile_screen = ProfileWindow()
        self.anomalies_screen = AnomaliesWindow()
        self.transaction_screen = TransactionWindow()
        self.settings_screen = SettingsWindow()

        # Adiciona ao QStackedWidget
        # Índices:
        # 0 = Login
        # 1 = Cadastro
        # 2 = Créditos
        # 3 = Dashboard
        # 4 = Perfil
        # 5 = Anomalias
        # 6 = Simulador de Transações
        # 7 = Configurações
        self.addWidget(self.login_screen)         # 0
        self.addWidget(self.cadastro_screen)      # 1
        self.addWidget(self.creditos_screen)      # 2
        self.addWidget(self.dashboard_screen)     # 3
        self.addWidget(self.profile_screen)       # 4
        self.addWidget(self.anomalies_screen)     # 5
        self.addWidget(self.transaction_screen)   # 6
        self.addWidget(self.settings_screen)      # 7

        # Conexões de Navegação e Fluxo de Estado
        self.login_screen.switch_to_signin.connect(lambda: self.setCurrentIndex(1))
        self.login_screen.switch_to_creditos.connect(lambda: self.setCurrentIndex(2))
        self.login_screen.login_successful.connect(self._ao_efetuar_login)

        self.cadastro_screen.switch_to_login.connect(lambda: self.setCurrentIndex(0))
        self.creditos_screen.switch_to_login.connect(lambda: self.setCurrentIndex(0))

        self.dashboard_screen.switch_to_login.connect(lambda: self.setCurrentIndex(0))
        self.dashboard_screen.switch_to_profile.connect(self._navegar_para_perfil)
        self.dashboard_screen.switch_to_settings.connect(lambda: self.setCurrentIndex(7))

        self.profile_screen.switch_to_dashboard.connect(lambda: self.setCurrentIndex(3))
        self.anomalies_screen.switch_to_dashboard.connect(lambda: self.setCurrentIndex(3))
        self.transaction_screen.switch_to_dashboard.connect(lambda: self.setCurrentIndex(3))
        self.settings_screen.switch_to_dashboard.connect(lambda: self.setCurrentIndex(3))

        # Estilo Global Compartilhado (Glassmorphism Moderno)
        self.setStyleSheet("""
            QWidget#GlassCard {
                background-color: rgba(255, 255, 255, 0.12);
                border: 1px solid rgba(255, 255, 255, 0.25);
                border-radius: 20px;
            }
            QLabel#TitleLabel {
                color: #ffffff;
                font-size: 26px;
                font-weight: bold;
                font-family: 'Segoe UI', sans-serif;
            }
            QLabel#SubtitleLabel {
                color: rgba(255, 255, 255, 0.85);
                font-size: 13px;
                font-family: 'Segoe UI', sans-serif;
                margin-bottom: 5px;
            }
            QLabel#FieldLabel, QLabel#DevLabel {
                color: rgba(255, 255, 255, 0.95);
                font-size: 13px;
                font-weight: 600;
                font-family: 'Segoe UI', sans-serif;
            }
            QLabel#DevLabel {
                font-size: 15px;
                font-weight: bold;
                color: #ffffff;
            }
            QLineEdit#InputField, QComboBox#InputField, QDateTimeEdit#InputField, QTimeEdit#InputField, QTextEdit#InputField {
                background-color: rgba(255, 255, 255, 0.18);
                border: 1px solid rgba(255, 255, 255, 0.35);
                border-radius: 12px;
                padding: 7px 12px;
                color: white;
                font-size: 13px;
                font-family: 'Segoe UI', sans-serif;
            }
            QLineEdit#InputField:focus, QComboBox#InputField:focus, QDateTimeEdit#InputField:focus, QTimeEdit#InputField:focus, QTextEdit#InputField:focus {
                background-color: rgba(255, 255, 255, 0.28);
                border: 1px solid #38bdf8;
            }
            QLineEdit#InputField::placeholder {
                color: rgba(255, 255, 255, 0.5);
            }
            QComboBox#InputField QAbstractItemView {
                background-color: #1e293b;
                color: white;
                selection-background-color: #3b82f6;
            }
            QPushButton#LoginButton {
                background-color: rgba(255, 255, 255, 0.92);
                color: #0f172a;
                font-size: 13px;
                font-weight: bold;
                border-radius: 12px;
                padding: 8px 16px;
                font-family: 'Segoe UI', sans-serif;
                border: none;
            }
            QPushButton#LoginButton:hover {
                background-color: #ffffff;
                color: #0284c7;
            }
            QPushButton#LoginButton:disabled {
                background-color: rgba(255, 255, 255, 0.4);
                color: rgba(15, 23, 42, 0.6);
            }
            QLabel#FooterLabel {
                color: rgba(255, 255, 255, 0.9);
                font-size: 12px;
                font-family: 'Segoe UI', sans-serif;
            }
            QPushButton#LinkButton {
                background: transparent;
                color: #ffffff;
                font-size: 12px;
                font-weight: bold;
                text-decoration: underline;
                border: none;
                font-family: 'Segoe UI', sans-serif;
                padding: 4px;
            }
            QPushButton#LinkButton:hover {
                color: #38bdf8;
            }
            QTabWidget::pane {
                border: 1px solid rgba(255, 255, 255, 0.2);
                border-radius: 12px;
                background-color: rgba(15, 23, 42, 0.45);
            }
            QTabBar::tab {
                background-color: rgba(255, 255, 255, 0.1);
                color: rgba(255, 255, 255, 0.85);
                padding: 9px 18px;
                margin-right: 4px;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                font-family: 'Segoe UI', sans-serif;
                font-weight: 600;
                font-size: 13px;
            }
            QTabBar::tab:selected {
                background-color: rgba(255, 255, 255, 0.28);
                color: #ffffff;
                border-bottom: 2px solid #38bdf8;
            }
            QTableWidget#GlassTable {
                background-color: rgba(15, 23, 42, 0.35);
                border: 1px solid rgba(255, 255, 255, 0.15);
                border-radius: 12px;
                color: #ffffff;
                gridline-color: rgba(255, 255, 255, 0.1);
                font-size: 12px;
            }
            QTableWidget#GlassTable::item {
                padding: 4px 6px;
            }
            QHeaderView::section {
                background-color: rgba(30, 41, 59, 0.85);
                color: white;
                padding: 7px;
                border: none;
                font-weight: bold;
                font-size: 12px;
            }
            QScrollBar:vertical {
                background: rgba(0, 0, 0, 0.2);
                width: 10px;
                margin: 0px;
                border-radius: 5px;
            }
            QScrollBar::handle:vertical {
                background: rgba(255, 255, 255, 0.3);
                min-height: 20px;
                border-radius: 5px;
            }
            QScrollBar::handle:vertical:hover {
                background: rgba(255, 255, 255, 0.5);
            }
        """)

    def _ao_efetuar_login(self, user_data):
        self.dashboard_screen.atualizar_usuario_logado(user_data)
        self.dashboard_screen.carregar_dados_backend()
        self.setCurrentIndex(3)

    def _navegar_para_perfil(self):
        self.profile_screen.carregar_perfil()
        self.setCurrentIndex(4)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
