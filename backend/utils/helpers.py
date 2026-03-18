# ============================================
# FUNÇÕES AUXILIARES
# ============================================

import os
import sys
from datetime import datetime
from typing import Optional
import logging

from .cores import Cores

def limpar_tela():
    """Limpa a tela do terminal"""
    os.system('cls' if os.name == 'nt' else 'clear')

def pausar(mensagem: str = "Pressione ENTER para continuar..."):
    """Pausa a execução até o usuário pressionar ENTER"""
    input(f"\n{Cores.info(mensagem)}")

def cabecalho(titulo: str, largura: int = 80):
    """Exibe um cabeçalho formatado"""
    print("╔" + "═" * (largura - 2) + "╗")
    print(f"║{titulo.center(largura - 2)}║")
    print("╠" + "═" * (largura - 2) + "╣")

def rodape(largura: int = 80):
    """Exibe um rodapé formatado"""
    print("╚" + "═" * (largura - 2) + "╝")

def exibir_tabela(cabecalhos: list, linhas: list, larguras: list = None):
    """Exibe dados em formato de tabela"""
    if not larguras:
        larguras = [20] * len(cabecalhos)
    
    # Cabeçalho
    linha_sep = "-" * (sum(larguras) + len(larguras) + 1)
    print(linha_sep)
    
    cab = ""
    for i, titulo in enumerate(cabecalhos):
        cab += f"{titulo:<{larguras[i]}}|"
    print(cab)
    print(linha_sep)
    
    # Linhas
    for linha in linhas:
        lin = ""
        for i, valor in enumerate(linha):
            lin += f"{str(valor):<{larguras[i]}}|"
        print(lin)
    
    print(linha_sep)

def registrar_operacao(operacao: str, detalhes: str = ""):
    """Registra operação no log"""
    logging.info(f"{operacao}: {detalhes}")

def confirmar(mensagem: str) -> bool:
    """Pede confirmação do usuário"""
    resp = input(f"{Cores.amarelo(mensagem)} (s/N): ").strip().lower()
    return resp in ['s', 'sim', 'yes', 'y']