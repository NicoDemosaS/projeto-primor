#!/usr/bin/env python3
"""
Primor Garçons - Sistema de Gestão de Garçons e Eventos
Ponto de entrada da aplicação Flask
"""

from app import create_app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
