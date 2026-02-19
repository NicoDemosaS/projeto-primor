import requests
from flask import current_app


def enviar_notificacao_whatsapp(escala):
    """
    Envia notificação via Evolution API para o garçom
    
    Args:
        escala: Objeto Escala com dados do garçom e evento
        
    Returns:
        bool: True se enviou com sucesso, False caso contrário
    """
    try:
        config = current_app.config
        
        # Dados da API
        api_url = config['EVOLUTION_API_URL']
        api_key = config['EVOLUTION_API_KEY']
        instance = config['EVOLUTION_INSTANCE']
        base_url = config['BASE_URL']
        
        # Dados do evento e garçom
        evento = escala.evento
        garcom = escala.garcom
        
        # Formatar número (remover caracteres não numéricos e adicionar código do país)
        numero = ''.join(filter(str.isdigit, garcom.telefone))
        if not numero.startswith('55'):
            numero = '55' + numero
        
        # Links de confirmação
        link_confirmar = f"{base_url}/confirmar/escala-{evento.id}-{garcom.id}"
          
        # Montar mensagem
        mensagem = f"""Olá {garcom.nome}! 👋

Você foi escalado para um evento:

📅 *Data:* {evento.data_formatada}
⏰ *Horário:* {evento.horario}
📍 *Local:* {evento.local}
🎉 *Evento:* {evento.nome} ({evento.tipo})
💰 *Valor:* R$ {escala.valor:,.2f}

Por favor, confirme sua presença:

✅ *Confirmar:* {link_confirmar}

_Primor Garçons_"""

        # Endpoint da Evolution API
        endpoint = f"{api_url}/message/sendText/{instance}"
        
        headers = {
            'Content-Type': 'application/json',
            'apikey': api_key
        }
        
        payload = {
            'number': numero,
            'text': mensagem
        }
        
        # Enviar requisição
        response = requests.post(endpoint, json=payload, headers=headers, timeout=30)
        
        if response.status_code == 200 or response.status_code == 201:
            print(f'✅ WhatsApp enviado para {garcom.nome} ({numero})')
            return True
        else:
            print(f'❌ Erro ao enviar para {garcom.nome}: {response.status_code} - {response.text}')
            return False
            
    except requests.exceptions.RequestException as e:
        print(f'❌ Erro de conexão com Evolution API: {e}')
        return False
    except Exception as e:
        print(f'❌ Erro ao enviar WhatsApp: {e}')
        return False


def verificar_conexao_whatsapp():
    """
    Verifica se a Evolution API está conectada
    
    Returns:
        dict: Status da conexão
    """
    try:
        config = current_app.config
        
        api_url = config['EVOLUTION_API_URL']
        api_key = config['EVOLUTION_API_KEY']
        instance = config['EVOLUTION_INSTANCE']
        
        endpoint = f"{api_url}/instance/connectionState/{instance}"
        
        headers = {
            'apikey': api_key
        }
        
        response = requests.get(endpoint, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            return {
                'conectado': data.get('state') == 'open',
                'status': data.get('state', 'unknown')
            }
        else:
            return {
                'conectado': False,
                'status': 'error',
                'erro': response.text
            }
            
    except Exception as e:
        return {
            'conectado': False,
            'status': 'error',
            'erro': str(e)
        }
