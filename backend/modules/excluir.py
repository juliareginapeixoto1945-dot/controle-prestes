# ============================================
# MÓDULO DE EXCLUSÃO - WEB VERSION
# ============================================
from typing import Optional
from ..core.database import Database
from ..core.models import Produto

def excluir_por_ean(ean: str, setor: Optional[str]) -> tuple:
    """
    Exclui produto por EAN
    Retorna (sucesso, mensagem, produto_excluido)
    """
    db = Database()
    todos_produtos = db.carregar_produtos()
    
    # Encontra produtos do setor com este EAN
    produtos_setor = [p for p in todos_produtos if p.ean == ean and p.setor == setor]
    
    if not produtos_setor:
        return False, "Produto não encontrado neste setor", None
    
    produto = produtos_setor[0]
    
    # Remove apenas deste setor
    novos_produtos = [p for p in todos_produtos if not (p.ean == ean and p.setor == setor)]
    
    if db.salvar_produtos(novos_produtos):
        return True, "Produto excluído com sucesso", produto
    else:
        return False, "Erro ao excluir produto", None

def excluir_por_descricao(termo: str, setor: Optional[str]) -> tuple:
    """
    Exclui produtos por descrição (busca parcial)
    Retorna (sucesso, mensagem, quantidade, produtos)
    """
    db = Database()
    todos_produtos = db.carregar_produtos()
    termo = termo.lower()
    
    # Encontra produtos do setor que contêm o termo
    produtos_setor = [p for p in todos_produtos if p.setor == setor and termo in p.descricao.lower()]
    
    if not produtos_setor:
        return False, "Nenhum produto encontrado", 0, []
    
    # Remove todos encontrados
    eans_remover = [(p.ean, p.setor) for p in produtos_setor]
    novos_produtos = [p for p in todos_produtos if (p.ean, p.setor) not in eans_remover]
    
    if db.salvar_produtos(novos_produtos):
        return True, f"{len(produtos_setor)} produto(s) excluído(s)", len(produtos_setor), produtos_setor
    else:
        return False, "Erro ao excluir produtos", 0, []

def excluir_todos_setor(setor: str) -> tuple:
    """
    Exclui TODOS os produtos do setor
    Retorna (sucesso, mensagem, quantidade)
    """
    db = Database()
    todos_produtos = db.carregar_produtos()
    
    produtos_setor = [p for p in todos_produtos if p.setor == setor]
    
    if not produtos_setor:
        return False, "Setor vazio", 0
    
    novos_produtos = [p for p in todos_produtos if p.setor != setor]
    
    if db.salvar_produtos(novos_produtos):
        return True, f"{len(produtos_setor)} produto(s) excluído(s) do setor {setor}", len(produtos_setor)
    else:
        return False, "Erro ao excluir produtos", 0