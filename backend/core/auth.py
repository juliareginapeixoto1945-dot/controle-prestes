# ============================================
# MÓDULO DE AUTENTICAÇÃO
# ============================================
import hashlib
import json
from pathlib import Path
from ..core.config import DATA_DIR

ARQUIVO_SENHAS = DATA_DIR / "senhas_setores.json"

def hash_senha(senha: str) -> str:
    """
    Gera um hash SHA-256 da senha.
    NOTA: Em produção, use bcrypt ou argon2 para maior segurança.
    """
    if not senha:
        return ""
    return hashlib.sha256(senha.encode()).hexdigest()

def carregar_senhas() -> dict:
    """Carrega o dicionário de setores -> senha_hash"""
    if ARQUIVO_SENHAS.exists():
        try:
            with open(ARQUIVO_SENHAS, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {}
    return {}

def salvar_senhas(senhas: dict) -> bool:
    """Salva o dicionário de senhas no arquivo"""
    try:
        with open(ARQUIVO_SENHAS, 'w', encoding='utf-8') as f:
            json.dump(senhas, f, indent=2, ensure_ascii=False)
        return True
    except:
        return False

def definir_senha(setor: str, senha: str) -> bool:
    """Define ou altera a senha de um setor"""
    senhas = carregar_senhas()
    
    # Se senha vazia, remove a proteção
    if not senha:
        if setor in senhas:
            del senhas[setor]
    else:
        senhas[setor] = hash_senha(senha)
    
    return salvar_senhas(senhas)

def verificar_senha(setor: str, senha: str) -> bool:
    """Verifica se a senha fornecida corresponde à do setor"""
    senhas = carregar_senhas()
    if setor not in senhas:
        # Se não tem senha cadastrada, permite acesso
        return True
    return senhas[setor] == hash_senha(senha)

def setor_tem_senha(setor: str) -> bool:
    """Verifica se um setor já possui senha cadastrada"""
    senhas = carregar_senhas()
    return setor in senhas