# ============================================
# MÓDULO DE ESTATÍSTICAS - WEB VERSION
# ============================================
from datetime import date
from typing import Optional
from ..core.database import Database
from ..core.config import DIAS_PRESTES
from .falta import produto_esta_em_falta
from .prestes import carregar_prestes_retirados

def get_estatisticas(setor: Optional[str] = None) -> dict:
    """Retorna estatísticas completas do setor"""
    db = Database()
    produtos = db.carregar_produtos(setor)
    faltas = Database.carregar_faltas()
    
    # Carrega prestes retirados
    prestes_retirados = carregar_prestes_retirados()
    eans_retirados = [p['ean'] for p in prestes_retirados if p.get('setor') == setor]
    
    hoje = date.today()
    
    # Contagens
    total = len(produtos)
    vencidos = 0
    prestes = 0
    ok = 0
    em_falta_count = 0
    retirados_count = 0
    
    # Listas para detalhes
    produtos_vencidos = []
    produtos_prestes = []
    produtos_em_falta = []
    
    for p in produtos:
        em_falta = produto_esta_em_falta(p.descricao, faltas)
        retirado = p.ean in eans_retirados
        
        if retirado:
            retirados_count += 1
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
    total_ativo = total - retirados_count
    
    return {
        'total': total_ativo,
        'ativos': total_ativo - em_falta_count,
        'em_falta': em_falta_count,
        'vencidos': vencidos,
        'prestes': prestes,
        'ok': ok,
        'prestes_retirados': retirados_count,
        'dias_prestes': DIAS_PRESTES,
        'lista_vencidos': produtos_vencidos[:10],
        'lista_prestes': produtos_prestes[:10],
        'lista_falta': produtos_em_falta[:10]
    }