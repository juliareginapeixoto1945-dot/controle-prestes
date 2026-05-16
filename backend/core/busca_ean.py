# ============================================
# MÓDULO DE BUSCA DE PRODUTOS POR EAN
# ============================================

import csv
from pathlib import Path
from typing import Optional, Dict, Set
import logging

from .config import DATA_DIR

logging.basicConfig(
    filename='logs/sistema.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class BuscaEAN:
    """Classe para buscar produtos por código EAN"""
    
    def __init__(self):
        self.arquivo_eans = DATA_DIR / "lista_ean_descricao.csv"
        self.cache: Dict[str, str] = {}
        self.mapeamento: Dict[str, str] = {}
        self.carregado = False
        self.usar_online = True
        
        # Tenta importar openfoodfacts (opcional)
        try:
            import openfoodfacts
            self.OPENFOOD_AVAILABLE = True
        except ImportError:
            self.OPENFOOD_AVAILABLE = False
    
    def _resolver_cadeia(self, ean: str, pares: Dict[str, str], visitados: Optional[Set[str]] = None) -> Optional[str]:
        """Resolve cadeia de EANs recursivamente"""
        if visitados is None:
            visitados = set()
        
        if ean in visitados:
            return None
        
        visitados.add(ean)
        
        if ean not in pares:
            return None
        
        valor = pares[ean]
        
        if not (isinstance(valor, str) and valor.isdigit() and len(valor) in [12, 13]):
            return valor
        
        return self._resolver_cadeia(valor.lstrip('0'), pares, visitados)
    
    def carregar_cache(self) -> bool:
        """Carrega o arquivo CSV para memória"""
        if self.carregado:
            return True
            
        if not self.arquivo_eans.exists():
            return False
        
        try:
            pares = {}
            
            with open(self.arquivo_eans, 'r', encoding='utf-8') as f:
                leitor = csv.reader(f, delimiter=';')
                next(leitor, None)  # Pula cabeçalho
                
                for linha in leitor:
                    if len(linha) >= 2:
                        ean = linha[0].strip().lstrip('0')
                        valor = linha[1].strip()
                        
                        if valor.isdigit() and len(valor) in [12, 13]:
                            pares[ean] = valor.lstrip('0')
                        else:
                            pares[ean] = valor
                            self.cache[ean] = valor
            
            # Resolve cadeias
            for ean, valor in pares.items():
                if ean not in self.cache and valor.isdigit():
                    descricao = self._resolver_cadeia(ean, pares)
                    if descricao:
                        self.cache[ean] = descricao
            
            self.carregado = True
            logging.info(f"Cache de EANs carregado com {len(self.cache)} resoluções")
            return True
            
        except Exception as e:
            logging.error(f"Erro ao carregar cache: {e}")
            return False
    
    def buscar_online(self, ean: str) -> Optional[str]:
        """Busca na internet (fallback)"""
        if not self.usar_online or not self.OPENFOOD_AVAILABLE:
            return None
        
        try:
            import openfoodfacts
            api = openfoodfacts.API(user_agent="ControlePrestes/3.0")
            result = api.product.get(ean, fields=["product_name", "brands"])
            
            if result and result.get("status") == 1:
                product = result.get("product", {})
                nome = product.get("product_name", "")
                marca = product.get("brands", "")
                
                if nome:
                    return f"{nome} - {marca}" if marca else nome
        except:
            pass
        
        return None
    
    def buscar(self, ean: str, tentar_online: bool = True) -> Optional[str]:
        """Busca descrição do produto pelo EAN"""
        if not self.carregado:
            self.carregar_cache()
        
        ean_busca = ean.strip().lstrip('0')
        ean_com_zero = ean.strip().zfill(13)
        
        for versao in [ean_busca, ean_com_zero]:
            if versao in self.cache:
                return self.cache[versao]
        
        if tentar_online and self.usar_online:
            return self.buscar_online(ean)
        
        return None
    
    def adicionar_ao_cache(self, ean: str, descricao: str):
        """Adiciona um novo produto ao cache"""
        ean_limpo = ean.strip().lstrip('0')
        ean_com_zero = ean.strip().zfill(13)
        
        self.cache[ean_limpo] = descricao
        self.cache[ean_com_zero] = descricao
        
        # Opcional: salvar no arquivo para persistência
        self._salvar_no_arquivo(ean, descricao)
    
    def _salvar_no_arquivo(self, ean: str, descricao: str):
        """Salva um novo produto no arquivo CSV"""
        try:
            if not self.arquivo_eans.exists():
                with open(self.arquivo_eans, 'w', encoding='utf-8') as f:
                    f.write("EAN;DESCRICAO\n")
            
            with open(self.arquivo_eans, 'a', encoding='utf-8') as f:
                f.write(f"{ean};{descricao}\n")
            
            logging.info(f"Novo EAN salvo no arquivo: {ean}")
        except Exception as e:
            logging.error(f"Erro ao salvar EAN no arquivo: {e}")