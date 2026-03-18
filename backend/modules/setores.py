# ============================================
# MÓDULO DE GERENCIAMENTO DE SETORES - SEM GERAL
# ============================================
from ..core.database import Database
from ..utils.helpers import limpar_tela, pausar, cabecalho, confirmar
from ..utils.cores import Cores

setor_atual = None  # MODIFICADO: não tem mais valor padrão

def get_setor_atual():
    """Retorna o setor atual"""
    global setor_atual
    return setor_atual

def set_setor_atual(setor):
    """Define o setor atual"""
    global setor_atual
    setor_atual = setor

def gerenciar_setores():
    """Menu de gerenciamento de setores"""
    global setor_atual
    db = Database()
    
    while True:
        limpar_tela()
        cabecalho("🏢 GERENCIAR SETORES")
        
        setores = db.carregar_setores()
        print(f"\n📌 Setor atual: {Cores.verde(setor_atual) if setor_atual else Cores.vermelho('Nenhum')}")
        
        print("\n📋 Setores disponíveis:")
        if setores:
            for i, setor in enumerate(setores, 1):
                if setor == setor_atual:
                    print(f"   {i}. {Cores.verde(f'{setor} (ATIVO)')}")
                else:
                    print(f"   {i}. {setor}")
        else:
            print(Cores.info("   Nenhum setor cadastrado"))
        
        print("\n" + "-" * 60)
        print("1 - Mudar de setor")
        print("2 - Criar novo setor")
        print("3 - Renomear setor")
        print("4 - Excluir setor (apenas se vazio)")
        print("0 - Voltar")
        
        opcao = input("\n👉 Escolha: ").strip()
        
        if opcao == '1':
            # Mudar de setor
            if not setores:
                print(Cores.erro("Nenhum setor disponível!"))
                pausar()
                continue
            
            print("\nEscolha o setor:")
            for i, setor in enumerate(setores, 1):
                print(f"   {i}. {setor}")
            
            try:
                idx = int(input("Número do setor: ")) - 1
                if 0 <= idx < len(setores):
                    setor_atual = setores[idx]
                    print(Cores.sucesso(f"✅ Setor alterado para: {setor_atual}"))
                else:
                    print(Cores.erro("Número inválido!"))
            except ValueError:
                print(Cores.erro("Digite um número válido!"))
        
        elif opcao == '2':
            # Criar novo setor
            novo_setor = input("Nome do novo setor: ").strip().upper()
            
            if not novo_setor:
                print(Cores.erro("Nome inválido!"))
                pausar()
                continue
            
            if novo_setor in setores:
                print(Cores.erro("Setor já existe!"))
                pausar()
                continue
            
            setores.append(novo_setor)
            db.salvar_setores(setores)
            print(Cores.sucesso(f"✅ Setor '{novo_setor}' criado!"))
        
        elif opcao == '3':
            # Renomear setor
            if not setores:
                print(Cores.erro("Nenhum setor para renomear!"))
                pausar()
                continue
            
            print("\nEscolha o setor para renomear:")
            for i, setor in enumerate(setores, 1):
                print(f"   {i}. {setor}")
            
            try:
                idx = int(input("Número do setor: ")) - 1
                if 0 <= idx < len(setores):
                    setor_antigo = setores[idx]
                    novo_nome = input(f"Novo nome para '{setor_antigo}': ").strip().upper()
                    
                    if novo_nome and novo_nome not in setores:
                        # Renomeia no arquivo de setores
                        setores[idx] = novo_nome
                        db.salvar_setores(setores)
                        
                        # Renomeia nos produtos
                        produtos = db.carregar_produtos()
                        for p in produtos:
                            if p.setor == setor_antigo:
                                p.setor = novo_nome
                        db.salvar_produtos(produtos)
                        
                        if setor_atual == setor_antigo:
                            setor_atual = novo_nome
                        
                        print(Cores.sucesso(f"✅ Setor renomeado para '{novo_nome}'!"))
                    else:
                        print(Cores.erro("Nome inválido ou já existe!"))
                else:
                    print(Cores.erro("Número inválido!"))
            except ValueError:
                print(Cores.erro("Digite um número válido!"))
        
        elif opcao == '4':
            # Excluir setor (apenas se vazio)
            if not setores:
                print(Cores.erro("Nenhum setor para excluir!"))
                pausar()
                continue
            
            print("\nEscolha o setor para excluir:")
            for i, setor in enumerate(setores, 1):
                print(f"   {i}. {setor}")
            
            try:
                idx = int(input("Número do setor: ")) - 1
                if 0 <= idx < len(setores):
                    setor_excluir = setores[idx]
                    
                    # Verifica se há produtos no setor
                    produtos = db.carregar_produtos(setor_excluir)
                    
                    if produtos:
                        print(Cores.erro(f"Não é possível excluir: setor tem {len(produtos)} produto(s)!"))
                        print("Transfira os produtos para outro setor primeiro.")
                    else:
                        if confirmar(f"Excluir setor '{setor_excluir}'?"):
                            setores.remove(setor_excluir)
                            db.salvar_setores(setores)
                            
                            if setor_atual == setor_excluir:
                                setor_atual = None if setores else None
                            
                            print(Cores.sucesso(f"✅ Setor '{setor_excluir}' excluído!"))
                else:
                    print(Cores.erro("Número inválido!"))
            except ValueError:
                print(Cores.erro("Digite um número válido!"))
        
        elif opcao == '0':
            break
        
        pausar()