from functools import wraps
from flask import request, jsonify
from app.models import SolarPlant

def require_api_key(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get('X-API-Key')
        if not api_key:
            return jsonify({"error": "No API key provided"}), 401
        
        plant_id = kwargs.get('plant_id')
        plant = SolarPlant.query.filter_by(id=plant_id, api_key=api_key).first()
        
        if not plant:
            return jsonify({"error": "Invalid API key"}), 401
        
        if plant.api_status != 'enabled':
            return jsonify({"error": "API access is not enabled for this plant"}), 403
        
        return f(*args, **kwargs)
    return decorated_function