# ============================================
# CLASSES DE DADOS - SETOR OPCIONAL
# ============================================
from dataclasses import dataclass
from datetime import date, datetime
from typing import Optional

@dataclass
class Produto:
    """Representa um produto no sistema"""
    ean: str
    descricao: str
    validade: date
    status: str = 'ativo'
    setor: Optional[str] = None  # MODIFICADO: agora pode ser None
    data_cadastro: date = None
    
    def __post_init__(self):
        if not self.ean or not self.ean.strip():
            raise ValueError("EAN não pode ser vazio")
        if not self.descricao or not self.descricao.strip():
            raise ValueError("Descrição não pode ser vazia")
        if self.data_cadastro is None:
            self.data_cadastro = date.today()
    
    @property
    def mes_ano(self) -> str:
        return self.validade.strftime("%m/%Y")
    
    @property
    def dias_para_vencer(self) -> int:
        hoje = date.today()
        return (self.validade - hoje).days
    
    @property
    def esta_vencido(self) -> bool:
        hoje = date.today()
        return hoje >= self.validade
    
    @property
    def esta_prestes(self, dias_limite: int = 90) -> bool:
        dias = self.dias_para_vencer
        return not self.esta_vencido and 0 < dias <= dias_limite
    
    @classmethod
    def from_mes_ano(cls, ean: str, descricao: str, mes: int, ano: int, 
                     status: str = 'ativo', setor: Optional[str] = None, 
                     data_cadastro: date = None):
        data_validade = date(ano, mes, 1)
        return cls(ean, descricao, data_validade, status, setor, data_cadastro)