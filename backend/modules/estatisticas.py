# ============================================
# MÓDULO DE ESTATÍSTICAS - WEB VERSION
# ============================================

from datetime import date
from ..core.database import Database
from ..core.config import DIAS_PRESTES
from .falta import produto_esta_em_falta
from .prestes import carregar_prestes_retirados

def get_estatisticas(setor: str = None):
    """Retorna estatísticas completas do setor"""
    db = Database()
    produtos = db.carregar_produtos(setor)
    faltas = Database.carregar_faltas()
    
    # Carrega prestes retirados
    prestes_retirados = carregar_prestes_retirados()
    eans_retirados = [p['ean'] for p in prestes_retirados if p['setor'] == setor]
    
    hoje = date.today()
    
    # Contagens
    total = len(produtos)
    vencidos = 0
    prestes = 0
    ok = 0
    em_falta_count = 0
    prestes_retirados_count = 0
    
    # Listas para detalhes
    produtos_vencidos = []
    produtos_prestes = []
    produtos_em_falta = []
    
    for p in produtos:
        em_falta = produto_esta_em_falta(p.descricao, faltas)
        prestes_retirado = p.ean in eans_retirados
        
        if prestes_retirado:
            prestes_retirados_count += 1
            # Não conta nas outras categorias
            continue
        
        if em_falta:
            em_falta_count += 1
            produtos_em_falta.append({
                'ean': p.ean,
                'descricao': p.descricao,
                'validade': p.mes_ano,
                'dias': p.dias_para_vencer
            })
        
        if p.esta_vencido:
            vencidos += 1
            if not em_falta:
                produtos_vencidos.append({
                    'ean': p.ean,
                    'descricao': p.descricao,
                    'validade': p.mes_ano,
                    'dias': p.dias_para_vencer
                })
        elif p.esta_prestes:
            prestes += 1
            if not em_falta:
                produtos_prestes.append({
                    'ean': p.ean,
                    'descricao': p.descricao,
                    'validade': p.mes_ano,
                    'dias': p.dias_para_vencer
                })
        else:
            if not em_falta:
                ok += 1
    
    # Ordenar por urgência
    produtos_prestes.sort(key=lambda x: x['dias'])
    produtos_vencidos.sort(key=lambda x: x['dias'])
    
    # Total ativo (sem contar retirados)
    total_ativo = total - prestes_retirados_count
    
    return {
        'total': total_ativo,  # Total não inclui retirados
        'ativos': total_ativo - em_falta_count,
        'em_falta': em_falta_count,
        'vencidos': vencidos,
        'prestes': prestes,
        'ok': ok,
        'prestes_retirados': prestes_retirados_count,
        'dias_prestes': DIAS_PRESTES,
        'lista_vencidos': produtos_vencidos[:10],
        'lista_prestes': produtos_prestes[:10],
        'lista_falta': produtos_em_falta[:10]
    }