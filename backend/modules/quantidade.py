# ============================================
# MÓDULO DE ADIÇÃO DE QUANTIDADE - WEB VERSION
# ============================================
from datetime import date
from typing import Optional
from ..core.database import Database
from ..core.models import Produto

def adicionar_quantidade(ean: str, setor: Optional[str], mes: int, ano: int, quantidade: int) -> tuple:
    """
    Adiciona quantidade de um produto existente
    Retorna (sucesso, mensagem)
    """
    if quantidade <= 0:
        return False, "Quantidade deve ser maior que zero"
    
    db = Database()
    todos_produtos = db.carregar_produtos()
    
    # Verifica se o produto existe
    produto_original = None
    for p in todos_produtos:
        if p.ean == ean and p.setor == setor:
            produto_original = p
            break
    
    if not produto_original:
        return False, "Produto não encontrado neste setor"
    
    # Cria data de validade (primeiro dia do mês)
    data_validade = date(ano, mes, 1)
    
    # Adiciona as unidades
    novos_produtos = []
    for i in range(quantidade):
        novos_produtos.append(Produto(
            ean=ean,
            descricao=produto_original.descricao,
            validade=data_validade,
            status='ativo',
            setor=setor
        ))
    
    if db.salvar_produtos(todos_produtos + novos_produtos):
        return True, f"{quantidade} unidade(s) adicionada(s) com sucesso"
    else:
        return False, "Erro ao salvar no banco de dados"