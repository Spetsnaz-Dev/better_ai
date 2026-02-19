from ..db.models import db, Task
from .ai_service import classify_task
from ..utils.constants import TaskStatus
from sqlalchemy.exc import SQLAlchemyError
import logging

def create_task(title, description):
    """
    Creates a new task, classifies it via AI, and saves to DB.
    """
    try:
        # Call AI Service
        category = classify_task(description)
        
        # Create Task
        new_task = Task(
            title=title,
            description=description,
            category=category,
            status=TaskStatus.PROCESSED
        )
        
        db.session.add(new_task)
        db.session.commit()
        
        logging.info(f"Task created successfully: {new_task.id}")
        return new_task.to_dict()
        
    except SQLAlchemyError as e:
        db.session.rollback()
        logging.error(f"Database error creating task: {str(e)}")
        raise e
    except Exception as e:
        db.session.rollback()
        logging.error(f"Unexpected error in create_task: {str(e)}")
        raise e

def get_all_tasks():
    try:
        tasks = Task.query.order_by(Task.created_at.desc()).all()
        return [task.to_dict() for task in tasks]
    except SQLAlchemyError as e:
        logging.error(f"Database error getting tasks: {str(e)}")
        raise e
