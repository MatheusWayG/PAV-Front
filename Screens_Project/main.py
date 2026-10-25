import sys
from PyQt6.QtWidgets import QApplication, QStackedWidget
from login_screen import GlassLoginWindow
from cadastro_screen import CadastroWindow

class MainWindow(QStackedWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sistema - Login e Cadastro")
        self.showMaximized()

        # Instancia as telas dos arquivos separados
        self.login_screen = GlassLoginWindow()
        self.cadastro_screen = CadastroWindow()

        # Adiciona ao container de páginas (Stacked Widget)
        self.addWidget(self.login_screen)
        self.addWidget(self.cadastro_screen)

        # Conecta os sinais de navegação entre os arquivos
        self.login_screen.switch_to_signin.connect(lambda: self.setCurrentIndex(1))
        self.cadastro_screen.switch_to_login.connect(lambda: self.setCurrentIndex(0))

        # Estilização global compartilhada para os efeitos Glassmorphism
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
            QLabel#FieldLabel {
                color: rgba(255, 255, 255, 0.95);
                font-size: 12px;
                font-weight: 600;
                font-family: 'Segoe UI', sans-serif;
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
                color: #4f46e5;
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
                color: #e0e7ff;
            }
        """)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())