# ============================================
# MÓDULO DE LISTAGEM - WEB VERSION
# ============================================
from datetime import date
from typing import Optional, List
from ..core.database import Database
from ..core.config import DIAS_PRESTES
from .falta import produto_esta_em_falta
from .prestes import carregar_prestes_retirados

def listar_produtos_ativos(setor: Optional[str] = None) -> List[dict]:
    """
    Lista apenas produtos que NÃO estão em falta
    e NÃO tiveram prestes retirados
    """
    db = Database()
    produtos = db.carregar_produtos(setor)
    faltas = Database.carregar_faltas()
    
    # Carrega prestes retirados
    prestes_retirados = carregar_prestes_retirados()
    eans_retirados = [p['ean'] for p in prestes_retirados if p.get('setor') == setor]
    
    produtos_ativos = []
    hoje = date.today()
    
    for p in produtos:
        em_falta = produto_esta_em_falta(p.descricao, faltas)
        prestes_retirado = p.ean in eans_retirados
        
        # Só inclui se não estiver em falta e não tiver prestes retirado
        if not em_falta and not prestes_retirado:
            produtos_ativos.append({
                'ean': p.ean,
                'descricao': p.descricao,
                'validade': p.mes_ano,
                'dias': p.dias_para_vencer,
                'status': 'vencido' if p.esta_vencido else 'prestes' if p.esta_prestes else 'ok'
            })
    
    return produtos_ativos

def listar_todos_produtos(setor: Optional[str] = None) -> List[dict]:
    """
    Lista TODOS os produtos (incluindo em falta)
    PRESTES RETIRADOS NÃO APARECEM MAIS NA LISTA
    """
    db = Database()
    produtos = db.carregar_produtos(setor)
    faltas = Database.carregar_faltas()
    
    prestes_retirados = carregar_prestes_retirados()
    eans_retirados = [p['ean'] for p in prestes_retirados if p.get('setor') == setor]
    
    lista = []
    hoje = date.today()
    
    for p in produtos:
        em_falta = produto_esta_em_falta(p.descricao, faltas)
        prestes_retirado = p.ean in eans_retirados
        
        # PRESTES RETIRADOS NÃO APARECEM MAIS NA LISTA
        if prestes_retirado:
            continue  # Pula completamente produtos com prestes retirados
        
        # Define status
        if em_falta:
            status_texto = "FALTA"
            status_class = "table-secondary"
        elif p.esta_vencido:
            status_texto = "VENCIDO"
            status_class = "table-danger"
        elif p.esta_prestes:
            status_texto = f"PRESTES ({p.dias_para_vencer})"
            status_class = "table-warning"
        else:
            status_texto = "OK"
            status_class = "table-success"
        
        lista.append({
            'ean': p.ean,
            'descricao': p.descricao,
            'validade': p.mes_ano,
            'dias': p.dias_para_vencer,
            'status': status_texto,
            'status_class': status_class
        })
    
    return lista