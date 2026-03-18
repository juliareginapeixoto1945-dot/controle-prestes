# ============================================
# GERENCIAMENTO DO BANCO DE DADOS - SEM SETOR GERAL
# ============================================
import csv
import os
import shutil
from datetime import datetime, date
from pathlib import Path
from typing import List, Dict, Optional
import logging
from .config import ARQUIVO_PRODUTOS, ARQUIVO_FALTAS, BACKUP_DIR, ARQUIVO_SETORES
from .models import Produto

# Configura logging
logging.basicConfig(
    filename='logs/sistema.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class Database:
    """Gerencia todas as operações com arquivos"""
    
    def __init__(self):
        """Construtor - mantido para compatibilidade"""
        pass
    
    @staticmethod
    def carregar_produtos(setor: str = None) -> List[Produto]:
        """
        Carrega produtos do CSV
        Se setor for None, carrega todos
        Se setor for especificado, carrega apenas daquele setor
        """
        produtos = []
        
        if not ARQUIVO_PRODUTOS.exists():
            return produtos
        
        try:
            with open(ARQUIVO_PRODUTOS, 'r', encoding='utf-8') as f:
                leitor = csv.DictReader(f)
                for linha in leitor:
                    try:
                        ano_mes = linha['Validade'].split('-')
                        if len(ano_mes) == 2:
                            ano = int(ano_mes[0])
                            mes = int(ano_mes[1])
                            
                            # Força primeiro dia do mês
                            data_validade = date(ano, mes, 1)
                            
                            # Data de cadastro
                            data_cadastro = None
                            if 'DataCadastro' in linha and linha['DataCadastro']:
                                try:
                                    data_cadastro = datetime.strptime(linha['DataCadastro'], "%Y-%m-%d").date()
                                except:
                                    data_cadastro = date.today()
                            else:
                                data_cadastro = date.today()
                            
                            produto = Produto(
                                ean=linha['EAN'],
                                descricao=linha['Descricao'],
                                validade=data_validade,
                                status=linha.get('Status', 'ativo'),
                                setor=linha.get('Setor'),  # Pode ser None
                                data_cadastro=data_cadastro
                            )
                            
                            # Filtra por setor se especificado
                            if setor is None or produto.setor == setor:
                                produtos.append(produto)
                    
                    except Exception as e:
                        logging.error(f"Erro ao carregar produto {linha}: {e}")
        except Exception as e:
            logging.error(f"Erro ao carregar arquivo: {e}")
        
        return produtos
    
    @staticmethod
    def salvar_produtos(produtos: List[Produto]) -> bool:
        """Salva todos os produtos no CSV"""
        try:
            Database.fazer_backup_automatico()
            
            with open(ARQUIVO_PRODUTOS, 'w', newline='', encoding='utf-8') as f:
                campos = ['EAN', 'Descricao', 'Validade', 'Status', 'Setor', 'DataCadastro']
                escritor = csv.DictWriter(f, fieldnames=campos)
                escritor.writeheader()
                
                for p in produtos:
                    escritor.writerow({
                        'EAN': p.ean,
                        'Descricao': p.descricao,
                        'Validade': p.validade.strftime("%Y-%m"),
                        'Status': p.status,
                        'Setor': p.setor if p.setor else '',
                        'DataCadastro': p.data_cadastro.strftime("%Y-%m-%d") if p.data_cadastro else ''
                    })
            
            logging.info(f"Salvos {len(produtos)} produtos com sucesso")
            return True
        
        except Exception as e:
            logging.error(f"Erro ao salvar produtos: {e}")
            return False
    
    @staticmethod
    def carregar_faltas() -> List[str]:
        """Carrega lista de produtos em falta"""
        faltas = []
        
        if ARQUIVO_FALTAS.exists():
            try:
                with open(ARQUIVO_FALTAS, 'r', encoding='utf-8') as f:
                    faltas = [linha.strip().lower() for linha in f if linha.strip()]
                logging.info(f"Carregadas {len(faltas)} faltas")
            except Exception as e:
                logging.error(f"Erro ao carregar faltas: {e}")
        
        return faltas
    
    @staticmethod
    def salvar_faltas(faltas: List[str]) -> bool:
        """Salva lista de produtos em falta"""
        try:
            with open(ARQUIVO_FALTAS, 'w', encoding='utf-8') as f:
                for falta in faltas:
                    f.write(f"{falta}\n")
            logging.info(f"Salvas {len(faltas)} faltas")
            return True
        except Exception as e:
            logging.error(f"Erro ao salvar faltas: {e}")
            return False
    
    @staticmethod
    def carregar_setores() -> List[str]:
        """Carrega lista de setores cadastrados"""
        setores = []  # REMOVIDO: não tem mais setor GERAL padrão
        
        if ARQUIVO_SETORES.exists():
            try:
                with open(ARQUIVO_SETORES, 'r', encoding='utf-8') as f:
                    setores = [linha.strip() for linha in f if linha.strip()]
                logging.info(f"Carregados {len(setores)} setores")
            except Exception as e:
                logging.error(f"Erro ao carregar setores: {e}")
        
        return setores
    
    @staticmethod
    def salvar_setores(setores: List[str]) -> bool:
        """Salva lista de setores"""
        try:
            with open(ARQUIVO_SETORES, 'w', encoding='utf-8') as f:
                for setor in setores:
                    f.write(f"{setor}\n")
            logging.info(f"Salvos {len(setores)} setores")
            return True
        except Exception as e:
            logging.error(f"Erro ao salvar setores: {e}")
            return False
    
    @staticmethod
    def excluir_produto(ean: str, setor: str = None) -> bool:
        """
        Exclui um produto do sistema
        Se setor for especificado, exclui apenas daquele setor
        """
        produtos = Database.carregar_produtos()
        
        if setor:
            # Exclui apenas do setor específico
            produtos_restantes = [p for p in produtos if not (p.ean == ean and p.setor == setor)]
        else:
            # Exclui todas as ocorrências do EAN
            produtos_restantes = [p for p in produtos if p.ean != ean]
        
        if len(produtos_restantes) == len(produtos):
            return False  # Nenhum produto removido
        
        return Database.salvar_produtos(produtos_restantes)
    
    @staticmethod
    def fazer_backup_automatico():
        """Faz backup automático do arquivo de produtos"""
        if ARQUIVO_PRODUTOS.exists():
            data = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_nome = BACKUP_DIR / f"produtos_backup_{data}.csv"
            shutil.copy(ARQUIVO_PRODUTOS, backup_nome)
            
            # Mantém apenas os 10 backups mais recentes
            backups = sorted(BACKUP_DIR.glob("produtos_backup_*.csv"))
            if len(backups) > 10:
                for velho in backups[:-10]:
                    velho.unlink()