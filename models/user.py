from dataclasses import dataclass
from datetime import datetime

@dataclass
class User:
    login: str
    senha: str
    perfil: str
    status: str = "Ativo"
    nome_completo: str = ""
    data_cadastro: str = None
    
    def __post_init__(self):
        if self.data_cadastro is None:
            self.data_cadastro = datetime.now().strftime("%Y-%m-%d %H:%M:%S")