"""Rotas públicas de identificação e saúde da API."""
from flask import Blueprint, jsonify

from models.base import now_utc

API_NAME = 'Task Manager API'
API_VERSION = '1.0'

health_bp = Blueprint('health', __name__)


@health_bp.get('/')
def index():
    return jsonify({'message': API_NAME, 'version': API_VERSION}), 200


@health_bp.get('/health')
def health():
    return jsonify({'status': 'ok', 'timestamp': str(now_utc())}), 200
