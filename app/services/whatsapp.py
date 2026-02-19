"""
Serviço de envio via WhatsApp Business Cloud API (Meta oficial).

Documentação: https://developers.facebook.com/docs/whatsapp/cloud-api/messages

Variáveis de ambiente necessárias:
  WHATSAPP_ACCESS_TOKEN   — token de acesso permanente ou temporário do app Meta
  WHATSAPP_PHONE_NUMBER_ID — id do número de telefone cadastrado no painel Meta
  BASE_URL                 — URL pública do servidor (para montar links de confirmação)
"""

import logging

import requests
from flask import current_app

logger = logging.getLogger(__name__)

# Endpoint base da Cloud API (versão estável)
_GRAPH_API_URL = 'https://graph.facebook.com/v19.0'


# ---------------------------------------------------------------------------
# Função principal chamada pelo sistema
# ---------------------------------------------------------------------------

def enviar_notificacao_whatsapp(escala) -> bool:
    """
    Envia notificação de escala para o garçom via Cloud API oficial do WhatsApp.

    Args:
        escala: objeto Escala com .garcom e .evento populados

    Returns:
        True se enviou com sucesso, False caso contrário
    """
    config = current_app.config

    access_token = config.get('WHATSAPP_ACCESS_TOKEN', '')
    phone_number_id = config.get('WHATSAPP_PHONE_NUMBER_ID', '')
    base_url = config.get('BASE_URL', '')

    if not access_token or not phone_number_id:
        logger.error(
            'WHATSAPP_ACCESS_TOKEN ou WHATSAPP_PHONE_NUMBER_ID não configurados.'
        )
        return False

    garcom = escala.garcom
    evento = escala.evento

    # Formatar número: somente dígitos, com DDI 55
    numero = ''.join(filter(str.isdigit, garcom.telefone))
    if not numero.startswith('55'):
        numero = '55' + numero

    link_confirmar = f"{base_url}/confirmar/escala-{evento.id}-{garcom.id}"

    mensagem = (
        f"Olá {garcom.nome}! 👋\n\n"
        f"Você foi escalado para um evento:\n\n"
        f"📅 *Data:* {evento.data_formatada}\n"
        f"⏰ *Horário:* {evento.horario}\n"
        f"📍 *Local:* {evento.local}\n"
        f"🎉 *Evento:* {evento.nome} ({evento.tipo})\n"
        f"💰 *Valor:* R$ {escala.valor:,.2f}\n\n"
        f"Por favor, confirme sua presença:\n\n"
        f"✅ *Confirmar:* {link_confirmar}\n\n"
        f"_Primor Garçons_"
    )

    return _enviar_texto(numero, mensagem, access_token, phone_number_id, garcom.nome)


# ---------------------------------------------------------------------------
# Helpers de envio
# ---------------------------------------------------------------------------

def _enviar_texto(
    numero: str,
    mensagem: str,
    access_token: str,
    phone_number_id: str,
    nome_destino: str = '',
) -> bool:
    """
    Envia uma mensagem de texto simples via Cloud API.

    Ref: POST /{phone-number-id}/messages
    """
    endpoint = f"{_GRAPH_API_URL}/{phone_number_id}/messages"

    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json',
    }

    payload = {
        'messaging_product': 'whatsapp',
        'recipient_type': 'individual',
        'to': numero,
        'type': 'text',
        'text': {
            'preview_url': False,
            'body': mensagem,
        },
    }

    try:
        response = requests.post(endpoint, json=payload, headers=headers, timeout=30)

        if response.status_code in (200, 201):
            data = response.json()
            msg_id = data.get('messages', [{}])[0].get('id', '')
            logger.info(
                'WhatsApp enviado para %s (%s) | msg_id=%s',
                nome_destino, numero, msg_id,
            )
            return True

        logger.error(
            'Erro ao enviar para %s (%s): HTTP %s — %s',
            nome_destino, numero, response.status_code, response.text,
        )
        return False

    except requests.exceptions.Timeout:
        logger.error('Timeout ao conectar com a Cloud API do WhatsApp.')
        return False
    except requests.exceptions.RequestException as exc:
        logger.error('Erro de conexão com a Cloud API: %s', exc)
        return False


def marcar_mensagem_lida(message_id: str) -> bool:
    """
    Marca uma mensagem recebida como lida (envia read receipt).
    Útil para chamar a partir do webhook após processar uma mensagem do garçom.

    Ref: POST /{phone-number-id}/messages  com status=read
    """
    config = current_app.config
    access_token = config.get('WHATSAPP_ACCESS_TOKEN', '')
    phone_number_id = config.get('WHATSAPP_PHONE_NUMBER_ID', '')

    if not access_token or not phone_number_id:
        return False

    endpoint = f"{_GRAPH_API_URL}/{phone_number_id}/messages"

    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json',
    }

    payload = {
        'messaging_product': 'whatsapp',
        'status': 'read',
        'message_id': message_id,
    }

    try:
        response = requests.post(endpoint, json=payload, headers=headers, timeout=10)
        return response.status_code in (200, 201)
    except requests.exceptions.RequestException:
        return False


def verificar_conexao_whatsapp() -> dict:
    """
    Verifica se o número está configurado corretamente na Cloud API.
    Faz GET no phone_number_id e retorna as informações do número.

    Ref: GET /{phone-number-id}
    """
    config = current_app.config
    access_token = config.get('WHATSAPP_ACCESS_TOKEN', '')
    phone_number_id = config.get('WHATSAPP_PHONE_NUMBER_ID', '')

    if not access_token or not phone_number_id:
        return {'conectado': False, 'status': 'error', 'erro': 'Credenciais não configuradas'}

    endpoint = f"{_GRAPH_API_URL}/{phone_number_id}"
    headers = {'Authorization': f'Bearer {access_token}'}

    try:
        response = requests.get(endpoint, headers=headers, timeout=10)

        if response.status_code == 200:
            data = response.json()
            return {
                'conectado': True,
                'status': data.get('verified_name', 'ok'),
                'numero': data.get('display_phone_number', ''),
                'qualidade': data.get('quality_rating', ''),
            }

        return {
            'conectado': False,
            'status': 'error',
            'erro': response.text,
        }

    except Exception as exc:
        return {'conectado': False, 'status': 'error', 'erro': str(exc)}
