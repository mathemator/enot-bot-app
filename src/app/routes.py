# import logging

from flask import Blueprint, jsonify
from telegram_service import TelegramService
from common.repository import save_participants

blueprint = Blueprint('api', __name__)

telegram_service = TelegramService()

@blueprint.errorhandler(ValueError)
def handle_value_error(e):
    response = {
        'error': 'Value Error',
        'message': str(e)
    }
    return jsonify(response), 400

@blueprint.errorhandler(Exception)
def handle_generic_error(e):
    response = {
        'error': 'Internal Server Error',
        'message': str(e)
    }
    # logging.error(e)
    return jsonify(response), 500

@blueprint.route('/health')
def health():
    return jsonify(status='healthy'), 200

@blueprint.route('/')
def index():
    return "Hello from app!"

# Эндпойнт для обновления списка участников
@blueprint.route('/update_participants/<group_id>', methods=['POST'])
async def update_participants(group_id):
    if not group_id:
        return {'status': 'error', 'message': 'Group ID is required'}, 400

    participants = await telegram_service.get_group_users(group_id=group_id)
    save_participants(participants, group_id)

    return {'status': 'success', 'message': f'Participants saved to database'}
