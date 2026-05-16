#!/usr/bin/env python3
# ============================================
# GERADOR DE CÓDIGOS DE BARRAS PARA WEB
# ============================================
# Gera HTML com imagens dos códigos de barras
# Baseado no seu arquivo anexado
# ============================================

import os
import sys
from datetime import datetime
import base64
from io import BytesIO

# Adiciona diretório raiz ao path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.core.config import DATA_DIR
from backend.core.validadores import calcular_dv_ean13

def gerar_codigo_mes(mes):
    """Gera código para mês"""
    return calcular_dv_ean13(f"78991{mes:02d}000")

def gerar_codigo_ano(ano):
    """Gera código para ano"""
    return calcular_dv_ean13(f"78992{ano}0")

def gerar_codigo_cancelar():
    """Gera código especial para cancelar produto"""
    return calcular_dv_ean13("78999000000")

def gerar_imagem_base64(codigo):
    """
    Gera imagem do código de barras em base64
    Retorna string base64 para usar direto no HTML
    """
    try:
        import barcode
        from barcode.writer import ImageWriter
        from PIL import Image
        
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
        print("⚠️ Bibliotecas não instaladas. Gerando HTML sem imagens.")
        return None
    except Exception as e:
        print(f"⚠️ Erro ao gerar imagem: {e}")
        return None

def gerar_html_completo():
    """Gera HTML completo com todas as imagens"""
    
    meses_nomes = [
        "Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
        "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"
    ]
    
    anos = list(range(2026, 2033))
    data_atual = datetime.now().strftime('%d/%m/%Y %H:%M')
    
    # Gerar códigos
    codigos_meses = []
    for mes in range(1, 13):
        codigo = gerar_codigo_mes(mes)
        img_base64 = gerar_imagem_base64(codigo)
        codigos_meses.append({
            'mes': mes,
            'nome': meses_nomes[mes-1],
            'codigo': codigo,
            'img': img_base64
        })
    
    codigos_anos = []
    for ano in anos:
        codigo = gerar_codigo_ano(ano)
        img_base64 = gerar_imagem_base64(codigo)
        codigos_anos.append({
            'ano': ano,
            'codigo': codigo,
            'img': img_base64
        })
    
    codigo_cancelar = gerar_codigo_cancelar()
    img_cancelar = gerar_imagem_base64(codigo_cancelar)
    
    # Gerar HTML
    html = f"""<!DOCTYPE html>
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
        .aviso {{
            background: #fff3cd;
            border-left: 5px solid #ffc107;
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
        .codigo-barras {{
            display: inline-block;
            padding: 5px;
            background: white;
        }}
        .codigo-barras img {{
            width: 100%;
            max-width: 280px;
            height: auto;
            image-rendering: crisp-edges;
            -ms-interpolation-mode: nearest-neighbor;
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
        .footer {{
            text-align: center;
            margin-top: 30px;
            color: #7f8c8d;
            font-size: 11px;
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
            <small>Gerado em: {data_atual}</small>
        </div>
        
        <table class="tabela-codigos">
"""
    
    # Adicionar meses (3 colunas)
    for i in range(0, 12, 3):
        html += "            <tr>\n"
        for j in range(3):
            if i + j < 12:
                mes = codigos_meses[i + j]
                if mes['img']:
                    html += f"""                <td>
                    <div class="codigo-barras">
                        <img src="{mes['img']}" alt="{mes['nome']}">
                    </div>
                    <div class="descricao">{mes['nome']}</div>
                    <div class="ean">{mes['codigo']}</div>
                </td>
"""
                else:
                    html += f"""                <td>
                    <div class="descricao">{mes['nome']}</div>
                    <div class="ean">{mes['codigo']}</div>
                </td>
"""
            else:
                html += "                <td></td>\n"
        html += "            </tr>\n"
    
    html += """        </table>
    </div>
    
    <!-- PÁGINA 2: ANOS -->
    <div class="pagina">
        <h1>CONTROLE DE PRESTES</h1>
        <h2>CÓDIGOS DE VALIDADE - ANOS</h2>
        
        <table class="tabela-codigos">
"""
    
    # Adicionar anos (3 colunas)
    for i in range(0, 7, 3):
        html += "            <tr>\n"
        for j in range(3):
            if i + j < 7:
                ano = codigos_anos[i + j]
                if ano['img']:
                    html += f"""                <td>
                    <div class="codigo-barras">
                        <img src="{ano['img']}" alt="Ano {ano['ano']}">
                    </div>
                    <div class="descricao">Ano {ano['ano']}</div>
                    <div class="ean">{ano['codigo']}</div>
                </td>
"""
                else:
                    html += f"""                <td>
                    <div class="descricao">Ano {ano['ano']}</div>
                    <div class="ean">{ano['codigo']}</div>
                </td>
"""
            else:
                html += "                <td></td>\n"
        html += "            </tr>\n"
    
    html += """        </table>
    </div>
    
    <!-- PÁGINA 3: CÓDIGO DE CANCELAMENTO -->
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
"""
    
    if img_cancelar:
        html += f"""                    <div class="codigo-barras">
                        <img src="{img_cancelar}" alt="Cancelar">
                    </div>
"""
    else:
        html += """                    <div class="codigo-barras">
                        <div style="height: 60px; background: #eee; display: flex; align-items: center; justify-content: center;">
                            [CÓDIGO DE BARRAS]
                        </div>
                    </div>
"""
    
    html += f"""                    <div class="descricao" style="color: #dc3545;">🚫 CANCELAR</div>
                    <div class="ean">{codigo_cancelar}</div>
                </td>
            </tr>
        </table>
        
        <div class="aviso">
            <strong>EXEMPLO:</strong><br>
            1. Você bipou o produto Leite (EAN: 7891234560012)<br>
            2. Você bipou o mês 12 por engano (queria 11)<br>
            3. Bipe o código CANCELAR acima<br>
            4. Bipe novamente o produto Leite<br>
            5. Bipe o mês correto (11)<br>
            6. Bipe o ano correto<br>
        </div>
    </div>
    
    <!-- PÁGINA 4: TABELA RESUMO -->
    <div class="pagina">
        <h1>TABELA RESUMO DE CÓDIGOS</h1>
        
        <h2>MESES</h2>
        <table class="tabela-codigos">
"""
    
    # Tabela resumo meses (2 colunas)
    for i in range(0, 12, 2):
        html += "            <tr>\n"
        for j in range(2):
            if i + j < 12:
                mes = codigos_meses[i + j]
                html += f"""                <td>
                    <div class="descricao">{mes['nome']}</div>
                    <div class="ean" style="font-size: 18px;">{mes['codigo']}</div>
                </td>
"""
            else:
                html += "                <td></td>\n"
        html += "            </tr>\n"
    
    html += """        </table>
        
        <h2>ANOS</h2>
        <table class="tabela-codigos">
"""
    
    # Tabela resumo anos (2 colunas)
    for i in range(0, 7, 2):
        html += "            <tr>\n"
        for j in range(2):
            if i + j < 7:
                ano = codigos_anos[i + j]
                html += f"""                <td>
                    <div class="descricao">Ano {ano['ano']}</div>
                    <div class="ean" style="font-size: 18px;">{ano['codigo']}</div>
                </td>
"""
            else:
                html += "                <td></td>\n"
        html += "            </tr>\n"
    
    html += f"""        </table>
        
        <h2>FUNÇÃO ESPECIAL</h2>
        <table class="tabela-codigos">
            <tr>
                <td style="background-color: #f8d7da;">
                    <div class="descricao" style="color: #dc3545;">🚫 CANCELAR</div>
                    <div class="ean" style="font-size: 18px;">{codigo_cancelar}</div>
                </td>
            </tr>
        </table>
        
        <div class="exemplo">
            <strong>EXEMPLO PRÁTICO:</strong><br>
            Para cadastrar um produto com validade <strong>Janeiro/2026</strong>:<br><br>
            1. Bipe o PRODUTO: <code>7891234560012</code><br>
            2. Bipe o MÊS: <code>{codigos_meses[0]['codigo']}</code><br>
            3. Bipe o ANO: <code>{codigos_anos[0]['codigo']}</code>
        </div>
    </div>
    
    <!-- PÁGINA 5: INSTRUÇÕES -->
    <div class="pagina">
        <h1>INSTRUÇÕES DETALHADAS</h1>
        
        <div class="instrucoes" style="background: #e8f4f8;">
            <h3>📋 PASSO A PASSO - CADASTRO NORMAL</h3>
            <ol style="font-size: 16px; line-height: 2;">
                <li>Conecte o leitor de código de barras ao computador</li>
                <li>Abra o sistema <strong>Controle de Prestes</strong></li>
                <li>Escolha a opção <strong>2 - Adicionar produto com BIP</strong></li>
                <li>Bipe o código do <strong>PRODUTO</strong></li>
                <li>Bipe o código do <strong>MÊS</strong> de validade</li>
                <li>Bipe o código do <strong>ANO</strong> de validade</li>
                <li>O produto será registrado automaticamente!</li>
            </ol>
        </div>
        
        <div class="cancelar" style="background: #f8d7da;">
            <h3>🚫 PASSO A PASSO - CANCELAR PRODUTO</h3>
            <ol style="font-size: 16px; line-height: 2;">
                <li>Se você errou a data de um produto, bipe o código <strong>CANCELAR</strong></li>
                <li>Bipe novamente o código do <strong>PRODUTO</strong> que errou</li>
                <li>O produto será removido automaticamente</li>
                <li>Agora você pode bipar novamente com a data correta</li>
            </ol>
        </div>
        
        <div class="exemplo" style="background: #e8f8f0;">
            <h3>✅ TESTE RÁPIDO</h3>
            <p>Antes de usar em larga escala, teste com:</p>
            <ul style="font-size: 14px;">
                <li>PRODUTO: 7891234560012 (qualquer EAN de teste)</li>
                <li>MÊS: {codigos_meses[0]['codigo']} (Janeiro)</li>
                <li>ANO: {codigos_anos[0]['codigo']} (2026)</li>
                <li>CANCELAR: {codigo_cancelar}</li>
            </ul>
        </div>
        
        <div class="footer">
            <p>Sistema de Controle de Prestes v3.0</p>
            <p>Gerado em: {data_atual}</p>
        </div>
    </div>
</body>
</html>
"""
    
    return html

def main():
    """Função principal"""
    print("\n" + "=" * 70)
    print("🔢 GERADOR DE CÓDIGOS DE BARRAS PARA WEB")
    print("=" * 70)
    
    # Verificar dependências
    try:
        import barcode
        from PIL import Image
        print("✅ Bibliotecas encontradas")
    except ImportError as e:
        print(f"\n❌ Erro: {e}")
        print("\nInstale as dependências:")
        print("python -m pip install python-barcode pillow")
        print("\nGerando HTML sem imagens...")
    
    # Gerar HTML
    print("\n📄 Gerando HTML com códigos de barras...")
    html_content = gerar_html_completo()
    
    # Salvar arquivo
    pasta_saida = DATA_DIR / "codigos_validade_profissional"
    pasta_saida.mkdir(parents=True, exist_ok=True)
    
    arquivo_html = pasta_saida / "codigos_validade_barras.html"
    with open(arquivo_html, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"✅ HTML gerado: {arquivo_html}")
    print("\n" + "=" * 70)
    print("✅ PROCESSO CONCLUÍDO!")
    print("=" * 70)
    print(f"\n📂 Arquivo salvo em:")
    print(f"   {arquivo_html}")
    print("\n📋 INSTRUÇÕES:")
    print("1. Abra o arquivo no navegador")
    print("2. Imprima (Ctrl+P) com as configurações:")
    print("   • Escala: 100%")
    print("   • Margens: Padrão")
    print("   • Ative 'Imprimir imagens de fundo'")
    print("\n" + "=" * 70)

if __name__ == "__main__":
    main()