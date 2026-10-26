import sys
from PyQt6.QtWidgets import QApplication, QStackedWidget
from login_screen import GlassLoginWindow
from cadastro_screen import CadastroWindow
from creditos_screen import CreditosWindow
from main_dashboard import MainDashboardWindow

class MainWindow(QStackedWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sistema - Login, Cadastro e Créditos")
        self.showMaximized()

        # Instancia as telas
        self.dashboard_screen = MainDashboardWindow()
        self.login_screen = GlassLoginWindow()
        self.cadastro_screen = CadastroWindow()
        self.creditos_screen = CreditosWindow()

        # Adiciona ao QStackedWidget (Índices: 0 = Login, 1 = Cadastro, 2 = Créditos, 3 = Dashboard)
        self.addWidget(self.login_screen)
        self.addWidget(self.cadastro_screen)
        self.addWidget(self.creditos_screen)
        self.addWidget(self.dashboard_screen)

        # Conecta as transições de navegação
        self.login_screen.switch_to_signin.connect(lambda: self.setCurrentIndex(1))
        self.login_screen.switch_to_creditos.connect(lambda: self.setCurrentIndex(2))
        self.login_screen.btn_entrar.clicked.connect(lambda: self.setCurrentIndex(3))

        self.cadastro_screen.switch_to_login.connect(lambda: self.setCurrentIndex(0))
        self.creditos_screen.switch_to_login.connect(lambda: self.setCurrentIndex(0))
        self.dashboard_screen.switch_to_login.connect(lambda: self.setCurrentIndex(0))

        # Estilização global compartilhada para os elementos de texto e cartões
        self.setStyleSheet("""
            QWidget#GlassCard {
                background-color: rgba(255, 255, 255, 0.12);
                border: 1px solid rgba(255, 255, 255, 0.3);
                border-radius: 24px;
            }
            QLabel#TitleLabel {
                color: #ffffff;
                font-size: 30px;
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
                font-size: 14px;
                font-weight: 600;
                font-family: 'Segoe UI', sans-serif;
            }
            QLabel#DevLabel {
                font-size: 16px;
                font-weight: bold;
                color: #ffffff;
            }
            QLineEdit#InputField {
                background-color: rgba(255, 255, 255, 0.2);
                border: 1px solid rgba(255, 255, 255, 0.35);
                border-radius: 18px;
                padding: 8px 16px;
                color: white;
                font-size: 13px;
                font-family: 'Segoe UI', sans-serif;
            }
            QLineEdit#InputField:focus {
                background-color: rgba(255, 255, 255, 0.3);
                border: 1px solid rgba(255, 255, 255, 0.8);
            }
            QLineEdit#InputField::placeholder {
                color: rgba(255, 255, 255, 0.5);
            }
            QPushButton#LoginButton {
                background-color: rgba(255, 255, 255, 0.9);
                color: #065f46;
                font-size: 14px;
                font-weight: bold;
                border-radius: 18px;
                padding: 10px;
                font-family: 'Segoe UI', sans-serif;
            }
            QPushButton#LoginButton:hover {
                background-color: #ffffff;
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
            }
            QPushButton#LinkButton:hover {
                color: #d1fae5;
            }
            /* ... (seus estilos anteriores de GlassCard, TitleLabel, InputField, etc.) ... */

            QTabWidget::pane {
                border: 1px solid rgba(255, 255, 255, 0.2);
                border-radius: 12px;
                background-color: rgba(255, 255, 255, 0.05);
    }
            QTabBar::tab {
                background-color: rgba(255, 255, 255, 0.1);
                color: rgba(255, 255, 255, 0.8);
                padding: 8px 16px;
                margin-right: 4px;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                font-family: 'Segoe UI', sans-serif;
                font-weight: 600;
    }
            QTabBar::tab:selected {
                background-color: rgba(255, 255, 255, 0.25);
                color: #ffffff;
    }
            QTableWidget#GlassTable {
                background-color: rgba(255, 255, 255, 0.1);
                border: 1px solid rgba(255, 255, 255, 0.2);
                border-radius: 12px;
                color: #ffffff;
                gridline-color: rgba(255, 255, 255, 0.15);
    }
            QHeaderView::section {
                background-color: rgba(255, 255, 255, 0.2);
                color: white;
                padding: 6px;
                border: none;
                font-weight: bold;
    }
""")

        

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())