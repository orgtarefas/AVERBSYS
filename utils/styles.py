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