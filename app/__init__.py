from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect

from app.config import config

# Extensões
db = SQLAlchemy()
login_manager = LoginManager()
csrf = CSRFProtect()

login_manager.login_view = 'auth.login'
login_manager.login_message = 'Por favor, faça login para acessar esta página.'
login_manager.login_message_category = 'warning'


def create_app(config_name='default'):
    """Factory de criação da aplicação Flask"""
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # Inicializar extensões
    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)
    
    # Registrar blueprints
    from app.routes.auth import auth_bp
    from app.routes.dashboard import dashboard_bp
    from app.routes.garcons import garcons_bp
    from app.routes.eventos import eventos_bp
    from app.routes.confirmacao import confirmacao_bp
    from app.routes.relatorios import relatorios_bp
    from app.routes.webhook import webhook_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(garcons_bp)
    app.register_blueprint(eventos_bp)
    app.register_blueprint(confirmacao_bp)
    app.register_blueprint(relatorios_bp)
    app.register_blueprint(webhook_bp)
    
    # Isentar webhook de CSRF (recebe POST externo da Meta)
    csrf.exempt(webhook_bp)
    
    # Criar tabelas e admin padrão
    with app.app_context():
        db.create_all()
        create_admin_user(app)
    
    return app


def create_admin_user(app):
    """Cria usuário admin padrão se não existir"""
    from app.models import User
    
    admin_email = app.config['ADMIN_EMAIL']
    admin = User.query.filter_by(email=admin_email).first()
    
    if not admin:
        admin = User(
            email=admin_email,
            nome='Administrador'
        )
        admin.set_password(app.config['ADMIN_PASSWORD'])
        db.session.add(admin)
        db.session.commit()
        print(f'✅ Admin criado: {admin_email}')
