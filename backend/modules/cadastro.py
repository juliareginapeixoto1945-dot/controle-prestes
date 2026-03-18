# ============================================
# MÓDULO DE CADASTRO MANUAL - VERSÃO FINAL
# ============================================
# Agora com busca local de EANs (SEM PERGUNTAR)
# ============================================

from datetime import date
from typing import Optional

from ..core.database import Database
from ..core.models import Produto
from ..core.busca_ean import BuscaEAN
from ..utils.helpers import limpar_tela, pausar, cabecalho, registrar_operacao
from ..utils.validadores import validar_ean, validar_mes_ano, validar_descricao, obter_primeiro_dia_mes
from ..utils.cores import Cores

# Inicializa o buscador de EANs
buscador_ean = BuscaEAN()

def buscar_descricao_por_ean(ean: str, produtos: list) -> Optional[str]:
    """Busca descrição de um produto pelo EAN"""
    for p in produtos:
        if p.ean == ean:
            return p.descricao
    return None

def adicionar_produto(setor: str, db: Database):
    """
    Função principal de cadastro manual - FLUXO RÁPIDO
    Agora com busca local de EANs (SEM PERGUNTAR)
    """
    limpar_tela()
    cabecalho("1️⃣  ADICIONAR PRODUTO (MODO DIGITAÇÃO)")
    print(f"📌 Setor: {Cores.verde(setor)}")
    print("(Digite o código EAN manualmente)")
    print("Para SAIR, digite 0 no EAN")
    print("-" * 60)
    
    # Carrega cache de EANs
    global buscador_ean
    buscador_ean.carregar_cache()
    
    produtos = db.carregar_produtos(setor)
    
    total_adicionados = 0
    primeiro_produto = True
    
    while True:
        if not primeiro_produto:
            print("\n" + "-" * 60)
            print(Cores.verde("🔄 Pronto para próximo produto..."))
        primeiro_produto = False
        
        print(f"\n{Cores.azul('📌 Novo Produto')}")
        ean = input("Código EAN (ou 0 para sair): ").strip()
        
        if ean == '0':
            break
            
        if not validar_ean(ean):
            print(Cores.erro("EAN inválido! Deve ter 13 dígitos."))
            continue
        
        # Verifica se produto já existe no sistema
        descricao = buscar_descricao_por_ean(ean, produtos)
        
        if descricao:
            print(Cores.sucesso(f"✓ Produto já cadastrado: {descricao}"))
        else:
            # Tenta buscar no cache de EANs
            print(Cores.info(f"🔍 Buscando EAN {ean} no banco local..."))
            descricao_cache = buscador_ean.buscar(ean)
            
            if descricao_cache:
                # USA AUTOMATICAMENTE SEM PERGUNTAR
                print(Cores.sucesso(f"✅ Encontrado: {descricao_cache}"))
                descricao = descricao_cache
            
            if not descricao:
                # Se não encontrou, pede manual
                print(Cores.info("⌨️ Digite a descrição manualmente:"))
                descricao = input("Descrição: ").strip()
                if not validar_descricao(descricao):
                    print(Cores.erro("Descrição inválida!"))
                    continue
        
        # Data de validade
        while True:
            data_str = input("Data de validade (MM/AAAA): ").strip()
            valido, mes, ano = validar_mes_ano(data_str)
            if valido:
                data_validade = obter_primeiro_dia_mes(mes, ano)
                break
            print(Cores.erro("Data inválida! Use MM/AAAA (ex: 12/2024)"))
        
        # Adiciona o produto
        produtos.append(Produto(
            ean=ean,
            descricao=descricao,
            validade=data_validade,
            status='ativo',
            setor=setor
        ))
        
        total_adicionados += 1
        print(Cores.sucesso(f"✓ Registrado: {descricao} - Validade: {data_validade.strftime('%m/%Y')}"))
        registrar_operacao("CADASTRO", f"{setor} - {ean} - {descricao}")
    
    if total_adicionados > 0:
        if db.salvar_produtos(db.carregar_produtos() + produtos[-total_adicionados:]):
            print(Cores.sucesso(f"\n💾 {total_adicionados} produto(s) salvo(s) no setor {setor}!"))
        else:
            print(Cores.erro("\n❌ Erro ao salvar produtos!"))
    
    pausar()