"""
Testes do sistema Primor Garçons.

Cobre:
  - Rotas básicas (dashboard, relatórios)
  - CRUD de garçons (criar, editar, excluir)
  - CRUD de eventos (criar, editar)
  - Adicionar garçom na escala do evento
  - Conflito de horário (mesmo garçom em eventos sobrepostos)
  - Confirmação de presença via link
  - Link inválido / já respondido

NÃO cobre (implementar depois):
  # TODO: Testes de envio WhatsApp (Cloud API)
  # TODO: Testes de webhook WhatsApp (recebimento)
"""

from datetime import date, time, timedelta
from app import db
from app.models import Garcom, Evento, Escala


# =========================================================================
# TESTES BÁSICOS — Rotas respondem
# =========================================================================

class TestRotasBasicas:
    """Testa se as rotas protegidas redirecionam para login"""

    def test_dashboard_redireciona_sem_login(self, client):
        resp = client.get('/', follow_redirects=False)
        assert resp.status_code == 302
        assert '/login' in resp.headers['Location']

    def test_login_page_responde(self, client):
        resp = client.get('/login')
        assert resp.status_code == 200

    def test_dashboard_responde_logado(self, logged_client):
        resp = logged_client.get('/')
        assert resp.status_code == 200

    def test_relatorios_responde_logado(self, logged_client):
        resp = logged_client.get('/relatorios/')
        assert resp.status_code == 200

    def test_garcons_index_responde(self, logged_client):
        resp = logged_client.get('/garcons/')
        assert resp.status_code == 200

    def test_eventos_index_responde(self, logged_client):
        resp = logged_client.get('/eventos/')
        assert resp.status_code == 200


# =========================================================================
# TESTES DE GARÇOM — Criar, Editar, Excluir
# =========================================================================

class TestGarcom:

    def test_criar_garcom(self, logged_client, app):
        resp = logged_client.post('/garcons/novo', data={
            'nome': 'Pedro Teste',
            'email': 'pedro@teste.com',
            'telefone': '45988887777',
            'idade': '27',
            'pix': 'pedro@pix.com',
            'descricao': 'Garcom de teste',
        }, follow_redirects=True)

        assert resp.status_code == 200
        assert 'Pedro Teste' in resp.data.decode()

        with app.app_context():
            garcom = Garcom.query.filter_by(email='pedro@teste.com').first()
            assert garcom is not None
            assert garcom.nome == 'Pedro Teste'
            assert garcom.idade == 27

    def test_editar_garcom(self, logged_client, app, garcons_padrao):
        garcom = garcons_padrao[0]

        resp = logged_client.post(f'/garcons/{garcom.id}/editar', data={
            'nome': 'Joao Editado',
            'email': 'joao@email.com',
            'telefone': '45999999001',
            'idade': '26',
            'pix': 'joao-novo@pix.com',
            'descricao': 'Editado',
        }, follow_redirects=True)

        assert resp.status_code == 200

        with app.app_context():
            garcom_atualizado = db.session.get(Garcom, garcom.id)
            assert garcom_atualizado.nome == 'Joao Editado'
            assert garcom_atualizado.idade == 26

    def test_excluir_garcom(self, logged_client, app, garcons_padrao):
        garcom = garcons_padrao[0]
        garcom_id = garcom.id

        resp = logged_client.post(
            f'/garcons/{garcom_id}/excluir',
            follow_redirects=True
        )

        assert resp.status_code == 200

        with app.app_context():
            assert db.session.get(Garcom, garcom_id) is None

    def test_toggle_ativo_garcom(self, logged_client, app, garcons_padrao):
        garcom = garcons_padrao[0]
        assert garcom.ativo is True

        logged_client.post(
            f'/garcons/{garcom.id}/toggle-ativo',
            follow_redirects=True
        )

        with app.app_context():
            garcom_atualizado = db.session.get(Garcom, garcom.id)
            assert garcom_atualizado.ativo is False

    def test_form_novo_garcom_responde(self, logged_client):
        resp = logged_client.get('/garcons/novo')
        assert resp.status_code == 200


# =========================================================================
# TESTES DE EVENTO — Criar, Editar
# =========================================================================

class TestEvento:

    def test_criar_evento(self, logged_client, app):
        data_evento = (date.today() + timedelta(days=5)).strftime('%d/%m/%Y')

        resp = logged_client.post('/eventos/novo', data={
            'nome': 'Evento Criado no Teste',
            'tipo': 'Corporativo',
            'data': data_evento,
            'hora_inicio': '18:00',
            'hora_fim': '22:00',
            'local': 'Local de Teste',
            'descricao': 'Descricao teste',
            'valor_padrao': '200',
            'valor_motorista': '50',
        }, follow_redirects=True)

        assert resp.status_code == 200

        with app.app_context():
            evento = Evento.query.filter_by(nome='Evento Criado no Teste').first()
            assert evento is not None
            assert evento.tipo == 'Corporativo'
            assert evento.local == 'Local de Teste'

    def test_editar_evento(self, logged_client, app, eventos_futuros):
        evento = eventos_futuros[0]
        data_evento = evento.data.strftime('%d/%m/%Y')

        resp = logged_client.post(f'/eventos/{evento.id}/editar', data={
            'nome': 'Casamento Editado',
            'tipo': 'Casamento',
            'data': data_evento,
            'hora_inicio': '20:00',
            'hora_fim': '23:30',
            'local': 'Novo Local',
            'descricao': '',
            'valor_padrao': '300',
            'valor_motorista': '80',
        }, follow_redirects=True)

        assert resp.status_code == 200

        with app.app_context():
            evento_atualizado = db.session.get(Evento, evento.id)
            assert evento_atualizado.nome == 'Casamento Editado'
            assert evento_atualizado.local == 'Novo Local'

    def test_detalhe_evento_responde(self, logged_client, eventos_futuros):
        evento = eventos_futuros[0]
        resp = logged_client.get(f'/eventos/{evento.id}')
        assert resp.status_code == 200

    def test_form_novo_evento_responde(self, logged_client):
        resp = logged_client.get('/eventos/novo')
        assert resp.status_code == 200

    def test_excluir_evento(self, logged_client, app, eventos_futuros):
        evento = eventos_futuros[0]
        evento_id = evento.id

        resp = logged_client.post(
            f'/eventos/{evento_id}/excluir',
            follow_redirects=True
        )

        assert resp.status_code == 200

        with app.app_context():
            assert db.session.get(Evento, evento_id) is None


# =========================================================================
# TESTES DE ESCALA — Adicionar garçom, conflito de horário
# =========================================================================

class TestEscala:

    def test_adicionar_garcom_ao_evento(self, logged_client, app, garcons_padrao, eventos_futuros):
        evento = eventos_futuros[0]
        garcom = garcons_padrao[0]

        resp = logged_client.post(
            f'/eventos/{evento.id}/adicionar-garcom',
            data={'garcons': [str(garcom.id)]},
            follow_redirects=True
        )

        assert resp.status_code == 200

        with app.app_context():
            escala = Escala.query.filter_by(
                evento_id=evento.id, garcom_id=garcom.id
            ).first()
            assert escala is not None
            assert escala.status == 'pendente'
            assert float(escala.valor) == float(evento.valor_padrao)

    def test_adicionar_garcom_duplicado_nao_duplica(self, logged_client, app, garcons_padrao, eventos_futuros):
        """Tentar adicionar o mesmo garçom ao mesmo evento 2x não deve duplicar"""
        evento = eventos_futuros[0]
        garcom = garcons_padrao[0]

        # Primeira vez
        logged_client.post(
            f'/eventos/{evento.id}/adicionar-garcom',
            data={'garcons': [str(garcom.id)]},
            follow_redirects=True
        )

        # Segunda vez
        logged_client.post(
            f'/eventos/{evento.id}/adicionar-garcom',
            data={'garcons': [str(garcom.id)]},
            follow_redirects=True
        )

        with app.app_context():
            total = Escala.query.filter_by(
                evento_id=evento.id, garcom_id=garcom.id
            ).count()
            assert total == 1

    def test_conflito_horario_mesmo_dia(self, logged_client, app, garcons_padrao):
        """Garçom não pode ser adicionado a dois eventos com horário sobreposto no mesmo dia"""
        garcom = garcons_padrao[0]
        amanha = date.today() + timedelta(days=1)

        # Evento 1: 18:00 - 22:00
        evento1 = Evento(
            nome='Evento A', tipo='Festa', data=amanha,
            hora_inicio=time(18, 0), hora_fim=time(22, 0),
            local='Local A', valor_padrao=100, status='planejado'
        )
        # Evento 2: 20:00 - 23:00 (sobrepõe com evento 1)
        evento2 = Evento(
            nome='Evento B', tipo='Festa', data=amanha,
            hora_inicio=time(20, 0), hora_fim=time(23, 0),
            local='Local B', valor_padrao=100, status='planejado'
        )
        db.session.add_all([evento1, evento2])
        db.session.commit()

        # Adicionar garçom ao evento 1
        logged_client.post(
            f'/eventos/{evento1.id}/adicionar-garcom',
            data={'garcons': [str(garcom.id)]},
            follow_redirects=True
        )

        # Tentar adicionar ao evento 2 (conflito)
        logged_client.post(
            f'/eventos/{evento2.id}/adicionar-garcom',
            data={'garcons': [str(garcom.id)]},
            follow_redirects=True
        )

        with app.app_context():
            # Deve estar apenas no evento 1
            escala_ev1 = Escala.query.filter_by(
                evento_id=evento1.id, garcom_id=garcom.id
            ).first()
            escala_ev2 = Escala.query.filter_by(
                evento_id=evento2.id, garcom_id=garcom.id
            ).first()
            assert escala_ev1 is not None
            assert escala_ev2 is None  # Conflito: não deve existir

    def test_sem_conflito_horarios_diferentes(self, logged_client, app, garcons_padrao):
        """Garçom pode participar de dois eventos no mesmo dia sem sobreposição"""
        garcom = garcons_padrao[0]
        amanha = date.today() + timedelta(days=1)

        # Evento 1: 10:00 - 14:00
        evento1 = Evento(
            nome='Evento Manhã', tipo='Brunch', data=amanha,
            hora_inicio=time(10, 0), hora_fim=time(14, 0),
            local='Local A', valor_padrao=100, status='planejado'
        )
        # Evento 2: 18:00 - 22:00 (sem conflito)
        evento2 = Evento(
            nome='Evento Noite', tipo='Jantar', data=amanha,
            hora_inicio=time(18, 0), hora_fim=time(22, 0),
            local='Local B', valor_padrao=100, status='planejado'
        )
        db.session.add_all([evento1, evento2])
        db.session.commit()

        logged_client.post(
            f'/eventos/{evento1.id}/adicionar-garcom',
            data={'garcons': [str(garcom.id)]},
            follow_redirects=True
        )

        logged_client.post(
            f'/eventos/{evento2.id}/adicionar-garcom',
            data={'garcons': [str(garcom.id)]},
            follow_redirects=True
        )

        with app.app_context():
            escala_ev1 = Escala.query.filter_by(
                evento_id=evento1.id, garcom_id=garcom.id
            ).first()
            escala_ev2 = Escala.query.filter_by(
                evento_id=evento2.id, garcom_id=garcom.id
            ).first()
            assert escala_ev1 is not None
            assert escala_ev2 is not None  # Sem conflito: ok

    def test_remover_garcom_do_evento(self, logged_client, app, escalas_pendentes):
        escala = escalas_pendentes[0]
        evento_id = escala.evento_id
        garcom_id = escala.garcom_id

        resp = logged_client.post(
            f'/eventos/{evento_id}/remover-garcom/{garcom_id}',
            follow_redirects=True
        )

        assert resp.status_code == 200

        with app.app_context():
            assert Escala.query.filter_by(
                evento_id=evento_id, garcom_id=garcom_id
            ).first() is None


# =========================================================================
# TESTES DE CONFIRMAÇÃO — Link de presença
# =========================================================================

class TestConfirmacao:

    def test_confirmar_presenca_via_link(self, client, app, escalas_pendentes):
        """GET /confirmar/escala-{evento_id}-{garcom_id} confirma a presença"""
        escala = escalas_pendentes[0]

        resp = client.get(
            f'/confirmar/escala-{escala.evento_id}-{escala.garcom_id}',
            follow_redirects=True
        )

        assert resp.status_code == 200
        assert 'confirmada' in resp.data.decode().lower()

        with app.app_context():
            escala_db = db.session.get(Escala, escala.id)
            assert escala_db.status == 'confirmado'
            assert escala_db.respondido_em is not None

    def test_confirmar_novamente_mostra_ja_respondido(self, client, app, escalas_pendentes):
        """Acessar link depois de já confirmado mostra 'já respondido'"""
        escala = escalas_pendentes[0]
        url = f'/confirmar/escala-{escala.evento_id}-{escala.garcom_id}'

        # Primeira vez — confirma
        client.get(url, follow_redirects=True)

        # Segunda vez — já respondido
        resp = client.get(url, follow_redirects=True)

        assert resp.status_code == 200
        assert 'respondeu' in resp.data.decode().lower()

    def test_link_invalido_retorna_404(self, client):
        """Link com IDs inexistentes retorna 404"""
        resp = client.get('/confirmar/escala-9999-9999')
        assert resp.status_code == 404

    def test_link_garcom_inexistente_retorna_404(self, client, eventos_futuros):
        """Garçom inexistente retorna 404"""
        evento = eventos_futuros[0]
        resp = client.get(f'/confirmar/escala-{evento.id}-9999')
        assert resp.status_code == 404

    def test_link_sem_escala_retorna_404(self, client, garcons_padrao, eventos_futuros):
        """Garçom existe mas não tem escala para o evento retorna 404"""
        garcom = garcons_padrao[0]
        evento = eventos_futuros[0]
        resp = client.get(f'/confirmar/escala-{evento.id}-{garcom.id}')
        assert resp.status_code == 404


# =========================================================================
# TODO: TESTES DE WHATSAPP
# =========================================================================

# TODO: Testar envio de notificação WhatsApp (Cloud API)
#   - Mockar requests.post para verificar payload correto
#   - Testar formatação do número (DDI 55)
#   - Testar montagem do link de confirmação

# TODO: Testar webhook WhatsApp (recebimento)
#   - Testar verificação GET (hub.challenge)
#   - Testar recebimento POST de mensagem
#   - Testar validação de assinatura HMAC
#   - Testar payload inválido retorna 400
