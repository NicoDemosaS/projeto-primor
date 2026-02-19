# Primor Garçons 🍾

Sistema de gestão de garçons e escalas para eventos.

## 🚀 Funcionalidades

- ✅ **Autenticação**: Login seguro para administradores
- ✅ **Gestão de Garçons**: Cadastro completo (nome, telefone, e-mail, PIX)
- ✅ **Gestão de Eventos**: Criação de eventos com data, horário, local
- ✅ **Escalas**: Vinculação de garçons aos eventos
- ✅ **Notificações WhatsApp**: Envio de convites via Evolution API
- ✅ **Confirmação Pública**: Link único para garçons confirmarem presença
- ✅ **Relatórios PDF**: Exportação de dados para PDF

## 📋 Pré-requisitos

- Python 3.10+
- PostgreSQL (ou SQLite para desenvolvimento)
- Evolution API (opcional, para WhatsApp)

## 🛠️ Instalação

### 1. Clonar o repositório

```bash
git clone https://github.com/seu-usuario/projeto-primor.git
cd projeto-primor
```

### 2. Criar ambiente virtual

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows
```

### 3. Instalar dependências

```bash
pip install -r requirements.txt
```

### 4. Configurar variáveis de ambiente

```bash
cp .env.example .env
```

Edite o arquivo `.env` com suas configurações:

```env
# Flask
SECRET_KEY=sua-chave-secreta-aqui
FLASK_ENV=development

# Database
DATABASE_URL=sqlite:///primor.db
# Ou para PostgreSQL:
# DATABASE_URL=postgresql://usuario:senha@localhost/primor

# Admin padrão
ADMIN_EMAIL=admin@primor.com
ADMIN_PASSWORD=admin123
ADMIN_NOME=Administrador

# Evolution API (opcional)
EVOLUTION_API_URL=http://localhost:8080
EVOLUTION_API_KEY=sua-api-key
EVOLUTION_INSTANCE=primor

# App URL (para links de confirmação)
APP_URL=http://localhost:5000
```

### 5. Inicializar o banco de dados

```bash
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
```

### 6. Executar a aplicação

```bash
python run.py
```

Acesse: http://localhost:5000

## 📁 Estrutura do Projeto

```
projeto-primor/
├── app/
│   ├── __init__.py          # Factory da aplicação
│   ├── config.py             # Configurações
│   ├── models.py             # Modelos do banco
│   ├── routes/
│   │   ├── auth.py           # Autenticação
│   │   ├── dashboard.py      # Dashboard
│   │   ├── garcons.py        # CRUD Garçons
│   │   ├── eventos.py        # CRUD Eventos
│   │   ├── confirmacao.py    # Página pública
│   │   └── relatorios.py     # Relatórios PDF
│   ├── services/
│   │   ├── whatsapp.py       # Evolution API
│   │   └── pdf.py            # Geração de PDFs
│   └── templates/
│       ├── base.html         # Layout base
│       ├── auth/             # Templates de autenticação
│       ├── dashboard/        # Templates do dashboard
│       ├── garcons/          # Templates de garçons
│       ├── eventos/          # Templates de eventos
│       ├── confirmacao/      # Templates públicos
│       └── relatorios/       # Templates de relatórios
├── docs/
│   ├── identidade.md         # Documentação visual
│   └── preview-identidade.html
├── .env.example
├── requirements.txt
├── run.py
└── README.md
```

## 🎨 Identidade Visual

- **Cores**: Tema escuro com detalhes em dourado (amber)
- **Fonte título**: Playfair Display
- **Fonte texto**: Inter
- **Estilo**: Glassmorphism com fundos semi-transparentes

## 📱 Integração WhatsApp

Para enviar notificações via WhatsApp, configure a Evolution API:

1. Instale e configure a [Evolution API](https://github.com/EvolutionAPI/evolution-api)
2. Crie uma instância e conecte seu WhatsApp
3. Configure as variáveis de ambiente no `.env`

## 📄 Licença

MIT License - Veja [LICENSE](LICENSE) para mais detalhes.

## 👨‍💻 Autor

Desenvolvido para **Primor Garçons**
