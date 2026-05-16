# ============================================
# MÓDULO DE FALTA - WEB VERSION
# ============================================

from ..core.database import Database

def listar_falta():
    """Retorna lista de produtos em falta"""
    return Database.carregar_faltas()

def adicionar_falta(descricao: str) -> bool:
    """Adiciona produto à lista de falta"""
    faltas = Database.carregar_faltas()
    descricao = descricao.lower().strip()
    
    if not descricao or descricao in faltas:
        return False
    
    faltas.append(descricao)
    return Database.salvar_faltas(faltas)

def remover_falta(descricao: str) -> bool:
    """Remove produto da lista de falta"""
    faltas = Database.carregar_faltas()
    descricao = descricao.lower().strip()
    
    if descricao not in faltas:
        return False
    
    faltas.remove(descricao)
    return Database.salvar_faltas(faltas)

def limpar_faltas() -> bool:
    """Limpa toda a lista de faltas"""
    return Database.salvar_faltas([])

def produto_esta_em_falta(descricao: str, faltas: list) -> bool:
    """Verifica se um produto está na lista de faltas"""
    return descricao.lower() in [f.lower() for f in faltas]