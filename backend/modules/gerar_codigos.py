# ============================================
# GERADOR DE CÓDIGOS DE VALIDADE - WEB VERSION
# ============================================

import os
from datetime import datetime
from pathlib import Path
import base64
from io import BytesIO

from ..core.validadores import calcular_dv_ean13
from ..core.config import DATA_DIR

def gerar_todos_codigos():
    """
    Gera todos os códigos de validade e retorna em formato JSON
    """
    meses = []
    anos = []
    
    # Gera códigos dos meses
    for mes in range(1, 13):
        codigo_base = f"78991{mes:02d}000"
        codigo_completo = calcular_dv_ean13(codigo_base)
        
        meses.append({
            'mes': mes,
            'codigo': codigo_completo,
            'nome': get_nome_mes(mes),
            'codigo_12': codigo_base,
            'codigo_13': codigo_completo
        })
    
    # Gera códigos dos anos
    for ano in range(2026, 2033):
        codigo_base = f"78992{ano}0"
        codigo_completo = calcular_dv_ean13(codigo_base)
        
        anos.append({
            'ano': ano,
            'codigo': codigo_completo,
            'codigo_12': codigo_base,
            'codigo_13': codigo_completo
        })
    
    # Gera código de cancelar
    codigo_cancelar_base = "78999000000"
    codigo_cancelar = calcular_dv_ean13(codigo_cancelar_base)
    
    return {
        'meses': meses,
        'anos': anos,
        'cancelar': codigo_cancelar,
        'data_geracao': datetime.now().strftime("%d/%m/%Y %H:%M")
    }

def get_nome_mes(mes: int) -> str:
    """Retorna o nome do mês"""
    meses = [
        "Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
        "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"
    ]
    return meses[mes-1]

def gerar_imagem_base64(codigo):
    """
    Gera imagem do código de barras em base64
    Retorna string base64 para usar direto no HTML
    """
    try:
        import barcode
        from barcode.writer import ImageWriter
        
        # Configurar writer
        writer = ImageWriter()
        writer.dpi = 300
        writer.module_width = 0.2
        writer.module_height = 15.0
        writer.font_size = 8
        writer.text_distance = 2
        writer.quiet_zone = 2
        
        # Gerar código
        ean = barcode.get_barcode_class('ean13')
        codigo_barras = ean(codigo, writer=writer)
        
        # Renderizar para bytes
        buffer = BytesIO()
        codigo_barras.write(buffer)
        buffer.seek(0)
        
        # Converter para base64
        img_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
        
        return f"data:image/png;base64,{img_base64}"
        
    except ImportError:
        return None
    except Exception as e:
        print(f"Erro ao gerar imagem: {e}")
        return None

def gerar_html_codigos() -> str:
    """
    Gera HTML completo com imagens dos códigos de barras
    """
    dados = gerar_todos_codigos()
    
    # Gerar imagens base64
    for mes in dados['meses']:
        mes['img'] = gerar_imagem_base64(mes['codigo_13'])
    
    for ano in dados['anos']:
        ano['img'] = gerar_imagem_base64(ano['codigo_13'])
    
    img_cancelar = gerar_imagem_base64(dados['cancelar'])
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>Códigos de Validade - Controle de Prestes</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                margin: 20px;
                background: white;
            }}
            @page {{
                size: A4;
                margin: 1.5cm;
            }}
            .pagina {{
                page-break-after: always;
            }}
            h1 {{
                color: #2c3e50;
                font-size: 24px;
                text-align: center;
                margin-bottom: 10px;
            }}
            h2 {{
                color: #34495e;
                font-size: 20px;
                border-bottom: 2px solid #3498db;
                padding-bottom: 5px;
                margin-top: 30px;
            }}
            .instrucoes {{
                background: #f8f9fa;
                border-left: 5px solid #28a745;
                padding: 15px;
                margin: 20px 0;
                font-size: 14px;
            }}
            .cancelar {{
                background: #f8d7da;
                border-left: 5px solid #dc3545;
                padding: 15px;
                margin: 20px 0;
                font-size: 14px;
            }}
            .tabela-codigos {{
                width: 100%;
                border-collapse: collapse;
                margin: 20px 0;
            }}
            .tabela-codigos td {{
                border: 1px solid #ddd;
                padding: 10px;
                text-align: center;
                vertical-align: middle;
                width: 33%;
            }}
            .codigo-barras img {{
                width: 100%;
                max-width: 280px;
                height: auto;
                image-rendering: crisp-edges;
            }}
            .descricao {{
                font-weight: bold;
                font-size: 16px;
                margin-top: 10px;
            }}
            .ean {{
                font-family: 'Courier New', monospace;
                font-size: 14px;
                color: #7f8c8d;
            }}
            .exemplo {{
                background: #fff3cd;
                border: 1px solid #ffeeba;
                padding: 15px;
                border-radius: 5px;
                margin-top: 20px;
            }}
        </style>
    </head>
    <body>
        <!-- PÁGINA 1: MESES -->
        <div class="pagina">
            <h1>CONTROLE DE PRESTES</h1>
            <h2>CÓDIGOS DE VALIDADE - MESES</h2>
            
            <div class="instrucoes">
                <strong>INSTRUÇÕES:</strong> Bipe o código do PRODUTO + MÊS + ANO<br>
                <small>Gerado em: {dados['data_geracao']}</small>
            </div>
            
            <table class="tabela-codigos">
    """
    
    # Adicionar meses (3 colunas)
    for i in range(0, 12, 3):
        html += "                <tr>\n"
        for j in range(3):
            if i + j < 12:
                mes = dados['meses'][i + j]
                html += f"""                    <td>
                        <div class="codigo-barras">
                            <img src="{mes['img']}" alt="{mes['nome']}">
                        </div>
                        <div class="descricao">{mes['nome']}</div>
                        <div class="ean">{mes['codigo_13']}</div>
                    </td>
"""
            else:
                html += "                    <td></td>\n"
        html += "                </tr>\n"
    
    html += """            </table>
        </div>
        
        <!-- PÁGINA 2: ANOS -->
        <div class="pagina">
            <h1>CONTROLE DE PRESTES</h1>
            <h2>CÓDIGOS DE VALIDADE - ANOS</h2>
            
            <table class="tabela-codigos">
    """
    
    # Adicionar anos (3 colunas)
    for i in range(0, 7, 3):
        html += "                <tr>\n"
        for j in range(3):
            if i + j < 7:
                ano = dados['anos'][i + j]
                html += f"""                    <td>
                        <div class="codigo-barras">
                            <img src="{ano['img']}" alt="Ano {ano['ano']}">
                        </div>
                        <div class="descricao">Ano {ano['ano']}</div>
                        <div class="ean">{ano['codigo_13']}</div>
                    </td>
"""
            else:
                html += "                    <td></td>\n"
        html += "                </tr>\n"
    
    html += f"""            </table>
        </div>
        
        <!-- PÁGINA 3: CANCELAR -->
        <div class="pagina">
            <h1>CONTROLE DE PRESTES</h1>
            <h2>FUNÇÃO ESPECIAL - CANCELAR PRODUTO</h2>
            
            <div class="cancelar">
                <strong>⚠️ ATENÇÃO:</strong> Use este código para cancelar o último produto bipado!<br><br>
                <strong>COMO USAR:</strong><br>
                1. Se você errou a data de um produto, bipe este código<br>
                2. Bipe novamente o código do PRODUTO que errou<br>
                3. O produto será removido para você cadastrar novamente<br>
            </div>
            
            <table class="tabela-codigos">
                <tr>
                    <td style="background-color: #f8d7da;">
                        <div class="codigo-barras">
                            <img src="{img_cancelar}" alt="Cancelar">
                        </div>
                        <div class="descricao" style="color: #dc3545;">🚫 CANCELAR</div>
                        <div class="ean">{dados['cancelar']}</div>
                    </td>
                </tr>
            </table>
        </div>
        
        <!-- PÁGINA 4: TABELA RESUMO -->
        <div class="pagina">
            <h1>TABELA RESUMO DE CÓDIGOS</h1>
            
            <h2>MESES</h2>
            <table class="tabela-codigos">
    """
    
    # Tabela resumo meses (2 colunas)
    for i in range(0, 12, 2):
        html += "                <tr>\n"
        for j in range(2):
            if i + j < 12:
                mes = dados['meses'][i + j]
                html += f"""                    <td>
                        <div class="descricao">{mes['nome']}</div>
                        <div class="ean" style="font-size: 18px;">{mes['codigo_13']}</div>
                    </td>
"""
            else:
                html += "                    <td></td>\n"
        html += "                </tr>\n"
    
    html += """            </table>
            
            <h2>ANOS</h2>
            <table class="tabela-codigos">
    """
    
    # Tabela resumo anos (2 colunas)
    for i in range(0, 7, 2):
        html += "                <tr>\n"
        for j in range(2):
            if i + j < 7:
                ano = dados['anos'][i + j]
                html += f"""                    <td>
                        <div class="descricao">Ano {ano['ano']}</div>
                        <div class="ean" style="font-size: 18px;">{ano['codigo_13']}</div>
                    </td>
"""
            else:
                html += "                    <td></td>\n"
        html += "                </tr>\n"
    
    html += f"""            </table>
            
            <h2>FUNÇÃO ESPECIAL</h2>
            <table class="tabela-codigos">
                <tr>
                    <td style="background-color: #f8d7da;">
                        <div class="descricao" style="color: #dc3545;">🚫 CANCELAR</div>
                        <div class="ean" style="font-size: 18px;">{dados['cancelar']}</div>
                    </td>
                </tr>
            </table>
            
            <div class="exemplo">
                <strong>EXEMPLO PRÁTICO:</strong><br>
                Para cadastrar um produto com validade <strong>Janeiro/2026</strong>:<br><br>
                1. Bipe o PRODUTO: <code>7891234560012</code><br>
                2. Bipe o MÊS: <code>{dados['meses'][0]['codigo_13']}</code><br>
                3. Bipe o ANO: <code>{dados['anos'][0]['codigo_13']}</code>
            </div>
        </div>
        
        <!-- PÁGINA 5: INSTRUÇÕES -->
        <div class="pagina">
            <h1>INSTRUÇÕES DETALHADAS</h1>
            
            <div class="instrucoes" style="background: #e8f4f8;">
                <h3>📋 CADASTRO NORMAL</h3>
                <ol>
                    <li>Conecte o leitor de código de barras</li>
                    <li>Abra o sistema e escolha a opção 2</li>
                    <li>Bipe o PRODUTO</li>
                    <li>Bipe o MÊS</li>
                    <li>Bipe o ANO</li>
                    <li>Produto registrado!</li>
                </ol>
            </div>
            
            <div class="cancelar">
                <h3>🚫 CANCELAR PRODUTO</h3>
                <ol>
                    <li>Se errou a data, bipe o código CANCELAR</li>
                    <li>Bipe novamente o PRODUTO</li>
                    <li>O produto será removido</li>
                    <li>Cadastre novamente com a data correta</li>
                </ol>
            </div>
        </div>
    </body>
    </html>
    """
    
    return html