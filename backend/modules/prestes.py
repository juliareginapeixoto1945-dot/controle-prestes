# ============================================
# MÓDULO DE PRODUTOS PRESTES A VENCER - VERSÃO FINAL
# ============================================
import json
from datetime import date
from pathlib import Path
from typing import List, Dict, Optional
from ..core.config import DATA_DIR

ARQUIVO_PRESTES_RETIRADOS = DATA_DIR / "prestes_retirados.json"

def carregar_prestes_retirados() -> list:
    """Carrega a lista de produtos que já tiveram os prestes retirados"""
    if ARQUIVO_PRESTES_RETIRADOS.exists():
        try:
            with open(ARQUIVO_PRESTES_RETIRADOS, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return []
    return []

def salvar_prestes_retirados(lista: list):
    """Salva a lista de produtos que tiveram os prestes retirados"""
    try:
        with open(ARQUIVO_PRESTES_RETIRADOS, 'w', encoding='utf-8') as f:
            json.dump(lista, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"Erro ao salvar prestes retirados: {e}")

def adicionar_prestes_retirados(ean: str, setor: Optional[str], descricao: str, data_retirada: str, validade: str = None):
    """Adiciona um produto à lista de prestes retirados com mais informações"""
    retirados = carregar_prestes_retirados()
    
    # Verifica se já existe (para não duplicar)
    for r in retirados:
        if (r['ean'] == ean and 
            r.get('setor') == setor and 
            r.get('validade') == validade and
            r.get('descricao') == descricao):
            return
    
    novo_registro = {
        'ean': ean,
        'setor': setor,
        'descricao': descricao,
        'data_retirada': data_retirada
    }
    if validade:
        novo_registro['validade'] = validade
    
    retirados.append(novo_registro)
    salvar_prestes_retirados(retirados)

def verificar_produto_retirado(ean: str, setor: Optional[str], validade: str = None) -> bool:
    """
    Verifica se um produto específico está na lista de retirados
    Retorna True se estiver retirado
    """
    retirados = carregar_prestes_retirados()
    
    for r in retirados:
        if r['ean'] == ean and r.get('setor') == setor:
            # Se o registro tem validade, compara
            if r.get('validade'):
                if r['validade'] == validade:
                    return True
            else:
                # Registro antigo sem validade - considera retirado
                return True
    return False

def listar_prestes_ativos(setor: Optional[str], produtos: list, faltas: list):
    """
    Lista apenas produtos prestes a vencer que NÃO estão em falta
    e NÃO tiveram prestes retirados
    """
    from ..core.config import DIAS_PRESTES
    
    prestes_lista = []
    
    for p in produtos:
        # Verifica se está em falta
        em_falta = p.descricao.lower() in [f.lower() for f in faltas]
        if em_falta:
            continue
        
        # Verifica se está retirado
        if verificar_produto_retirado(p.ean, p.setor, p.mes_ano):
            continue
        
        if p.esta_prestes:
            if p.dias_para_vencer <= 15:
                desconto = "50%"
            elif p.dias_para_vencer <= 30:
                desconto = "30%"
            elif p.dias_para_vencer <= 60:
                desconto = "20%"
            else:
                desconto = "10%"
            
            prestes_lista.append({
                'ean': p.ean,
                'descricao': p.descricao,
                'validade': p.mes_ano,
                'dias': p.dias_para_vencer,
                'desconto': desconto
            })
    
    return prestes_lista