# ============================================
# MÓDULO DE CADASTRO COM BIP - WEB VERSION
# ============================================
import json
from datetime import date
from pathlib import Path
from typing import List, Dict, Optional
from ..core.database import Database
from ..core.models import Produto
from ..core.busca_ean import BuscaEAN
from ..core.validadores import (
    decodificar_mes, decodificar_ano, validar_ean,
    obter_primeiro_dia_mes, CODIGO_CANCELAR_COMPLETO
)
from ..core.config import DATA_DIR

# Arquivo para salvar os erros
ARQUIVO_ERROS = DATA_DIR / "erros_bip.json"

def carregar_erros() -> List[Dict]:
    """Carrega a lista de erros do arquivo"""
    if ARQUIVO_ERROS.exists():
        try:
            with open(ARQUIVO_ERROS, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return []
    return []

def salvar_erros(erros: List[Dict]):
    """Salva a lista de erros no arquivo"""
    try:
        with open(ARQUIVO_ERROS, 'w', encoding='utf-8') as f:
            json.dump(erros, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"Erro ao salvar erros: {e}")

def adicionar_erro(setor: Optional[str], ean: str, motivo: str, codigo_mes: str = None, codigo_ano: str = None):
    """Adiciona um erro à lista"""
    erros = carregar_erros()
    erros.append({
        'setor': setor,
        'ean': ean,
        'motivo': motivo,
        'codigo_mes': codigo_mes,
        'codigo_ano': codigo_ano,
        'timestamp': str(date.today())
    })
    salvar_erros(erros)

def processar_bip_produto(setor: Optional[str], codigo: str) -> dict:
    """
    Processa um código bipado
    Retorna um dicionário com o resultado
    """
    # Verifica se é código de cancelar
    if codigo == CODIGO_CANCELAR_COMPLETO or codigo.lstrip('0') == CODIGO_CANCELAR_COMPLETO.lstrip('0'):
        return {
            'tipo': 'cancelar',
            'mensagem': 'Modo CANCELAR ativado'
        }
    
    # Verifica se é código de mês
    mes = decodificar_mes(codigo)
    if mes:
        return {
            'tipo': 'mes',
            'valor': mes,
            'codigo': codigo,
            'mensagem': f"Mês: {mes:02d}"
        }
    
    # Verifica se é código de ano
    ano = decodificar_ano(codigo)
    if ano:
        return {
            'tipo': 'ano',
            'valor': ano,
            'codigo': codigo,
            'mensagem': f"Ano: {ano}"
        }
    
    # Verifica se é EAN de produto válido
    if validar_ean(codigo):
        # Busca descrição
        buscador = BuscaEAN()
        descricao = buscador.buscar(codigo, tentar_online=True)
        
        return {
            'tipo': 'produto',
            'ean': codigo,
            'descricao': descricao,
            'encontrado': descricao is not None
        }
    
    # Se não for nada reconhecido
    return {
        'tipo': 'erro',
        'mensagem': 'Código não reconhecido'
    }

def cancelar_ultimo_produto(setor: Optional[str], ean: str) -> tuple:
    """
    Cancela o último produto cadastrado com o EAN especificado
    Retorna (sucesso, mensagem, produto)
    """
    db = Database()
    todos_produtos = db.carregar_produtos()
    
    # Filtra produtos do setor com este EAN
    produtos_setor = [p for p in todos_produtos if p.ean == ean and p.setor == setor]
    
    if not produtos_setor:
        return False, "Produto não encontrado neste setor", None
    
    # Pega o último (assumindo ordem cronológica)
    ultimo = produtos_setor[-1]
    
    # Remove do banco de dados
    novos_produtos = [p for p in todos_produtos 
                     if not (p.ean == ean and p.validade == ultimo.validade 
                             and p.setor == setor and p.descricao == ultimo.descricao)]
    
    if db.salvar_produtos(novos_produtos):
        return True, f"Produto '{ultimo.descricao}' cancelado", ultimo
    else:
        return False, "Erro ao cancelar produto", None