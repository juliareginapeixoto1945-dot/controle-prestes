#!/usr/bin/env python3
# ============================================
# WEB APP - CONTROLE DE PRESTES
# Versão Web com Flask - VERSÃO FINAL CORRIGIDA
# ============================================
import os
import sys
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_cors import CORS
from datetime import datetime, date
import json

# === CONFIGURAÇÃO DE CAMINHOS ABSOLUTOS ===
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMPLATE_DIR = os.path.join(BASE_DIR, 'frontend', 'templates')
STATIC_DIR = os.path.join(BASE_DIR, 'frontend', 'static')

print(f"📁 Diretório base: {BASE_DIR}")
print(f"📁 Templates: {TEMPLATE_DIR}")
print(f"📁 Static: {STATIC_DIR}")
print(f"✅ Templates existe? {os.path.exists(TEMPLATE_DIR)}")
print(f"✅ Static existe? {os.path.exists(STATIC_DIR)}")

# Cria o app com as pastas explicitamente definidas
app = Flask(__name__, 
            template_folder=TEMPLATE_DIR,
            static_folder=STATIC_DIR)

app.secret_key = 'chave-secreta-muito-segura-para-sessao'
CORS(app)

# Configurações
app.config['DATA_DIR'] = os.path.join(BASE_DIR, 'data')
app.config['BASE_DIR'] = BASE_DIR

# Adiciona diretório raiz ao path para imports
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

# Importa módulos
from backend.core.database import Database
from backend.core.models import Produto
from backend.core.busca_ean import BuscaEAN
from backend.modules import prestes
from backend.modules import falta, estatisticas, excluir, quantidade, listagem
from backend.modules import cadastro_com_bip_v2
from backend.core.auth import verificar_senha, definir_senha, setor_tem_senha

# Sessão temporária para produtos bipados
bip_temp_produtos = []

# ============================================
# FUNÇÃO AUXILIAR - VERIFICAR SE PRODUTO ESTÁ RETIRADO
# ============================================
def produto_esta_retirado(ean: str, setor: str, validade: date = None) -> bool:
    """
    Verifica se um produto específico está na lista de prestes retirados
    Agora considera a data de validade para não remover produtos diferentes
    """
    from backend.modules.prestes import carregar_prestes_retirados
    
    prestes_retirados = carregar_prestes_retirados()
    validade_str = validade.strftime("%m/%Y") if validade else None
    
    for r in prestes_retirados:
        if r['ean'] == ean and r['setor'] == setor:
            # Se o registro tem validade, compara com a do produto
            if r.get('validade'):
                if r['validade'] == validade_str:
                    return True
            else:
                # Registro antigo sem validade - considera retirado
                return True
    return False

def remover_da_lista_prestes_retirados(ean: str, setor: str, validade: date = None, descricao: str = None):
    """
    Remove um produto específico da lista de prestes retirados.
    Se validade for fornecida, remove apenas o produto exato.
    """
    from backend.modules.prestes import carregar_prestes_retirados, salvar_prestes_retirados
    
    prestes_retirados = carregar_prestes_retirados()
    validade_str = validade.strftime("%m/%Y") if validade else None
    
    novos_retirados = []
    removidos = 0
    
    for r in prestes_retirados:
        if r['ean'] == ean and r['setor'] == setor:
            # Se tem validade e coincide, remove
            if validade_str and r.get('validade') == validade_str:
                removidos += 1
                print(f"✅ Removido registro específico: {ean} - {validade_str}")
                continue
            # Se não tem validade (registro antigo), remove também
            elif not validade_str and not r.get('validade'):
                removidos += 1
                print(f"✅ Removido registro antigo: {ean}")
                continue
        novos_retirados.append(r)
    
    if removidos > 0:
        salvar_prestes_retirados(novos_retirados)
        return True
    return False

# ============================================
# PÁGINAS HTML
# ============================================
@app.route('/')
def index():
    """Página inicial - seleção de setor"""
    db = Database()
    setores = db.carregar_setores()
    return render_template('index.html', setores=setores)

@app.route('/setor/<setor>')
def setor_main(setor):
    """Menu principal do setor"""
    session['setor_atual'] = setor
    return render_template('main.html', setor=setor)

@app.route('/falta')
def pagina_falta():
    return render_template('falta.html')

@app.route('/estatisticas')
def pagina_estatisticas():
    return render_template('estatisticas.html')

@app.route('/excluir')
def pagina_excluir():
    return render_template('excluir.html')

@app.route('/quantidade')
def pagina_quantidade():
    return render_template('quantidade.html')

@app.route('/erros')
def pagina_erros():
    return render_template('erros.html')

@app.route('/bip')
def pagina_bip():
    """Página do modo bip"""
    return render_template('cadastro_bip.html')

@app.route('/codigos')
def pagina_codigos():
    """Página com códigos de validade"""
    from backend.modules.gerar_codigos import gerar_html_codigos
    html = gerar_html_codigos()
    return html

# ============================================
# PÁGINAS DE AUTENTICAÇÃO
# ============================================
@app.route('/login-setor/<setor>')
def login_setor(setor):
    """Página de login para o setor"""
    return render_template('login_setor.html', setor=setor)

@app.route('/definir-senha')
def pagina_definir_senha():
    """Página para definir/alterar senha"""
    setor = session.get('setor_atual')
    if not setor:
        return redirect('/')
    tem_senha = setor_tem_senha(setor)
    return render_template('definir_senha.html', setor=setor, tem_senha=tem_senha)

# ============================================
# API - SETORES
# ============================================
@app.route('/api/setores', methods=['GET'])
def api_listar_setores():
    """Retorna lista de setores"""
    db = Database()
    setores = db.carregar_setores()
    return jsonify({'setores': setores})

@app.route('/api/setores/novo', methods=['POST'])
def api_criar_setor():
    """Cria novo setor"""
    data = request.json
    novo_setor = data.get('setor', '').upper().strip()
    
    if not novo_setor:
        return jsonify({'erro': 'Nome inválido'}), 400
    
    db = Database()
    setores = db.carregar_setores()
    
    if novo_setor in setores:
        return jsonify({'erro': 'Setor já existe'}), 400
    
    setores.append(novo_setor)
    if db.salvar_setores(setores):
        return jsonify({'sucesso': True, 'setor': novo_setor})
    else:
        return jsonify({'erro': 'Erro ao salvar'}), 500

# ============================================
# API - AUTENTICAÇÃO
# ============================================
@app.route('/api/verificar-senha-setor', methods=['POST'])
def api_verificar_senha_setor():
    """Verifica se a senha do setor está correta"""
    data = request.json
    setor = data.get('setor')
    senha = data.get('senha', '')
    
    if not setor:
        return jsonify({'erro': 'Setor não informado'}), 400
    
    if verificar_senha(setor, senha):
        # Se a senha estiver correta, já cria a sessão
        session['setor_atual'] = setor
        return jsonify({'sucesso': True})
    else:
        return jsonify({'erro': 'Senha incorreta'}), 401

@app.route('/api/definir-senha-setor', methods=['POST'])
def api_definir_senha_setor():
    """Define ou altera a senha de um setor"""
    setor = session.get('setor_atual')
    if not setor:
        return jsonify({'erro': 'Setor não selecionado'}), 400
    
    data = request.json
    nova_senha = data.get('senha', '')
    
    if definir_senha(setor, nova_senha):
        if nova_senha:
            mensagem = "Senha definida com sucesso!"
        else:
            mensagem = "Proteção por senha removida!"
        return jsonify({'sucesso': True, 'mensagem': mensagem})
    else:
        return jsonify({'erro': 'Erro ao salvar senha'}), 500

@app.route('/api/verificar-necessidade-senha/<setor>', methods=['GET'])
def api_verificar_necessidade_senha(setor):
    """Verifica se o setor precisa de senha para acesso"""
    precisa = setor_tem_senha(setor)
    return jsonify({'precisa_senha': precisa})

# ============================================
# API - PRODUTOS
# ============================================
@app.route('/api/produtos', methods=['GET'])
def api_listar_produtos():
    """Lista TODOS os produtos do setor (PRESTES RETIRADOS NÃO APARECEM)"""
    setor = session.get('setor_atual')
    if not setor:
        return jsonify({'erro': 'Setor não selecionado'}), 400
    
    db = Database()
    todos_produtos = db.carregar_produtos(setor)
    
    # Filtra apenas os que NÃO estão retirados
    produtos_filtrados = []
    
    for p in todos_produtos:
        if not produto_esta_retirado(p.ean, setor, p.validade):
            # Define status e classe para exibição
            from backend.modules.falta import produto_esta_em_falta
            faltas = Database.carregar_faltas()
            em_falta = produto_esta_em_falta(p.descricao, faltas)
            
            if em_falta:
                status_texto = "FALTA"
                status_class = "table-secondary"
            elif p.esta_vencido:
                status_texto = "VENCIDO"
                status_class = "table-danger"
            elif p.esta_prestes:
                status_texto = f"PRESTES ({p.dias_para_vencer})"
                status_class = "table-warning"
            else:
                status_texto = "OK"
                status_class = "table-success"
            
            produtos_filtrados.append({
                'ean': p.ean,
                'descricao': p.descricao,
                'validade': p.mes_ano,
                'dias': p.dias_para_vencer,
                'status': status_texto,
                'status_class': status_class
            })
    
    return jsonify({'produtos': produtos_filtrados})

@app.route('/api/produtos/ativos', methods=['GET'])
def api_listar_produtos_ativos():
    """Lista apenas produtos ATIVOS (não em falta, não retirados)"""
    setor = session.get('setor_atual')
    if not setor:
        return jsonify({'erro': 'Setor não selecionado'}), 400
    
    db = Database()
    todos_produtos = db.carregar_produtos(setor)
    faltas = Database.carregar_faltas()
    
    from backend.modules.falta import produto_esta_em_falta
    
    produtos_ativos = []
    
    for p in todos_produtos:
        em_falta = produto_esta_em_falta(p.descricao, faltas)
        retirado = produto_esta_retirado(p.ean, setor, p.validade)
        
        if not em_falta and not retirado:
            produtos_ativos.append({
                'ean': p.ean,
                'descricao': p.descricao,
                'validade': p.mes_ano,
                'dias': p.dias_para_vencer,
                'status': 'vencido' if p.esta_vencido else 'prestes' if p.esta_prestes else 'ok'
            })
    
    return jsonify({'produtos': produtos_ativos})

@app.route('/api/produtos/buscar/<ean>', methods=['GET'])
def api_buscar_produto(ean):
    """Busca produto por EAN (local ou internet)"""
    setor = session.get('setor_atual')
    if not setor:
        return jsonify({'erro': 'Setor não selecionado'}), 400
    
    db = Database()
    produtos = db.carregar_produtos(setor)
    
    # Busca no banco local primeiro
    for p in produtos:
        if p.ean == ean:
            return jsonify({
                'encontrado': True,
                'descricao': p.descricao,
                'validade': p.mes_ano,
                'fonte': 'local'
            })
    
    # Se não encontrou, busca no cache de EANs
    buscador = BuscaEAN()
    descricao = buscador.buscar(ean, tentar_online=True)
    
    if descricao:
        return jsonify({
            'encontrado': True,
            'descricao': descricao,
            'fonte': 'cache'
        })
    else:
        return jsonify({'encontrado': False})

@app.route('/api/produtos/adicionar', methods=['POST'])
def api_adicionar_produto():
    """Adiciona um novo produto - CORRIGIDO: remove da lista de prestes retirados"""
    setor = session.get('setor_atual')
    if not setor:
        return jsonify({'erro': 'Setor não selecionado'}), 400
    
    data = request.json
    ean = data.get('ean')
    descricao = data.get('descricao')
    mes = data.get('mes')
    ano = data.get('ano')
    
    if not all([ean, descricao, mes, ano]):
        return jsonify({'erro': 'Dados incompletos'}), 400
    
    try:
        data_validade = date(int(ano), int(mes), 1)
        
        db = Database()
        todos_produtos = db.carregar_produtos()
        
        # ========== CORREÇÃO IMPORTANTE ==========
        # Remove da lista de prestes retirados (específico)
        remover_da_lista_prestes_retirados(ean, setor, data_validade, descricao)
        
        novo_produto = Produto(
            ean=ean,
            descricao=descricao,
            validade=data_validade,
            status='ativo',
            setor=setor
        )
        
        todos_produtos.append(novo_produto)
        
        if db.salvar_produtos(todos_produtos):
            return jsonify({'sucesso': True})
        else:
            return jsonify({'erro': 'Erro ao salvar'}), 500
    
    except Exception as e:
        return jsonify({'erro': str(e)}), 500

@app.route('/api/produtos/prestes', methods=['GET'])
def api_produtos_prestes():
    """Lista produtos prestes a vencer (excluindo em falta e retirados)"""
    setor = session.get('setor_atual')
    if not setor:
        return jsonify({'erro': 'Setor não selecionado'}), 400
    
    db = Database()
    produtos = db.carregar_produtos(setor)
    faltas = Database.carregar_faltas()
    
    from backend.modules.falta import produto_esta_em_falta
    
    prestes_lista = []
    
    for p in produtos:
        em_falta = produto_esta_em_falta(p.descricao, faltas)
        retirado = produto_esta_retirado(p.ean, setor, p.validade)
        
        if p.esta_prestes and not em_falta and not retirado:
            if p.dias_para_vencer <= 15:
                desconto = "50%"
            elif p.dias_para_vencer <= 30:
                desconto = "30%"
            elif p.dias_para_vencer <= 60:
                desconto = "20%"
            else:
                desconto = "10%"
            
            prestes_lista.append({
                'ean': p.ean,
                'descricao': p.descricao,
                'validade': p.mes_ano,
                'dias': p.dias_para_vencer,
                'desconto': desconto
            })
    
    return jsonify({'prestes': prestes_lista, 'total': len(prestes_lista)})

@app.route('/api/produtos/retirar-prestes', methods=['POST'])
def api_retirar_prestes():
    """Marca produtos como prestes retirados"""
    setor = session.get('setor_atual')
    if not setor:
        return jsonify({'erro': 'Setor não selecionado'}), 400
    
    data = request.json
    eans = data.get('eans', [])
    
    if not eans:
        return jsonify({'erro': 'Nenhum produto selecionado'}), 400
    
    db = Database()
    produtos = db.carregar_produtos(setor)
    
    from backend.modules.prestes import adicionar_prestes_retirados
    
    for ean in eans:
        # Encontra a descrição e validade do produto
        for p in produtos:
            if p.ean == ean:
                adicionar_prestes_retirados(
                    ean, setor, p.descricao,
                    date.today().strftime("%d/%m/%Y"),
                    p.mes_ano
                )
                break
    
    return jsonify({'sucesso': True, 'quantidade': len(eans)})

# ============================================
# API - PRECIFICAÇÃO (TIRAR PREÇO)
# ============================================
@app.route('/api/precificacao/eans', methods=['GET'])
def api_eans_precificacao():
    """Retorna lista de EANs para precificação - FUNÇÃO TIRAR PREÇO"""
    setor = session.get('setor_atual')
    if not setor:
        return jsonify({'erro': 'Setor não selecionado'}), 400
    
    db = Database()
    produtos = db.carregar_produtos(setor)
    faltas = Database.carregar_faltas()
    
    from backend.modules.falta import produto_esta_em_falta
    
    eans_unicos = set()
    for p in produtos:
        em_falta = produto_esta_em_falta(p.descricao, faltas)
        retirado = produto_esta_retirado(p.ean, setor, p.validade)
        
        # Inclui apenas produtos ativos (não em falta, não retirados)
        if not em_falta and not retirado and p.status == 'ativo':
            eans_unicos.add(p.ean)
    
    return jsonify({'eans': sorted(list(eans_unicos))})

# ============================================
# API - PESQUISA POR DATA
# ============================================
@app.route('/api/produtos/pesquisar', methods=['POST'])
def api_pesquisar_produtos():
    """Pesquisa produtos por período"""
    setor = session.get('setor_atual')
    if not setor:
        return jsonify({'erro': 'Setor não selecionado'}), 400
    
    data = request.json
    data_inicial = data.get('data_inicial')
    data_final = data.get('data_final')
    
    try:
        if data_inicial:
            data_inicial = datetime.strptime(data_inicial, "%Y-%m-%d").date()
        if data_final:
            data_final = datetime.strptime(data_final, "%Y-%m-%d").date()
    except:
        return jsonify({'erro': 'Formato de data inválido'}), 400
    
    db = Database()
    produtos = db.carregar_produtos(setor)
    
    resultados = []
    for p in produtos:
        if not hasattr(p, 'data_cadastro') or p.data_cadastro is None:
            p.data_cadastro = date.today()
        
        incluir = True
        if data_inicial and p.data_cadastro < data_inicial:
            incluir = False
        if data_final and p.data_cadastro > data_final:
            incluir = False
        
        if incluir:
            resultados.append({
                'ean': p.ean,
                'descricao': p.descricao,
                'validade': p.mes_ano,
                'data_cadastro': p.data_cadastro.strftime("%d/%m/%Y"),
                'dias': p.dias_para_vencer
            })
    
    return jsonify({'resultados': resultados})

# ============================================
# API - FALTA
# ============================================
@app.route('/api/falta', methods=['GET'])
def api_listar_falta():
    """Retorna lista de produtos em falta"""
    faltas = Database.carregar_faltas()
    return jsonify({'faltas': faltas})

@app.route('/api/falta/adicionar', methods=['POST'])
def api_adicionar_falta():
    """Adiciona produto à lista de falta"""
    data = request.json
    descricao = data.get('descricao', '').strip()
    
    if not descricao:
        return jsonify({'erro': 'Descrição inválida'}), 400
    
    from backend.modules.falta import adicionar_falta
    if adicionar_falta(descricao):
        return jsonify({'sucesso': True})
    else:
        return jsonify({'erro': 'Produto já está na lista'}), 400

@app.route('/api/falta/remover', methods=['POST'])
def api_remover_falta():
    """Remove produto da lista de falta"""
    data = request.json
    descricao = data.get('descricao', '').strip()
    
    if not descricao:
        return jsonify({'erro': 'Descrição inválida'}), 400
    
    from backend.modules.falta import remover_falta
    if remover_falta(descricao):
        return jsonify({'sucesso': True})
    else:
        return jsonify({'erro': 'Produto não encontrado'}), 400

@app.route('/api/falta/limpar', methods=['POST'])
def api_limpar_falta():
    """Limpa toda a lista de falta"""
    from backend.modules.falta import limpar_faltas
    if limpar_faltas():
        return jsonify({'sucesso': True})
    else:
        return jsonify({'erro': 'Erro ao limpar'}), 500

# ============================================
# API - ESTATÍSTICAS
# ============================================
@app.route('/api/estatisticas', methods=['GET'])
def api_estatisticas():
    """Retorna estatísticas do setor"""
    setor = session.get('setor_atual')
    if not setor:
        return jsonify({'erro': 'Setor não selecionado'}), 400
    
    db = Database()
    produtos = db.carregar_produtos(setor)
    faltas = Database.carregar_faltas()
    
    from backend.modules.falta import produto_esta_em_falta
    
    hoje = date.today()
    
    vencidos = 0
    prestes = 0
    ok = 0
    em_falta_count = 0
    retirados_count = 0
    
    produtos_vencidos = []
    produtos_prestes = []
    produtos_em_falta = []
    
    for p in produtos:
        em_falta = produto_esta_em_falta(p.descricao, faltas)
        retirado = produto_esta_retirado(p.ean, setor, p.validade)
        
        if retirado:
            retirados_count += 1
            continue
        
        if em_falta:
            em_falta_count += 1
            produtos_em_falta.append({
                'ean': p.ean,
                'descricao': p.descricao,
                'validade': p.mes_ano,
                'dias': p.dias_para_vencer
            })
        
        if p.esta_vencido:
            vencidos += 1
            if not em_falta:
                produtos_vencidos.append({
                    'ean': p.ean,
                    'descricao': p.descricao,
                    'validade': p.mes_ano,
                    'dias': p.dias_para_vencer
                })
        elif p.esta_prestes:
            prestes += 1
            if not em_falta:
                produtos_prestes.append({
                    'ean': p.ean,
                    'descricao': p.descricao,
                    'validade': p.mes_ano,
                    'dias': p.dias_para_vencer
                })
        else:
            if not em_falta:
                ok += 1
    
    produtos_prestes.sort(key=lambda x: x['dias'])
    produtos_vencidos.sort(key=lambda x: x['dias'])
    
    total_ativo = len(produtos) - retirados_count
    
    return jsonify({
        'total': total_ativo,
        'ativos': total_ativo - em_falta_count,
        'em_falta': em_falta_count,
        'vencidos': vencidos,
        'prestes': prestes,
        'ok': ok,
        'prestes_retirados': retirados_count,
        'dias_prestes': 90,
        'lista_vencidos': produtos_vencidos[:10],
        'lista_prestes': produtos_prestes[:10],
        'lista_falta': produtos_em_falta[:10]
    })

# ============================================
# API - EXCLUSÃO
# ============================================
@app.route('/api/produtos/excluir/ean', methods=['POST'])
def api_excluir_por_ean():
    """Exclui produto por EAN"""
    setor = session.get('setor_atual')
    if not setor:
        return jsonify({'erro': 'Setor não selecionado'}), 400
    
    data = request.json
    ean = data.get('ean', '').strip()
    
    if not ean:
        return jsonify({'erro': 'EAN inválido'}), 400
    
    from backend.modules.excluir import excluir_por_ean
    sucesso, mensagem, produto = excluir_por_ean(ean, setor)
    
    if sucesso:
        return jsonify({
            'sucesso': True,
            'mensagem': mensagem,
            'produto': {
                'ean': produto.ean,
                'descricao': produto.descricao,
                'validade': produto.mes_ano
            } if produto else None
        })
    else:
        return jsonify({'erro': mensagem}), 404

@app.route('/api/produtos/excluir/descricao', methods=['POST'])
def api_excluir_por_descricao():
    """Exclui produtos por descrição"""
    setor = session.get('setor_atual')
    if not setor:
        return jsonify({'erro': 'Setor não selecionado'}), 400
    
    data = request.json
    termo = data.get('termo', '').strip()
    
    if not termo or len(termo) < 3:
        return jsonify({'erro': 'Digite pelo menos 3 caracteres'}), 400
    
    from backend.modules.excluir import excluir_por_descricao
    sucesso, mensagem, quantidade, produtos = excluir_por_descricao(termo, setor)
    
    if sucesso:
        return jsonify({
            'sucesso': True,
            'mensagem': mensagem,
            'quantidade': quantidade
        })
    else:
        return jsonify({'erro': mensagem}), 404

@app.route('/api/produtos/excluir/todos', methods=['POST'])
def api_excluir_todos_setor():
    """Exclui todos os produtos do setor"""
    setor = session.get('setor_atual')
    if not setor:
        return jsonify({'erro': 'Setor não selecionado'}), 400
    
    from backend.modules.excluir import excluir_todos_setor
    sucesso, mensagem, quantidade = excluir_todos_setor(setor)
    
    if sucesso:
        return jsonify({
            'sucesso': True,
            'mensagem': mensagem,
            'quantidade': quantidade
        })
    else:
        return jsonify({'erro': mensagem}), 400

# ============================================
# API - QUANTIDADE
# ============================================
@app.route('/api/produtos/adicionar-quantidade', methods=['POST'])
def api_adicionar_quantidade():
    """Adiciona quantidade a produto existente"""
    setor = session.get('setor_atual')
    if not setor:
        return jsonify({'erro': 'Setor não selecionado'}), 400
    
    data = request.json
    ean = data.get('ean')
    mes = data.get('mes')
    ano = data.get('ano')
    quantidade = data.get('quantidade', 1)
    
    if not all([ean, mes, ano]):
        return jsonify({'erro': 'Dados incompletos'}), 400
    
    from backend.modules.quantidade import adicionar_quantidade
    sucesso, mensagem = adicionar_quantidade(ean, setor, int(mes), int(ano), int(quantidade))
    
    if sucesso:
        return jsonify({'sucesso': True, 'mensagem': mensagem})
    else:
        return jsonify({'erro': mensagem}), 400

# ============================================
# API - ERROS DO BIP
# ============================================
@app.route('/api/erros', methods=['GET'])
def api_listar_erros():
    """Lista erros do bip"""
    setor = session.get('setor_atual')
    if not setor:
        return jsonify({'erro': 'Setor não selecionado'}), 400
    
    from backend.modules.cadastro_com_bip_v2 import carregar_erros
    erros = carregar_erros()
    erros_setor = [e for e in erros if e['setor'] == setor]
    
    return jsonify({'erros': erros_setor})

@app.route('/api/erros/resolver', methods=['POST'])
def api_resolver_erro():
    """Resolve um erro específico"""
    setor = session.get('setor_atual')
    if not setor:
        return jsonify({'erro': 'Setor não selecionado'}), 400
    
    data = request.json
    ean = data.get('ean')
    descricao = data.get('descricao')
    mes = data.get('mes')
    ano = data.get('ano')
    
    if not all([ean, descricao, mes, ano]):
        return jsonify({'erro': 'Dados incompletos'}), 400
    
    try:
        data_validade = date(int(ano), int(mes), 1)
        db = Database()
        todos_produtos = db.carregar_produtos()
        
        # Remove da lista de prestes retirados
        remover_da_lista_prestes_retirados(ean, setor, data_validade, descricao)
        
        novo_produto = Produto(
            ean=ean,
            descricao=descricao,
            validade=data_validade,
            status='ativo',
            setor=setor
        )
        
        todos_produtos.append(novo_produto)
        
        if db.salvar_produtos(todos_produtos):
            # Remove o erro da lista
            from backend.modules.cadastro_com_bip_v2 import carregar_erros, salvar_erros
            erros = carregar_erros()
            novos_erros = [e for e in erros if not (e['ean'] == ean and e['setor'] == setor)]
            salvar_erros(novos_erros)
            
            return jsonify({'sucesso': True})
        else:
            return jsonify({'erro': 'Erro ao salvar'}), 500
    except Exception as e:
        return jsonify({'erro': str(e)}), 500

@app.route('/api/erros/descartar', methods=['POST'])
def api_descartar_erro():
    """Descarta um erro sem resolver"""
    setor = session.get('setor_atual')
    if not setor:
        return jsonify({'erro': 'Setor não selecionado'}), 400
    
    data = request.json
    ean = data.get('ean')
    
    if not ean:
        return jsonify({'erro': 'EAN não informado'}), 400
    
    from backend.modules.cadastro_com_bip_v2 import carregar_erros, salvar_erros
    erros = carregar_erros()
    novos_erros = [e for e in erros if not (e['ean'] == ean and e['setor'] == setor)]
    salvar_erros(novos_erros)
    
    return jsonify({'sucesso': True})

# ============================================
# API - BIP (CADASTRO RÁPIDO)
# ============================================
@app.route('/api/codigos-validade', methods=['GET'])
def api_codigos_validade():
    """Retorna todos os códigos de validade"""
    from backend.modules.gerar_codigos import gerar_todos_codigos
    return jsonify(gerar_todos_codigos())

@app.route('/api/bip/processar', methods=['POST'])
def api_processar_bip():
    """Processa um código bipado"""
    data = request.json
    codigo = data.get('codigo', '')
    
    from backend.modules.cadastro_com_bip_v2 import processar_bip_produto
    resultado = processar_bip_produto(session.get('setor_atual'), codigo)
    
    return jsonify(resultado)

@app.route('/api/bip/cancelar', methods=['POST'])
def api_cancelar_produto():
    """Cancela o último produto bipado"""
    setor = session.get('setor_atual')
    if not setor:
        return jsonify({'erro': 'Setor não selecionado'}), 400
    
    data = request.json
    ean = data.get('ean')
    
    if not ean:
        return jsonify({'erro': 'EAN não informado'}), 400
    
    from backend.modules.cadastro_com_bip_v2 import cancelar_ultimo_produto
    sucesso, mensagem, produto = cancelar_ultimo_produto(setor, ean)
    
    if sucesso:
        # Remove da lista temporária também
        global bip_temp_produtos
        bip_temp_produtos = [p for p in bip_temp_produtos if not (p['ean'] == ean)]
        
        return jsonify({'sucesso': True, 'mensagem': mensagem})
    else:
        return jsonify({'erro': mensagem}), 400

@app.route('/api/produtos/adicionar-bip', methods=['POST'])
def api_adicionar_produto_bip():
    """Adiciona produto vindo do modo bip - CORRIGIDO"""
    setor = session.get('setor_atual')
    if not setor:
        return jsonify({'erro': 'Setor não selecionado'}), 400
    
    data = request.json
    ean = data.get('ean')
    mes = data.get('mes')
    ano = data.get('ano')
    descricao = data.get('descricao')
    
    if not all([ean, mes, ano]):
        return jsonify({'erro': 'Dados incompletos'}), 400
    
    try:
        data_validade = date(int(ano), int(mes), 1)
        
        # Se não tem descrição, tenta buscar
        if not descricao:
            from backend.core.busca_ean import BuscaEAN
            buscador = BuscaEAN()
            descricao = buscador.buscar(ean, tentar_online=True)
        
        if not descricao:
            return jsonify({'erro': 'Descrição não encontrada'}), 400
        
        db = Database()
        todos_produtos = db.carregar_produtos()
        
        # Remove da lista de prestes retirados
        remover_da_lista_prestes_retirados(ean, setor, data_validade, descricao)
        
        novo_produto = Produto(
            ean=ean,
            descricao=descricao,
            validade=data_validade,
            status='ativo',
            setor=setor
        )
        
        todos_produtos.append(novo_produto)
        
        if db.salvar_produtos(todos_produtos):
            # Adiciona à lista temporária
            global bip_temp_produtos
            bip_temp_produtos.append({
                'ean': ean,
                'descricao': descricao,
                'validade': f"{mes:02d}/{ano}"
            })
            
            return jsonify({
                'sucesso': True,
                'produto': {
                    'ean': ean,
                    'descricao': descricao,
                    'validade': f"{mes:02d}/{ano}"
                }
            })
        else:
            return jsonify({'erro': 'Erro ao salvar'}), 500
    
    except Exception as e:
        return jsonify({'erro': str(e)}), 500

@app.route('/api/produtos-bip-temp', methods=['GET'])
def api_produtos_bip_temp():
    """Retorna produtos da sessão atual de bip"""
    global bip_temp_produtos
    return jsonify({'produtos': bip_temp_produtos[-10:]})  # Últimos 10

# ============================================
# INICIALIZAÇÃO (para desenvolvimento local)
# ============================================
if __name__ == '__main__':
    os.makedirs(app.config['DATA_DIR'], exist_ok=True)
    print("\n" + "=" * 60)
    print("🚀 CONTROLE DE PRESTES - WEB APP")
    print("=" * 60)
    print("\n✅ Configuração de pastas:")
    print(f"   Templates: {TEMPLATE_DIR}")
    print(f"   Static: {STATIC_DIR}")
    print(f"   Data: {app.config['DATA_DIR']}")
    print("\n📱 Acesse: http://localhost:5000")
    print("\n🔴 Pressione CTRL+C para parar")
    print("=" * 60)
    app.run(host='0.0.0.0', port=5000, debug=True)