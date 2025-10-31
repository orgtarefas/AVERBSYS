from PyQt5.QtCore import QObject

class UserController(QObject):
    def __init__(self, db_manager):
        super().__init__()
        self.db_manager = db_manager
    
    def validate_user_exists(self, login, nome_completo):
        return self.db_manager.user_exists(login, nome_completo)