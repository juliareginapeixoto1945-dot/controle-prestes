#!/usr/bin/env python3
# ============================================
# INICIALIZADOR DO WEB APP
# ============================================

import os
import sys
import webbrowser
import threading
import time

def abrir_navegador():
    """Abre o navegador após 2 segundos"""
    time.sleep(2)
    webbrowser.open('http://localhost:5000')

if __name__ == '__main__':
    # Adiciona diretório atual ao path
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    
    # Inicia thread para abrir navegador
    threading.Thread(target=abrir_navegador, daemon=True).start()
    
    # Importa e executa o app
    from backend.app import app
    app.run(host='0.0.0.0', port=5000, debug=True)