import sys

from PySide6.QtWidgets import QApplication

from ui.main_window import MainWindow
from services.backup_service import criar_backup
from database import criar_banco
from criar_usuarios import criar_usuarios


def main():

    criar_usuarios()
    criar_banco()
    criar_backup()

    app = QApplication(sys.argv)

    janela = MainWindow()
    janela.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()