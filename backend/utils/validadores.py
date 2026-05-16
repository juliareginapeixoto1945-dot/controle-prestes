# ============================================
# VALIDAÇÕES
# ============================================

from datetime import datetime, date
import re
from typing import Optional, Tuple

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
    """Valida data no formato MM/AAAA"""
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
    
    return False, None, None

def obter_primeiro_dia_mes(mes: int, ano: int) -> date:
    """Retorna o primeiro dia do mês"""
    return date(ano, mes, 1)