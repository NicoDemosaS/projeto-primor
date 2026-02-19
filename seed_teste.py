"""
Script de seed e testes para o sistema Primor Garcons.

Uso:
    python3 seed_teste.py seed      # cria dados de teste no banco
    python3 seed_teste.py test      # testa os endpoints de confirmacao via HTTP
    python3 seed_teste.py reset     # apaga todos os dados de teste
    python3 seed_teste.py all       # seed + test

O servidor Flask precisa estar rodando para o modo 'test'.
"""

import sys
from datetime import date, time, timedelta

BASE_URL = "http://127.0.0.1:5000"

# ---------------------------------------------------------------------------
# Dados de teste
# ---------------------------------------------------------------------------

GARCONS = [
    {
        "nome": "Carlos Souza",
        "email": "carlos@teste.com",
        "telefone": "11991110001",
        "idade": 28,
        "descricao": "Garcom experiente em eventos corporativos",
        "pix": "carlos@pix.com",
    },
    {
        "nome": "Ana Lima",
        "email": "ana@teste.com",
        "telefone": "11991110002",
        "idade": 25,
        "descricao": "Especialista em casamentos",
        "pix": "ana@pix.com",
    },
    {
        "nome": "Marcos Pereira",
        "email": "marcos@teste.com",
        "telefone": "11991110003",
        "idade": 32,
        "descricao": "Motorista e garcom",
        "pix": "marcos@pix.com",
    },
]

EVENTOS = [
    {
        "nome": "Casamento Silva",
        "tipo": "Casamento",
        "data": date.today() + timedelta(days=7),
        "hora_inicio": time(18, 0),
        "hora_fim": time(23, 0),
        "local": "Espaco Villa Eventos - Sao Paulo",
        "descricao": "Recepcao com jantar para 150 pessoas",
        "valor_padrao": 250.00,
        "valor_motorista": 50.00,
    },
    {
        "nome": "Formatura Turma 2025",
        "tipo": "Formatura",
        "data": date.today() + timedelta(days=14),
        "hora_inicio": time(20, 0),
        "hora_fim": time(2, 0),
        "local": "Clube Atletico - Campinas",
        "descricao": "Jantar de gala com 200 convidados",
        "valor_padrao": 300.00,
        "valor_motorista": 60.00,
    },
]


# ---------------------------------------------------------------------------
# Modo SEED — cria dados no banco via contexto Flask
# ---------------------------------------------------------------------------

def seed():
    from app import create_app, db
    from app.models import Garcom, Evento, Escala

    app = create_app()
    with app.app_context():
        print("\n=== SEED: Criando dados de teste ===\n")

        # --- Garcons ---
        garcons_criados = []
        for dados in GARCONS:
            existente = Garcom.query.filter_by(email=dados["email"]).first()
            if existente:
                print(f"  [SKIP] Garcom ja existe: {dados['nome']}")
                garcons_criados.append(existente)
                continue

            g = Garcom(**dados)
            db.session.add(g)
            db.session.flush()  # garante id antes do commit
            garcons_criados.append(g)
            print(f"  [OK]   Garcom criado: {g.nome} (id={g.id})")

        db.session.commit()

        # --- Eventos ---
        eventos_criados = []
        for dados in EVENTOS:
            existente = Evento.query.filter_by(nome=dados["nome"]).first()
            if existente:
                print(f"  [SKIP] Evento ja existe: {dados['nome']}")
                eventos_criados.append(existente)
                continue

            e = Evento(**dados)
            db.session.add(e)
            db.session.flush()
            eventos_criados.append(e)
            print(f"  [OK]   Evento criado: {e.nome} (id={e.id})")

        db.session.commit()

        # --- Escalas (todos os garcons em todos os eventos) ---
        print()
        for evento in eventos_criados:
            for i, garcom in enumerate(garcons_criados):
                existente = Escala.query.filter_by(
                    evento_id=evento.id, garcom_id=garcom.id
                ).first()
                if existente:
                    print(f"  [SKIP] Escala ja existe: {garcom.nome} -> {evento.nome}")
                    continue

                escala = Escala(
                    evento_id=evento.id,
                    garcom_id=garcom.id,
                    valor=evento.valor_padrao,
                    is_motorista=(i == len(garcons_criados) - 1),  # ultimo vira motorista
                    status="pendente",
                )
                db.session.add(escala)
                print(
                    f"  [OK]   Escala criada: {garcom.nome} -> {evento.nome}"
                    f"{' (motorista)' if escala.is_motorista else ''}"
                )

        db.session.commit()

        # --- Imprimir links de confirmacao ---
        print("\n=== Links gerados ===\n")
        for escala in Escala.query.all():
            g = escala.garcom
            ev = escala.evento
            print(f"  {g.nome} | {ev.nome}")
            print(f"    Confirmar : {BASE_URL}/confirmar/escala-{ev.id}-{g.id}")
            print()

        print("Seed concluido!\n")


# ---------------------------------------------------------------------------
# Modo TEST — bate nos endpoints via HTTP e verifica respostas
# ---------------------------------------------------------------------------

def test():
    try:
        import requests as req
    except ImportError:
        print("Instale o requests: pip3 install requests")
        sys.exit(1)

    from app import create_app, db
    from app.models import Escala, Garcom, Evento

    app = create_app()

    print("\n=== TEST: Testando endpoints de confirmacao ===\n")
    passou = 0
    falhou = 0

    def check(label, url, esperado_status, esperado_texto=None):
        nonlocal passou, falhou
        try:
            r = req.get(url, timeout=5, allow_redirects=True)
            ok_status = r.status_code == esperado_status
            ok_texto = (esperado_texto in r.text) if esperado_texto else True

            if ok_status and ok_texto:
                print(f"  [PASS] {label}")
                passou += 1
            else:
                print(f"  [FAIL] {label}")
                print(f"         URL    : {url}")
                print(f"         Status : {r.status_code} (esperado {esperado_status})")
                if esperado_texto and not ok_texto:
                    print(f"         Texto '{esperado_texto}' nao encontrado na resposta")
                falhou += 1
        except Exception as e:
            print(f"  [ERR]  {label} -> {e}")
            falhou += 1

    with app.app_context():
        escalas = Escala.query.all()
        if not escalas:
            print("Nenhuma escala encontrada. Rode primeiro: python3 seed_teste.py seed\n")
            sys.exit(1)

        for escala in escalas:
            g = escala.garcom
            ev = escala.evento

            # Resetar para pendente para poder testar
            escala.status = "pendente"
            escala.respondido_em = None
            db.session.commit()

            url_confirmar = f"{BASE_URL}/confirmar/escala-{ev.id}-{g.id}"
            url_invalida  = f"{BASE_URL}/confirmar/escala-9999-9999"
            url_ja_resp   = f"{BASE_URL}/confirmar/escala-{ev.id}-{g.id}"

            # 1. Confirmar com escala pendente — espera pagina de sucesso
            check(
                f"Confirmacao: {g.nome} -> {ev.nome}",
                url_confirmar,
                200,
                "confirmada",
            )

            # 2. Acessar o mesmo link de novo — escala ja respondida
            check(
                f"Ja respondido: {g.nome} -> {ev.nome}",
                url_ja_resp,
                200,
                None,
            )

        # 4. ID invalido
        check("ID invalido (garcom/evento inexistente)", url_invalida, 404)

        # Resetar todas as escalas para pendente ao final
        # para que os links manuais continuem funcionando
        for escala in Escala.query.all():
            escala.status = "pendente"
            escala.respondido_em = None
        db.session.commit()

    print(f"\n  Resultado: {passou} passou | {falhou} falhou\n")
    if falhou:
        sys.exit(1)


# ---------------------------------------------------------------------------
# Modo RESET — remove dados de teste
# ---------------------------------------------------------------------------

def reset():
    from app import create_app, db
    from app.models import Garcom, Evento, Escala

    app = create_app()
    with app.app_context():
        print("\n=== RESET: Removendo dados de teste ===\n")
        emails_teste = [g["email"] for g in GARCONS]
        nomes_eventos = [e["nome"] for e in EVENTOS]

        garcons = Garcom.query.filter(Garcom.email.in_(emails_teste)).all()
        for g in garcons:
            for escala in g.escalas.all():
                db.session.delete(escala)
            db.session.delete(g)
            print(f"  [DEL] Garcom: {g.nome}")

        for nome in nomes_eventos:
            ev = Evento.query.filter_by(nome=nome).first()
            if ev:
                db.session.delete(ev)
                print(f"  [DEL] Evento: {ev.nome}")

        db.session.commit()
        print("\nReset concluido!\n")


# ---------------------------------------------------------------------------
# Entrypoint
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "help"

    if cmd == "seed":
        seed()
    elif cmd == "test":
        test()
    elif cmd == "reset":
        reset()
    elif cmd == "all":
        seed()
        test()
    else:
        print(__doc__)
