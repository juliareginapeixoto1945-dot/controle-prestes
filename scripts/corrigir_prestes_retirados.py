#!/usr/bin/env python3
# ============================================
# CORRIGIR REGISTROS ANTIGOS DE PRESTES RETIRADOS
# ============================================

import sys
import os
import json
from datetime import date
from pathlib import Path

# Adiciona diretório raiz ao path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.core.database import Database
from backend.modules.prestes import carregar_prestes_retirados, salvar_prestes_retirados

def corrigir_registros_antigos():
    """Adiciona data de validade aos registros antigos de prestes retirados"""
    
    print("\n" + "=" * 70)
    print("🔧 CORRIGIR REGISTROS DE PRESTES RETIRADOS")
    print("=" * 70)
    
    # Carrega lista atual
    prestes_retirados = carregar_prestes_retirados()
    print(f"\n📊 Total de registros: {len(prestes_retirados)}")
    
    # Carrega todos os produtos do banco
    db = Database()
    todos_produtos = db.carregar_produtos()
    
    # Cria um dicionário para buscar produtos por EAN e setor
    produtos_dict = {}
    for p in todos_produtos:
        chave = f"{p.ean}|{p.setor}|{p.validade.strftime('%m/%Y')}"
        produtos_dict[chave] = p.descricao
    
    corrigidos = 0
    novos_registros = []
    
    for registro in prestes_retirados:
        # Se já tem validade, mantém
        if registro.get('validade'):
            novos_registros.append(registro)
            continue
        
        # Tenta encontrar a validade no banco
        ean = registro['ean']
        setor = registro['setor']
        descricao = registro['descricao']
        
        # Busca produtos com este EAN e setor
        produtos_encontrados = [
            p for p in todos_produtos 
            if p.ean == ean and p.setor == setor
        ]
        
        if produtos_encontrados:
            # Se encontrou, usa a validade do primeiro (mais recente?)
            validade = produtos_encontrados[-1].mes_ano
            registro['validade'] = validade
            corrigidos += 1
            print(f"✅ Corrigido: {ean} - {descricao} - Validade {validade}")
        else:
            # Se não encontrou, mantém sem validade (registro antigo)
            print(f"⚠️ Não encontrado: {ean} - {descricao}")
        
        novos_registros.append(registro)
    
    # Salva registros corrigidos
    salvar_prestes_retirados(novos_registros)
    
    print(f"\n✅ {corrigidos} registro(s) corrigido(s)")
    print(f"📊 Total final: {len(novos_registros)} registros")

def listar_registros_problema():
    """Lista registros que podem estar causando problema"""
    prestes_retirados = carregar_prestes_retirados()
    
    print("\n🔍 REGISTROS SEM VALIDADE:")
    sem_validade = [r for r in prestes_retirados if not r.get('validade')]
    
    for i, r in enumerate(sem_validade, 1):
        print(f"{i}. {r['ean']} - {r['setor']} - {r['descricao']}")

def menu():
    while True:
        print("\n" + "=" * 50)
        print("CORREÇÃO DE PRESTES RETIRADOS")
        print("=" * 50)
        print("1 - Listar registros sem validade")
        print("2 - Corrigir registros automaticamente")
        print("3 - Ver todos os registros")
        print("4 - Limpar TODOS os registros (CUIDADO!)")
        print("0 - Sair")
        
        opcao = input("\n👉 Escolha: ").strip()
        
        if opcao == '1':
            listar_registros_problema()
        elif opcao == '2':
            corrigir_registros_antigos()
        elif opcao == '3':
            prestes = carregar_prestes_retirados()
            print(f"\n📋 Total: {len(prestes)} registros")
            for i, r in enumerate(prestes[:10], 1):
                print(f"{i}. {r}")
        elif opcao == '4':
            conf = input("⚠️ ISSO APAGARÁ TODOS OS REGISTROS! Continuar? (s/N): ")
            if conf.lower() == 's':
                salvar_prestes_retirados([])
                print("✅ Lista limpa!")
        elif opcao == '0':
            break
        else:
            print("Opção inválida")

if __name__ == "__main__":
    menu()