import sys
import os
import traceback
from datetime import datetime, timedelta
from PyQt5.QtWidgets import QApplication, QMessageBox
from PyQt5.QtCore import Qt

def verificar_validade_sistema():
    """Verifica se o sistema está dentro do período de validade"""
    try:
        # Data de expiração do sistema (ajuste conforme necessário)
        data_expiracao = datetime(2025, 11, 20)  
        
        data_atual = datetime.now()
        
        if data_atual > data_expiracao:
            QMessageBox.critical(
                None,
                "Sistema Expirado",
                f"O sistema expirou em {data_expiracao.strftime('%d/%m/%Y')}.\n\n"
                "Entre em contato com o suporte para renovação."
            )
            return False
        
        # Verificar se está próximo da expiração (3 dias antes)
        dias_para_expirar = (data_expiracao - data_atual).days
        if dias_para_expirar <= 3:
            QMessageBox.warning(
                None,
                "Aviso de Expiração",
                f"O sistema expirará em {dias_para_expirar} dias.\n"
                f"Data de expiração: {data_expiracao.strftime('%d/%m/%Y')}\n\n"
                "Entre em contato com o suporte para renovação."
            )
        
        return True
        
    except Exception as e:
        print(f"Erro ao verificar validade: {e}")
        return True  # Em caso de erro, permite continuar

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
    app.setApplicationName(" ")
    
    try:
        # Verificar validade do sistema antes de iniciar
        if not verificar_validade_sistema():
            sys.exit(1)
        
        # Criar controller principal
        from controllers.auth_controller import AuthController
        auth_controller = AuthController()
        auth_controller.show_login()
        
        sys.exit(app.exec_())
        
    except Exception as e:
        print(f"Error starting application: {e}")
        sys.exit(1)
       
if __name__ == "__main__":
    main()