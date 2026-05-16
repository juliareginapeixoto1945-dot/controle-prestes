# ============================================
# MÓDULO DE PRECIFICAÇÃO - CORRIGIDO
# ============================================

import pyperclip

from ..core.database import Database
from ..utils.helpers import limpar_tela, pausar, cabecalho
from ..utils.cores import Cores

def tirar_preco(setor: str = None):
    """
    Gera lista de EANs para atualização de preços
    COPIA APENAS OS CÓDIGOS, SEM DESCRIÇÃO
    """
    limpar_tela()
    cabecalho("5️⃣  LISTA PARA ATUALIZAR PREÇOS")
    print("(Apenas códigos EAN - copiados automaticamente)")
    
    if setor:
        print(Cores.info(f"📌 Setor: {setor}"))
    print("-" * 60)
    
    db = Database()
    produtos = db.carregar_produtos(setor)
    
    # CORREÇÃO: chamar método estático corretamente
    faltas = Database.carregar_faltas()
    
    if not produtos:
        print(Cores.info("Nenhum produto cadastrado neste setor."))
        pausar()
        return
    
    # Filtra apenas produtos ativos (não em falta)
    ativos = []
    for p in produtos:
        em_falta = p.descricao.lower() in [f.lower() for f in faltas]
        if not em_falta and p.status == 'ativo':
            ativos.append(p)
    
    # Remove duplicatas de EAN (mantém um de cada)
    eans_unicos = set()
    for p in ativos:
        eans_unicos.add(p.ean)
    
    # Ordena
    lista_eans = sorted(list(eans_unicos))
    
    print(f"📋 {len(lista_eans)} códigos EAN únicos encontrados:\n")
    
    # Mostra na tela (opcional - pode desligar se quiser)
    for i, ean in enumerate(lista_eans[:20], 1):
        print(f"   {ean}")
    
    if len(lista_eans) > 20:
        print(f"   ... e mais {len(lista_eans) - 20} códigos")
    
    print("-" * 60)
    
    # Cria o texto para copiar (apenas EANs, um por linha)
    texto_copia = "\n".join(lista_eans)
    
    # Tenta copiar para área de transferência
    try:
        pyperclip.copy(texto_copia)
        print(Cores.sucesso(f"\n✅ {len(lista_eans)} códigos copiados para área de transferência!"))
        print("   (Cole no sistema de precificação com Ctrl+V)")
    except ImportError:
        print(Cores.alerta("\n⚠️ pyperclip não instalado. Instale com:"))
        print("   pip install pyperclip")
        print("\n📋 Códigos (copie manualmente):")
        print("-" * 40)
        print(texto_copia)
        print("-" * 40)
    
    print(f"\n📊 Total: {len(lista_eans)} códigos únicos no setor {setor if setor else 'GERAL'}")
    pausar()