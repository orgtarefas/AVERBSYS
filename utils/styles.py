def get_login_styles():
    return """
    QWidget {
        background-color: #f5f6fa;
        font-family: 'Segoe UI', Arial, sans-serif;
    }
    
    QLabel#title {
        font-size: 28px;
        font-weight: bold;
        color: #2c3e50;
        margin-bottom: 10px;
    }
    
    QLabel#subtitle {
        font-size: 16px;
        color: #7f8c8d;
        margin-bottom: 20px;
    }
    
    QFrame#formFrame {
        background-color: white;
        border-radius: 10px;
        padding: 30px;
        border: 1px solid #ddd;
    }
    
    QLineEdit#inputField {
        padding: 12px;
        border: 2px solid #ecf0f1;
        border-radius: 6px;
        font-size: 14px;
        background-color: #fafbfc;
    }
    
    QLineEdit#inputField:focus {
        border-color: #3498db;
        background-color: white;
    }
    
    QPushButton#loginButton {
        background-color: #27ae60;
        color: white;
        border: none;
        padding: 12px;
        border-radius: 6px;
        font-size: 14px;
        font-weight: bold;
    }
    
    QPushButton#loginButton:hover {
        background-color: #219a52;
    }
    
    QPushButton#loginButton:disabled {
        background-color: #bdc3c7;
    }
    
    QPushButton#sobreButton {
        background-color: transparent;
        border: none;
        padding: 0px;
    }
    
    QPushButton#sobreButton:hover {
        opacity: 0.7;
    }

    /* Estilo para o botão de mostrar/ocultar senha */
    QPushButton#togglePasswordButton {
        background-color: transparent;
        border: none;
        padding: 5px;
        margin-left: 2px;
    }
    
    QPushButton#togglePasswordButton:hover {
        background-color: #f0f0f0;
        border-radius: 3px;
    }
    
    QPushButton#togglePasswordButton:pressed {
        background-color: #e0e0e0;
    }
    
    /* Estilo para o checkbox de lembrar senha */
    QCheckBox#rememberCheckbox {
        color: #555555;
        font-size: 12px;
        spacing: 5px;
    }
    
    QCheckBox#rememberCheckbox::indicator {
        width: 16px;
        height: 16px;
    }
    
    QCheckBox#rememberCheckbox::indicator:unchecked {
        border: 1px solid #cccccc;
        background-color: white;
        border-radius: 2px;
    }
    
    QCheckBox#rememberCheckbox::indicator:checked {
        border: 1px solid #3498db;
        background-color: #3498db;
        border-radius: 2px;
        image: url(assets/checkmark.png);
    }
    
    QCheckBox#rememberCheckbox::indicator:unchecked:hover {
        border: 1px solid #3498db;
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
    
    /* Header Styles */
    QFrame#header {
        background-color: white;
        padding: 15px;
        border-radius: 8px;
        border: 1px solid #dadce0;
        border-bottom: 2px solid #3498db;
    }
    
    QLabel#welcomeLabel {
        font-size: 14px;
        font-weight: bold;
        color: #2c3e50;
    }

    QLabel#sistemaNome {
        font-size: 18px;
        font-weight: bold;
        color: #2c3e50;
        padding: 5px;
    }
    
    QLabel#sistemaVersao {
        font-size: 10px;
        color: #7f8c8d;
        font-weight: normal;
    }
    
    /* Button Styles */
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
    
    #primaryButton {
        background-color: #1a73e8;
        color: white;
        border: none;
        padding: 8px 16px;
        border-radius: 4px;
        font-size: 14px;
        font-weight: bold;
    }
    
    #primaryButton:hover {
        background-color: #1669d6;
    }
    
    #primaryButton:disabled {
        background-color: #cccccc;
        color: #666666;
        border: 1px solid #aaaaaa;
    }
    
    /* BOTÕES APROVAR E RECUSAR - ESTADO INATIVO */
    #successButton:disabled {
        background-color: #cccccc;
        color: #666666;
        border: 1px solid #aaaaaa;
        padding: 12px 20px;
        border-radius: 6px;
        font-size: 14px;
        font-weight: bold;
    }
    
    #dangerButton:disabled {
        background-color: #cccccc;
        color: #666666;
        border: 1px solid #aaaaaa;
        padding: 12px 20px;
        border-radius: 6px;
        font-size: 14px;
        font-weight: bold;
    }
    
    /* BOTÕES APROVAR E RECUSAR - ESTADO ATIVO */
    #successButton:enabled {
        background-color: #28a745;
        color: white;
        border: none;
        padding: 12px 20px;
        border-radius: 6px;
        font-size: 14px;
        font-weight: bold;
    }
    
    #successButton:enabled:hover {
        background-color: #218838;
    }
    
    #dangerButton:enabled {
        background-color: #dc3545;
        color: white;
        border: none;
        padding: 12px 20px;
        border-radius: 6px;
        font-size: 14px;
        font-weight: bold;
    }
    
    #dangerButton:enabled:hover {
        background-color: #c82333;
    }
    
    #secondaryButton {
        background-color: #6c757d;
        color: white;
        border: none;
        padding: 8px 16px;
        border-radius: 4px;
        font-size: 14px;
    }
    
    #secondaryButton:hover {
        background-color: #5a6268;
    }
    
    #secondaryButton:disabled {
        background-color: #cccccc;
        color: #666666;
        border: 1px solid #aaaaaa;
    }
    
    /* Form Styles */
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
    
    #subtitleLabel {
        font-size: 14px;
        font-weight: bold;
        color: #495057;
        margin-bottom: 10px;
    }
    
    #inputField {
        padding: 10px;
        border: 2px solid #dadce0;
        border-radius: 6px;
        font-size: 14px;
        margin-bottom: 15px;
    }
    
    #inputField:focus {
        border-color: #1a73e8;
    }
    
    #comboField {
        padding: 8px;
        border: 2px solid #ddd;
        border-radius: 5px;
        background-color: white;
        font-size: 14px;
        min-width: 150px;
    }
    
    #comboField:focus {
        border-color: #1a73e8;
    }
    
    #comboField:disabled {
        background-color: #f5f5f5;
        color: #999;
    }
    
    /* Info and Warning Labels */
    #infoLabel {
        font-size: 12px;
        color: #6c757d;
        font-style: italic;
    }
    
    .warningLabel {
        color: #ff9800;
        font-size: 12px;
        font-weight: bold;
        padding: 5px;
        background-color: #fff3e0;
        border-radius: 3px;
    }
    
    /* Checkbox Styles */
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
    
    QCheckBox:disabled {
        color: #999999;
    }
    
    QCheckBox::indicator:disabled {
        border: 2px solid #cccccc;
        background-color: #f5f5f5;
    }
    
    /* Table Styles */
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
    
    /* Tab Styles */
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
    
    /* Date Edit Styles */
    QDateEdit {
        padding: 8px;
        border: 2px solid #ddd;
        border-radius: 5px;
        background-color: white;
        font-size: 14px;
    }
    
    QDateEdit::drop-down {
        subcontrol-origin: padding;
        subcontrol-position: top right;
        width: 25px;
        border-left-width: 1px;
        border-left-color: #ddd;
        border-left-style: solid;
    }
    
    /* ComboBox Styles */
    QComboBox {
        padding: 8px;
        border: 2px solid #ddd;
        border-radius: 5px;
        background-color: white;
        font-size: 14px;
        min-width: 150px;
    }
    
    QComboBox::drop-down {
        subcontrol-origin: padding;
        subcontrol-position: top right;
        width: 25px;
        border-left-width: 1px;
        border-left-color: #ddd;
        border-left-style: solid;
    }
    
    QComboBox QAbstractItemView {
        border: 1px solid #ddd;
        background-color: white;
        selection-background-color: #4CAF50;
        selection-color: white;
    }
    
    /* Scroll Area */
    QScrollArea {
        border: 1px solid #dadce0;
        border-radius: 6px;
        background-color: white;
    }
    
    QScrollBar:vertical {
        border: none;
        background-color: #f8f9fa;
        width: 12px;
        margin: 0px;
    }
    
    QScrollBar::handle:vertical {
        background-color: #c1c1c1;
        border-radius: 6px;
        min-height: 20px;
    }
    
    QScrollBar::handle:vertical:hover {
        background-color: #a8a8a8;
    }
    
    /* Group Box */
    QGroupBox {
        font-weight: bold;
        border: 1px solid #dadce0;
        border-radius: 6px;
        margin-top: 10px;
        padding-top: 10px;
    }
    
    QGroupBox::title {
        subcontrol-origin: margin;
        subcontrol-position: top center;
        padding: 0 8px;
        background-color: white;
    }
    
    /* User Info Label */
    QLabel#userInfoLabel {
        color: #2c3e50;
        font-weight: bold;
        padding: 5px 10px;
        background-color: #ecf0f1;
        border-radius: 4px;
    }
    """