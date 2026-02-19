import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Configurações base"""
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Evolution API
    EVOLUTION_API_URL = os.getenv('EVOLUTION_API_URL', 'http://localhost:8080')
    EVOLUTION_API_KEY = os.getenv('EVOLUTION_API_KEY', '')
    EVOLUTION_INSTANCE = os.getenv('EVOLUTION_INSTANCE', 'primor')
    
    # WhatsApp Business Cloud API (Meta oficial)
    WHATSAPP_ACCESS_TOKEN = os.getenv('WHATSAPP_ACCESS_TOKEN', '')       # Bearer token do app Meta
    WHATSAPP_PHONE_NUMBER_ID = os.getenv('WHATSAPP_PHONE_NUMBER_ID', '') # ID do número no painel Meta
    WHATSAPP_VERIFY_TOKEN = os.getenv('WHATSAPP_VERIFY_TOKEN', '')       # Token de verificação do webhook
    WHATSAPP_APP_SECRET = os.getenv('WHATSAPP_APP_SECRET', '')           # App Secret para validação HMAC
    
    # URL base
    BASE_URL = os.getenv('BASE_URL', 'http://localhost:5000')
    
    # Admin padrão
    ADMIN_EMAIL = os.getenv('ADMIN_EMAIL', 'admin@primor.com')
    ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD', 'admin123')


class DevelopmentConfig(Config):
    """Configurações de desenvolvimento"""
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'DATABASE_URL', 
        'sqlite:///primor.db'
    )


class ProductionConfig(Config):
    """Configurações de produção"""
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')


class TestingConfig(Config):
    """Configurações de teste"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
