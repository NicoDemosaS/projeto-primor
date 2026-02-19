import hmac
import hashlib
import logging

from flask import Blueprint, request, jsonify, current_app, make_response

logger = logging.getLogger(__name__)

webhook_bp = Blueprint('webhook', __name__, url_prefix='/webhook')


@webhook_bp.route('/whatsapp', methods=['GET'])
def verificar_webhook():
    """
    Verificação do webhook (GET) — exigido pela Meta.
    
    Quando você registra a URL do webhook no painel da Meta,
    ela envia um GET com:
      - hub.mode = "subscribe"
      - hub.verify_token = <token que você definiu>
      - hub.challenge = <string aleatória>
    
    Devemos responder com o hub.challenge caso o token confira.
    """
    mode = request.args.get('hub.mode')
    token = request.args.get('hub.verify_token')
    challenge = request.args.get('hub.challenge')

    verify_token = current_app.config.get('WHATSAPP_VERIFY_TOKEN', '')

    if mode == 'subscribe' and token == verify_token:
        logger.info('Webhook do WhatsApp verificado com sucesso.')
        resp = make_response(str(challenge), 200)
        resp.content_type = 'text/plain'
        return resp

    logger.warning('Falha na verificação do webhook: token inválido.')
    return make_response('Forbidden', 403)


@webhook_bp.route('/whatsapp', methods=['POST'])
def receber_webhook():
    """
    Recebe notificações do webhook da API oficial do WhatsApp Business.

    Tipos de payload tratados:
      - messages  → mensagens recebidas de usuários
      - statuses  → atualizações de status de mensagens enviadas
    """
    # --- Validar assinatura (X-Hub-Signature-256) ---
    app_secret = current_app.config.get('WHATSAPP_APP_SECRET', '')
    if app_secret:
        signature_header = request.headers.get('X-Hub-Signature-256', '')
        if not _validar_assinatura(request.data, app_secret, signature_header):
            logger.warning('Assinatura do webhook inválida.')
            return jsonify({'status': 'error', 'message': 'Assinatura inválida'}), 403

    payload = request.get_json(silent=True)
    if not payload:
        return jsonify({'status': 'error', 'message': 'Payload vazio'}), 400

    # A Meta sempre envia object = "whatsapp_business_account"
    if payload.get('object') != 'whatsapp_business_account':
        return jsonify({'status': 'ignored'}), 200

    try:
        for entry in payload.get('entry', []):
            for change in entry.get('changes', []):
                field = change.get('field')
                value = change.get('value', {})

                if field == 'messages':
                    _processar_mensagens(value)

        return jsonify({'status': 'ok'}), 200

    except Exception:
        logger.exception('Erro ao processar webhook do WhatsApp.')
        return jsonify({'status': 'error'}), 200  # 200 para evitar retries


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _validar_assinatura(payload_body: bytes, app_secret: str, signature_header: str) -> bool:
    """
    Valida a assinatura HMAC-SHA256 enviada pela Meta no header
    X-Hub-Signature-256 para garantir autenticidade do webhook.
    """
    if not signature_header:
        return False

    expected = 'sha256=' + hmac.new(
        app_secret.encode('utf-8'),
        payload_body,
        hashlib.sha256,
    ).hexdigest()

    return hmac.compare_digest(expected, signature_header)


def _processar_mensagens(value: dict):
    """
    Processa o campo 'messages' do webhook.

    Trata:
      - mensagens de texto recebidas
      - atualizações de status de mensagens enviadas
    """
    from app.services.whatsapp import marcar_mensagem_lida

    metadata = value.get('metadata', {})
    phone_number_id = metadata.get('phone_number_id')

    # --- Atualizações de status (sent, delivered, read, failed) ---
    for status in value.get('statuses', []):
        _processar_status(status, phone_number_id)

    # --- Mensagens recebidas ---
    for message in value.get('messages', []):
        msg_id = message.get('id', '')
        sender = message.get('from', '')
        msg_type = message.get('type', '')
        logger.info('Mensagem recebida — de=%s tipo=%s id=%s', sender, msg_type, msg_id)

        # Marcar como lida na plataforma da Meta
        if msg_id:
            marcar_mensagem_lida(msg_id)



def _processar_status(status: dict, phone_number_id: str):
    """
    Processa atualizações de status de mensagens enviadas.
    Exemplo: delivered, read, sent, failed.
    """
    status_value = status.get('status')        # sent | delivered | read | failed
    recipient_id = status.get('recipient_id')  # número do destinatário
    timestamp = status.get('timestamp')

    logger.info(
        'Status de mensagem — destino=%s status=%s phone_id=%s ts=%s',
        recipient_id, status_value, phone_number_id, timestamp,
    )

    # Erros de envio
    errors = status.get('errors', [])
    for err in errors:
        logger.error(
            'Erro no envio — código=%s título=%s detalhe=%s',
            err.get('code'), err.get('title'), err.get('message'),
        )