from datetime import datetime

class UserModel:
    def __init__(self, login, senha, perfil, nome_completo, status="Ativo"):
        self.login = login
        self.senha = senha
        self.perfil = perfil
        self.nome_completo = nome_completo
        self.status = status
        self.data_cadastro = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def to_dict(self):
        return {
            'login': self.login,
            'senha': self.senha,
            'perfil': self.perfil,
            'nome_completo': self.nome_completo,
            'status': self.status,
            'data_cadastro': self.data_cadastro
        }
    
    @staticmethod
    def from_dict(data):
        user = UserModel(
            data['login'],
            data['senha'],
            data['perfil'],
            data['nome_completo'],
            data.get('status', 'Ativo')
        )
        user.data_cadastro = data.get('data_cadastro', '')
        return user