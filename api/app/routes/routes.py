from flask import Blueprint, request, jsonify
from pydantic import ValidationError
from ..schemas.input import TaskCreateInput
from ..services import task_service
from ..utils.responses import build_error_response

main_bp = Blueprint('main', __name__)

@main_bp.route('/', methods=['GET'])
def index():
    return jsonify({"message": "InfraTask API", "endpoints": ["/api/health", "/api/tasks"]}), 200

@main_bp.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({"status": "ok"}), 200

@main_bp.route('/api/tasks', methods=['GET'])
def get_tasks():
    tasks = task_service.get_all_tasks()
    return jsonify(tasks), 200

@main_bp.route('/api/tasks', methods=['POST'])
def create_task():
    try:
        json_data = request.get_json()
        if not json_data:
            return jsonify(build_error_response("ValidationError", "No input data provided")), 400
            
        # Pydantic Validation
        validated = TaskCreateInput(**json_data)
        
        # Service Call
        task = task_service.create_task(validated.title, validated.description)
        
        return jsonify(task), 201
        
    except ValidationError as err:
        return jsonify(build_error_response("ValidationError", "Validation failed", err.errors())), 400
    except Exception as e:
        raise e
