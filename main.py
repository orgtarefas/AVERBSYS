import sys
import os
import traceback
from PyQt5.QtWidgets import QApplication, QMessageBox
from PyQt5.QtCore import Qt
from controllers.auth_controller import AuthController

def excepthook(exctype, value, tb):
    """Handler global de exceções"""
    error_msg = ''.join(traceback.format_exception(exctype, value, tb))
    print(f"Uncaught exception: {error_msg}")
    
    # Mostrar mensagem de erro para o usuário
    msg = QMessageBox()
    msg.setIcon(QMessageBox.Critical)
    msg.setText("Ocorreu um erro inesperado")
    msg.setInformativeText(str(value))
    msg.setWindowTitle("Erro")
    msg.setDetailedText(error_msg)
    msg.exec_()

def main():
    # Configurar handler global de exceções
    sys.excepthook = excepthook
    
    # Configurar high DPI
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    
    app = QApplication(sys.argv)
    app.setApplicationName("ABERBSYS")
    
    try:
        # Criar controller principal
        auth_controller = AuthController()
        auth_controller.show_login()
        
        sys.exit(app.exec_())
    except Exception as e:
        print(f"Error starting application: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()