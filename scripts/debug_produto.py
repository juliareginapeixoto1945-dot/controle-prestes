#!/usr/bin/env python3
# ============================================
# SCRIPT PARA DEBUGAR PRODUTO
# ============================================

import sys
import os
import json
from datetime import date

# Adiciona diretório raiz ao path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.core.database import Database
from backend.modules.prestes import carregar_prestes_retirados
from backend.modules.listagem import listar_todos_produtos
from backend.modules.falta import produto_esta_em_falta

def debug_produto(ean=None, setor=None):
    print("\n" + "=" * 70)
    print("🔍 DEBUG DE PRODUTO")
    print("=" * 70)
    
    if not setor:
        setor = input("Digite o setor (ex: GERAL): ").strip().upper()
    if not ean:
        ean = input("Digite o EAN do produto: ").strip()
    
    print(f"\n📌 Setor: {setor}")
    print(f"📌 EAN: {ean}")
    
    # 1. Verificar no banco de dados
    db = Database()
    todos_produtos = db.carregar_produtos()
    
    produtos_encontrados = [p for p in todos_produtos if p.ean == ean and p.setor == setor]
    
    print(f"\n📦 Produtos no banco com este EAN: {len(produtos_encontrados)}")
    for i, p in enumerate(produtos_encontrados, 1):
        print(f"\n  {i}. {p.descricao}")
        print(f"     Validade: {p.validade.strftime('%d/%m/%Y')} ({p.mes_ano})")
        print(f"     Dias: {p.dias_para_vencer}")
        print(f"     Data cadastro: {p.data_cadastro}")
        print(f"     Status: {'Vencido' if p.esta_vencido else 'Prestes' if p.esta_prestes else 'OK'}")
    
    # 2. Verificar lista de prestes retirados
    prestes_retirados = carregar_prestes_retirados()
    retirados_setor = [r for r in prestes_retirados if r['setor'] == setor and r['ean'] == ean]
    
    print(f"\n🚫 Prestes retirados com este EAN: {len(retirados_setor)}")
    for i, r in enumerate(retirados_setor, 1):
        print(f"  {i}. {r}")
    
    # 3. Verificar lista de faltas
    faltas = Database.carregar_faltas()
    em_falta = [f for f in faltas if f.lower() in [p.descricao.lower() for p in produtos_encontrados]]
    
    print(f"\n⚠️ Em falta: {len(em_falta)}")
    for f in em_falta:
        print(f"  • {f}")
    
    # 4. Testar se aparece na listagem
    from backend.modules.listagem import listar_todos_produtos, listar_produtos_ativos
    
    todos_listados = listar_todos_produtos(setor)
    aparece_todos = any(p['ean'] == ean for p in todos_listados)
    
    ativos_listados = listar_produtos_ativos(setor)
    aparece_ativos = any(p['ean'] == ean for p in ativos_listados)
    
    print(f"\n📋 Aparece em 'Listar Todos': {'✅ SIM' if aparece_todos else '❌ NÃO'}")
    print(f"📋 Aparece em 'Listar Ativos': {'✅ SIM' if aparece_ativos else '❌ NÃO'}")
    
    if not aparece_todos:
        print("\n🔎 Possíveis causas:")
        print("  • Produto ainda está na lista de prestes retirados")
        print("  • Produto está marcado como 'em falta'")
        print("  • Data de validade inválida")
        
        # Mostrar todos os produtos listados (primeiros 5)
        print("\n📋 Primeiros produtos listados em 'Listar Todos':")
        for i, p in enumerate(todos_listados[:5], 1):
            print(f"  {i}. {p['ean']} - {p['descricao']} ({p['status']})")

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        ean = sys.argv[1]
        setor = sys.argv[2] if len(sys.argv) > 2 else None
        debug_produto(ean, setor)
    else:
        debug_produto()