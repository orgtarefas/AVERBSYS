def get_login_styles():
    return """
    QWidget {
        background-color: #f0f2f5;
        font-family: 'Segoe UI', Arial, sans-serif;
    }
    
    #title {
        font-size: 28px;
        font-weight: bold;
        color: #1a73e8;
        padding: 20px;
    }
    
    #formFrame {
        background-color: white;
        border-radius: 10px;
        padding: 30px;
        border: 1px solid #dadce0;
    }
    
    QLabel {
        font-size: 14px;
        color: #5f6368;
        font-weight: 500;
    }
    
    #inputField {
        padding: 12px;
        border: 2px solid #dadce0;
        border-radius: 6px;
        font-size: 14px;
        background-color: white;
    }
    
    #inputField:focus {
        border-color: #1a73e8;
    }
    
    #loginButton {
        background-color: #1a73e8;
        color: white;
        border: none;
        padding: 12px;
        border-radius: 6px;
        font-size: 14px;
        font-weight: bold;
    }
    
    #loginButton:hover {
        background-color: #1669d6;
    }
    
    #loginButton:disabled {
        background-color: #cccccc;
    }
    
    #registerButton {
        background-color: transparent;
        color: #1a73e8;
        border: 1px solid #dadce0;
        padding: 12px;
        border-radius: 6px;
        font-size: 14px;
    }
    
    #registerButton:hover {
        background-color: #f8f9fa;
    }
    """

def get_home_styles():
    return """
    QWidget {
        background-color: #f8f9fa;
        font-family: 'Segoe UI', Arial, sans-serif;
    }
    
    #header {
        background-color: white;
        padding: 15px;
        border-radius: 8px;
        border: 1px solid #dadce0;
    }
    
    #welcomeLabel {
        font-size: 24px;
        font-weight: bold;
        color: #1a73e8;
    }
    
    #logoutButton {
        background-color: #dc3545;
        color: white;
        border: none;
        padding: 8px 16px;
        border-radius: 4px;
        font-size: 14px;
    }
    
    #logoutButton:hover {
        background-color: #c82333;
    }
    
    #infoFrame {
        background-color: white;
        padding: 20px;
        border-radius: 8px;
        border: 1px solid #dadce0;
    }
    
    #contentLabel {
        font-size: 18px;
        color: #5f6368;
        padding: 40px;
    }
    """

def get_register_styles():
    return """
    QWidget {
        background-color: #f0f2f5;
        font-family: 'Segoe UI', Arial, sans-serif;
    }
    
    #title {
        font-size: 24px;
        font-weight: bold;
        color: #1a73e8;
        padding: 20px;
    }
    
    #formFrame {
        background-color: white;
        border-radius: 10px;
        padding: 30px;
        border: 1px solid #dadce0;
    }
    
    QLabel {
        font-size: 14px;
        color: #5f6368;
        font-weight: 500;
    }
    
    #inputField, #comboBox {
        padding: 12px;
        border: 2px solid #dadce0;
        border-radius: 6px;
        font-size: 14px;
        background-color: white;
    }
    
    #inputField:focus, #comboBox:focus {
        border-color: #1a73e8;
    }
    
    #registerButton {
        background-color: #28a745;
        color: white;
        border: none;
        padding: 12px;
        border-radius: 6px;
        font-size: 14px;
        font-weight: bold;
    }
    
    #registerButton:hover {
        background-color: #218838;
    }
    
    #registerButton:disabled {
        background-color: #cccccc;
    }
    
    #backButton {
        background-color: #6c757d;
        color: white;
        border: none;
        padding: 12px;
        border-radius: 6px;
        font-size: 14px;
    }
    
    #backButton:hover {
        background-color: #5a6268;
    }
    """

def get_propostas_styles():
    return """
    QWidget {
        background-color: #f8f9fa;
        font-family: 'Segoe UI', Arial, sans-serif;
    }
    
    #header {
        background-color: white;
        padding: 15px;
        border-radius: 8px;
        border: 1px solid #dadce0;
    }
    
    #welcomeLabel {
        font-size: 18px;
        font-weight: bold;
        color: #1a73e8;
    }
    
    #logoutButton {
        background-color: #dc3545;
        color: white;
        border: none;
        padding: 8px 16px;
        border-radius: 4px;
        font-size: 14px;
    }
    
    #logoutButton:hover {
        background-color: #c82333;
    }
    
    #formFrame {
        background-color: white;
        border-radius: 8px;
        padding: 20px;
        border: 1px solid #dadce0;
    }
    
    #titleLabel {
        font-size: 16px;
        font-weight: bold;
        color: #1a73e8;
        margin-bottom: 15px;
    }
    
    #inputField, #comboBox {
        padding: 10px;
        border: 2px solid #dadce0;
        border-radius: 6px;
        font-size: 14px;
        margin-bottom: 15px;
    }
    
    #inputField:focus, #comboBox:focus {
        border-color: #1a73e8;
    }
    
    #primaryButton {
        background-color: #1a73e8;
        color: white;
        border: none;
        padding: 12px;
        border-radius: 6px;
        font-size: 14px;
        font-weight: bold;
    }
    
    #primaryButton:hover {
        background-color: #1669d6;
    }
    
    #primaryButton:disabled {
        background-color: #cccccc;
    }
    
    QTableWidget {
        background-color: white;
        border: 1px solid #dadce0;
        border-radius: 6px;
    }
    
    QTableWidget::item {
        padding: 8px;
        border-bottom: 1px solid #f0f0f0;
    }
    
    QHeaderView::section {
        background-color: #f8f9fa;
        padding: 10px;
        border: none;
        font-weight: bold;
    }
    
    QTabWidget::pane {
        border: 1px solid #dadce0;
        border-radius: 6px;
        background-color: white;
    }
    
    QTabBar::tab {
        background-color: #f8f9fa;
        padding: 10px 20px;
        margin-right: 2px;
        border: 1px solid #dadce0;
        border-bottom: none;
        border-top-left-radius: 4px;
        border-top-right-radius: 4px;
    }
    
    QTabBar::tab:selected {
        background-color: white;
        border-bottom: 2px solid #1a73e8;
    }


    # ... outros estilos existentes ...

    # Novos estilos para checkboxes e botões específicos
    QCheckBox {
        spacing: 8px;
        font-size: 14px;
        padding: 5px;
    }

    QCheckBox::indicator {
        width: 18px;
        height: 18px;
    }

    QCheckBox::indicator:unchecked {
        border: 2px solid #dadce0;
        border-radius: 3px;
        background-color: white;
    }

    QCheckBox::indicator:checked {
        border: 2px solid #1a73e8;
        border-radius: 3px;
        background-color: #1a73e8;
    }

    #successButton {
        background-color: #28a745;
        color: white;
        border: none;
        padding: 12px 20px;
        border-radius: 6px;
        font-size: 14px;
        font-weight: bold;
    }

    #successButton:hover {
        background-color: #218838;
    }

    #dangerButton {
        background-color: #dc3545;
        color: white;
        border: none;
        padding: 12px 20px;
        border-radius: 6px;
        font-size: 14px;
        font-weight: bold;
    }

    #dangerButton:hover {
        background-color: #c82333;
    }

    #secondaryButton {
        background-color: #6c757d;
        color: white;
        border: none;
        padding: 10px 15px;
        border-radius: 6px;
        font-size: 14px;
    }

    #secondaryButton:hover {
        background-color: #5a6268;
    }

    #infoLabel {
        font-size: 12px;
        color: #6c757d;
        font-style: italic;
    }

    #subtitleLabel {
        font-size: 14px;
        font-weight: bold;
        color: #495057;
        margin-bottom: 10px;
    }


    """

