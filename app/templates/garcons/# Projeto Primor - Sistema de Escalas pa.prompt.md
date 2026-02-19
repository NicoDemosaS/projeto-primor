# Projeto Primor - Sistema de Escalas para Garçons

## 📋 Visão Geral

**Primor** é um SaaS web para gerenciamento de escalas de garçons em eventos. O sistema permite que o administrador cadastre garçons, crie eventos, monte escalas e notifique os profissionais via WhatsApp sobre seus compromissos.

**Versão:** 1.0 (MVP/Protótipo)  
**Acesso:** Web público (hospedado online)  
**Usuário:** Administrador único

---

## 🎯 Objetivos da V1

- Login seguro para o administrador
- Cadastro e gestão de garçons
- Cadastro de tipos de evento
- Criação de eventos com escalas de garçons
- Notificação via WhatsApp (Evolution API) com link de confirmação
- Relatório básico de escalas em PDF

---

## 👥 Atores

| Ator | Descrição |
|------|-----------|
| **Administrador** | Usuário único que gerencia todo o sistema |
| **Garçom** | Recebe notificações e confirma presença via link (não acessa o sistema) |

---

## 📦 Entidades Principais

### Garçom
| Campo | Tipo | Obrigatório |
|-------|------|-------------|
| Nome | Texto | ✅ |
| Email | Texto | ✅ |
| Número (WhatsApp) | Texto | ✅ |
| Idade | Número | ✅ |
| Descrição | Texto | ❌ |
| Chave PIX | Texto | ❌ |
| Ativo | Booleano | ✅ |

### Evento
| Campo | Tipo | Obrigatório |
|-------|------|-------------|
| Nome/Título | Texto | ✅ |
| Tipo de Evento | Categoria | ✅ |
| Data | Data | ✅ |
| Hora Início | Hora | ✅ |
| Hora Fim | Hora | ❌ |
| Local | Texto livre | ✅ |
| Descrição | Texto | ❌ |
| Status | Enum | ✅ |

**Status do Evento:** `Planejado` → `Notificado` → `Realizado`

### Escala (Garçom no Evento)
| Campo | Tipo | Obrigatório |
|-------|------|-------------|
| Evento | Referência | ✅ |
| Garçom | Referência | ✅ |
| Valor (R$) | Número | ✅ |
| Status Confirmação | Enum | ✅ |
| Token Confirmação | Texto | ✅ |

**Status Confirmação:** `Pendente` | `Confirmado` | `Recusado`

---

## 🔐 Casos de Uso

### UC01 - Login do Administrador
**Ator:** Administrador  
**Fluxo:**
1. Admin acessa a tela de login
2. Insere email e senha
3. Sistema valida credenciais
4. Redireciona para o Dashboard

---

### UC02 - Gerenciar Garçons

#### UC02.1 - Cadastrar Garçom
**Fluxo:**
1. Admin acessa "Garçons" → "Novo Garçom"
2. Preenche: nome, email, número, idade, descrição, PIX,
3. Garçom é criado como **Ativo** por padrão
4. Sistema salva e exibe lista atualizada

#### UC02.2 - Editar Garçom
**Fluxo:**
1. Admin seleciona garçom na lista
2. Altera campos desejados
3. Sistema salva alterações

#### UC02.3 - Ativar/Inativar Garçom
**Fluxo:**
1. Admin clica no toggle de status
2. Garçom inativo não aparece na seleção de escalas

#### UC02.4 - Listar Garçons
**Fluxo:**
1. Admin visualiza lista com filtro por status (Ativo/Inativo/Todos)
2. Busca por nome disponível

---


### UC04 - Gerenciar Eventos

#### UC04.1 - Criar Evento
**Fluxo:**
1. Admin acessa "Eventos" → "Novo Evento"
2. Preenche: nome, tipo, data, hora início/fim, local, descrição, valor para cada garcom.
3. Sistema cria evento com status **Planejado**

#### UC04.2 - Montar Escala do Evento
**Fluxo:**
1. Admin abre evento existente
2. Clica em "Adicionar Garçons"
3. Seleciona garçons ativos da lista
4. Sistema salva a escala com status **Pendente**

#### UC04.3 - Remover Garçom da Escala
**Fluxo:**
1. Admin visualiza escala do evento
2. Remove garçom da lista
3. Sistema atualiza escala

#### UC04.4 - Editar Evento
**Fluxo:**
1. Admin altera dados do evento
2. Se já notificado, exibe alerta de que garçons já foram avisados

---

### UC05 - Enviar Notificações

#### UC05.1 - Notificar Garçons do Evento
**Pré-condição:** Evento com pelo menos 1 garçom escalado  
**Fluxo:**
1. Admin abre evento e clica em "Enviar Notificações"
2. Sistema gera **token único** para cada garçom
3. Para cada garçom, envia mensagem via **Evolution API (WhatsApp)**:
   ```
   Olá [Nome]! 👋
   
   Você foi escalado para um evento:
   
   📅 Data: [Data]
   ⏰ Horário: [Hora Início] - [Hora Fim]
   📍 Local: [Local]
   🎉 Evento: [Nome do Evento] ([Tipo])
   💰 Valor: R$ [Valor]
   
   Por favor, confirme sua presença:
   ✅ Confirmar: [Link de Confirmação]
   ❌ Recusar: [Link de Recusa]
   ```
4. Status do evento muda para **Notificado**
5. Sistema registra data/hora do envio

#### UC05.2 - Reenviar Notificação Individual
**Fluxo:**
1. Admin visualiza escala do evento
2. Clica em "Reenviar" para garçom específico
3. Sistema envia nova mensagem

---

### UC06 - Confirmação do Garçom (via Link)

**Ator:** Garçom (externo ao sistema)  
**Fluxo:**
1. Garçom recebe mensagem no WhatsApp
2. Clica no link de confirmação ou recusa
3. Sistema abre página simples:
   - Se **confirmar**: exibe "Presença confirmada! ✅"
   - Se **recusar**: exibe "Presença recusada. Obrigado por avisar!"
4. Status da escala é atualizado
5. Admin pode ver status atualizado no painel

---

### UC07 - Visualizar Status das Confirmações

**Fluxo:**
1. Admin abre evento
2. Visualiza lista de garçons com status:
   - 🟡 Pendente
   - 🟢 Confirmado  
   - 🔴 Recusado
3. Pode filtrar por status

---

### UC08 - Relatórios

#### UC08.1 - Relatório de Escalas por Evento
**Fluxo:**
1. Admin acessa "Relatórios" → "Por Evento"
2. Seleciona evento ou período
3. Visualiza lista de eventos com garçons escalados
4. Exporta em **PDF**

**Conteúdo do PDF:**
- Nome do evento, data, local, tipo
- Lista de garçons (nome, valor, status confirmação)
- Total de garçons / Total confirmados
- Valor total do evento

#### UC08.2 - Relatório Geral de Escalas
**Fluxo:**
1. Admin seleciona período (data início/fim)
2. Sistema lista todos os eventos com suas escalas
3. Exporta em PDF

---

## 🖥️ Telas da V1

| Tela | Descrição |
|------|-----------|
| **Login** | Email + senha |
| **Dashboard** | Resumo: próximos eventos, confirmações pendentes |
| **Garçons** | Lista, cadastro, edição, toggle ativo/inativo |
| **Tipos de Evento** | CRUD simples |
| **Eventos** | Lista de eventos, criar/editar evento |
| **Detalhe do Evento** | Dados do evento + escala + botão notificar |
| **Confirmação (pública)** | Página simples para garçom confirmar/recusar |
| **Relatórios** | Filtros + visualização + botão exportar PDF |

---

## 🔗 Integrações

### Evolution API (WhatsApp)
- **Propósito:** Envio de mensagens para garçons
- **Tipo:** Self-hosted ou Cloud
- **Endpoints necessários:**
  - Envio de mensagem de texto
  - (Opcional) Verificar status de entrega

---

## 🚀 Roadmap

### ✅ V1 (MVP) - Atual
- [x] Login admin
- [x] CRUD Garçons
- [x] CRUD Tipos de Evento
- [x] CRUD Eventos
- [x] Montar escalas
- [x] Notificação WhatsApp
- [x] Link de confirmação
- [x] Relatório PDF básico

### 🔮 V2 (Futuro)
- [ ] Confirmação de comparecimento real
- [ ] Relatórios avançados por garçom
- [ ] Exportar Excel
- [ ] Lembretes automáticos (X dias antes)
- [ ] Notificação por email
- [ ] Histórico de pagamentos
- [ ] Dashboard com gráficos

### 🔮 V3 (Futuro)
- [ ] Multi-tenancy (vários clientes)
- [ ] App/Portal do garçom
- [ ] Integração financeira
- [ ] Múltiplos administradores

---

## 🛠️ Stack Sugerida (V1)

| Camada | Tecnologia |
|--------|------------|
| **Frontend** | HTML + CSS|
| **Estilização** | Tailwind CSS + shadcn/ui |
| **Backend** | FLASK E PYTHON |
| **Banco de Dados** | PostgreSQL / Supabase |
| **Autenticação** | FLASK E PYTHON|
| **WhatsApp** | Evolution API |
| **PDF** | jsPDF ou React-PDF |
| **Hospedagem** | Digitalocean para o MVP, hostingetor dps de aprovado |

---

## 📝 Notas Adicionais

1. **Segurança dos Links:** Tokens de confirmação devem ser únicos, longos e expirar após uso
2. **Garçons Inativos:** Não aparecem para seleção em novas escalas, mas histórico é mantido

---

*Documento criado em: Janeiro/2026*  
*Versão do documento: 1.0*
