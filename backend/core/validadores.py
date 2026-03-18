# ============================================
# VALIDAÇÕES E DECODIFICAÇÃO DE CÓDIGOS
# ============================================

from datetime import datetime, date
import re
from typing import Optional, Tuple

# Dicionários com códigos de validade (mesmo da versão CMD)
CODIGOS_MES_13 = {
    "0078991010001": 1,   # Janeiro
    "0078991020000": 2,   # Fevereiro
    "0078991030009": 3,   # Março
    "0078991040008": 4,   # Abril
    "0078991050007": 5,   # Maio
    "0078991060006": 6,   # Junho
    "0078991070005": 7,   # Julho
    "0078991080004": 8,   # Agosto
    "0078991090003": 9,   # Setembro
    "0078991100009": 10,  # Outubro
    "0078991110008": 11,  # Novembro
    "0078991120007": 12,  # Dezembro
}

CODIGOS_ANO_13 = {
    "0078992202603": 2026,
    "0078992202702": 2027,
    "0078992202801": 2028,
    "0078992202900": 2029,
    "0078992203006": 2030,
    "0078992203105": 2031,
    "0078992203204": 2032,
}

# Versões sem o zero inicial (12 dígitos)
CODIGOS_MES_12 = {cod[1:]: valor for cod, valor in CODIGOS_MES_13.items()}
CODIGOS_ANO_12 = {cod[1:]: valor for cod, valor in CODIGOS_ANO_13.items()}

# Código para cancelar
CODIGO_CANCELAR = "78999000000"  # Base sem DV
CODIGO_CANCELAR_COMPLETO = None  # Será calculado

def calcular_dv_ean13(codigo: str) -> str:
    """
    Calcula o dígito verificador de um código EAN-13
    Recebe um código de 12 dígitos e retorna o código completo com 13 dígitos
    """
    if len(codigo) != 12:
        codigo = codigo.zfill(12)
    
    soma_par = sum(int(codigo[i]) for i in range(0, 12, 2))
    soma_impar = sum(int(codigo[i]) for i in range(1, 12, 2))
    total = soma_par + soma_impar * 3
    dv = (10 - (total % 10)) % 10
    return f"{codigo}{dv}"

# Inicializa o código de cancelar completo
CODIGO_CANCELAR_COMPLETO = calcular_dv_ean13(CODIGO_CANCELAR)

def decodificar_mes(codigo: str) -> Optional[int]:
    """Decodifica código EAN de mês (aceita 12 ou 13 dígitos)"""
    codigo = codigo.strip()
    if codigo in CODIGOS_MES_13:
        return CODIGOS_MES_13[codigo]
    if codigo in CODIGOS_MES_12:
        return CODIGOS_MES_12[codigo]
    return None

def decodificar_ano(codigo: str) -> Optional[int]:
    """Decodifica código EAN de ano (aceita 12 ou 13 dígitos)"""
    codigo = codigo.strip()
    if codigo in CODIGOS_ANO_13:
        return CODIGOS_ANO_13[codigo]
    if codigo in CODIGOS_ANO_12:
        return CODIGOS_ANO_12[codigo]
    return None

def validar_ean(ean: str) -> bool:
    """Valida código EAN-13"""
    if not ean or not ean.strip():
        return False
    
    ean = re.sub(r'[^0-9]', '', ean)
    
    if len(ean) != 13:
        return False
    
    try:
        soma_par = sum(int(ean[i]) for i in range(0, 12, 2))
        soma_impar = sum(int(ean[i]) for i in range(1, 12, 2))
        total = soma_par + soma_impar * 3
        digito_verificador = (10 - (total % 10)) % 10
        return digito_verificador == int(ean[12])
    except:
        return False

def validar_mes_ano(data_str: str) -> Tuple[bool, Optional[int], Optional[int]]:
    """Valida data no formato MM/AAAA (aceita vários formatos)"""
    if not data_str or not data_str.strip():
        return False, None, None
    
    data_str = data_str.strip()
    numeros = re.sub(r'[^0-9]', '', data_str)
    
    # Tenta diferentes formatos
    if len(numeros) == 6:  # MMAAAA
        mes = int(numeros[0:2])
        ano = int(numeros[2:6])
        if 1 <= mes <= 12 and 2000 <= ano <= 2100:
            return True, mes, ano
    elif len(numeros) == 4:  # MMAA
        mes = int(numeros[0:2])
        ano = 2000 + int(numeros[2:4])
        if 1 <= mes <= 12 and 2000 <= ano <= 2100:
            return True, mes, ano
    elif len(numeros) == 5:  # M AAAA (ex: 62027)
        mes = int(numeros[0:1])
        ano = int(numeros[1:5])
        if 1 <= mes <= 12 and 2000 <= ano <= 2100:
            return True, mes, ano
    elif len(numeros) == 3:  # M AA (ex: 627)
        mes = int(numeros[0:1])
        ano = 2000 + int(numeros[1:3])
        if 1 <= mes <= 12 and 2000 <= ano <= 2100:
            return True, mes, ano
    
    return False, None, None

def validar_descricao(descricao: str) -> bool:
    """Valida descrição do produto"""
    if not descricao or not descricao.strip():
        return False
    if len(descricao.strip()) < 3:
        return False
    return True

def obter_primeiro_dia_mes(mes: int, ano: int) -> date:
    """Retorna o primeiro dia do mês"""
    return date(ano, mes, 1)