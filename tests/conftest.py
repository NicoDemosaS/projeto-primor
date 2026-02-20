import pytest
from datetime import date, time, datetime, timedelta
from app import create_app, db
from app.models import User, Garcom, Evento, Escala

@pytest.fixture
def app():
    """Fixture para criar o app Flask para testes"""
    app = create_app('testing')
    app.config['WTF_CSRF_ENABLED'] = False  # Desabilitar CSRF nos testes
    
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    """O navegador fake"""
    return app.test_client()


@pytest.fixture
def logged_client(client, admin_user):
    """Client já logado como admin"""
    client.post('/login', data={
        'email': admin_user.email,
        'password': 'senha123'
    }, follow_redirects=True)
    return client

# --- FÁBRICAS DE DADOS (Baseado nos seus Models) ---

@pytest.fixture
def admin_user(app):
    """Cria um admin para logar no sistema"""
    user = User(nome="Admin Teste", email="admin@teste.com")
    user.set_password("senha123") # Usa seu método set_password
    db.session.add(user)
    db.session.commit()
    return user

@pytest.fixture
def garcons_padrao(app):
    """Cria 4 garçons prontos para trabalhar"""
    garcons_dados = [
        {
            "nome": "Joao Silva",
            "email": "joao@email.com",
            "telefone": "45999999001",
            "idade": 25,
            "pix": "joao@pix.com",
            "ativo": True
        },
        {
            "nome": "Maria Santos",
            "email": "maria@email.com",
            "telefone": "45999999002",
            "idade": 28,
            "pix": "maria@pix.com",
            "ativo": True
        },
        {
            "nome": "Carlos Oliveira",
            "email": "carlos@email.com",
            "telefone": "45999999003",
            "idade": 30,
            "pix": "carlos@pix.com",
            "ativo": True
        },
        {
            "nome": "Ana Costa",
            "email": "ana@email.com",
            "telefone": "45999999004",
            "idade": 26,
            "pix": "ana@pix.com",
            "ativo": True
        }
    ]
    
    garcons = []
    for dados in garcons_dados:
        garcom = Garcom(**dados)
        db.session.add(garcom)
        garcons.append(garcom)
    
    db.session.commit()
    return garcons

@pytest.fixture
def eventos_futuros(app):
    """Cria 3 eventos futuros"""
    eventos_dados = [
        {
            "nome": "Casamento Silva",
            "tipo": "Casamento",
            "data": date.today() + timedelta(days=1),
            "hora_inicio": time(19, 0),
            "hora_fim": time(23, 0),
            "local": "Salão de Festas Premium",
            "valor_padrao": 200.00,
            "valor_motorista": 50.00,
            "status": "planejado"
        },
        {
            "nome": "Formatura Medicina 2026",
            "tipo": "Formatura",
            "data": date.today() + timedelta(days=7),
            "hora_inicio": time(20, 0),
            "hora_fim": time(2, 0),
            "local": "Clube Atlético",
            "valor_padrao": 250.00,
            "valor_motorista": 60.00,
            "status": "planejado"
        },
        {
            "nome": "Aniversário 50 Anos",
            "tipo": "Aniversário",
            "data": date.today() + timedelta(days=14),
            "hora_inicio": time(18, 0),
            "hora_fim": time(22, 0),
            "local": "Chácara Recanto Verde",
            "valor_padrao": 180.00,
            "valor_motorista": 40.00,
            "status": "planejado"
        }
    ]
    
    eventos = []
    for dados in eventos_dados:
        evento = Evento(**dados)
        db.session.add(evento)
        eventos.append(evento)
    
    db.session.commit()
    return eventos


@pytest.fixture
def escalas_pendentes(app, garcons_padrao, eventos_futuros):
    """Cria escalas pendentes: todos os garcons no primeiro evento"""
    evento = eventos_futuros[0]
    escalas = []
    for garcom in garcons_padrao:
        escala = Escala(
            evento_id=evento.id,
            garcom_id=garcom.id,
            valor=float(evento.valor_padrao),
            is_motorista=False,
            status='pendente'
        )
        db.session.add(escala)
        escalas.append(escala)
    db.session.commit()
    return escalas