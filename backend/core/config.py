# ============================================
# CONFIGURAÇÕES GLOBAIS DO SISTEMA
# ============================================
import os
from pathlib import Path

# Diretórios
BASE_DIR = Path(__file__).parent.parent.parent
DATA_DIR = BASE_DIR / "data"
LOGS_DIR = BASE_DIR / "logs"
BACKUP_DIR = DATA_DIR / "backups"

# Arquivos
ARQUIVO_PRODUTOS = DATA_DIR / "produtos.csv"
ARQUIVO_FALTAS = DATA_DIR / "faltas.txt"
ARQUIVO_LOG = LOGS_DIR / "sistema.log"
ARQUIVO_SETORES = DATA_DIR / "setores.txt"
ARQUIVO_SENHAS = DATA_DIR / "senhas_setores.json"  # NOVO

# Configurações de negócio
DIAS_PRESTES = 90
FORMATO_DATA = "%m/%Y"
FORMATO_DATA_ARQUIVO = "%Y-%m"

# Criar diretórios se não existirem
for diretorio in [DATA_DIR, LOGS_DIR, BACKUP_DIR]:
    diretorio.mkdir(parents=True, exist_ok=True)

# Configurações de exibição
TITULO = "PRESTES MANAGER v3.0"
LARGURA_TELA = 80