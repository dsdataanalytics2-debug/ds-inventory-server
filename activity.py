from sqlalchemy.orm import Session
from datetime import datetime
import models

def log_activity(
    db: Session, 
    user: models.User, 
    action: str, 
    target: str, 
    details: str = None
):
    """Log user activity to the database"""
    activity_log = models.ActivityLog(
        user_id=user.id,
        action=action,
        target=target,
        details=details,
        timestamp=datetime.utcnow()
    )
    db.add(activity_log)
    db.commit()
    return activity_log

def get_activity_logs(db: Session, limit: int = 100):
    """Get activity logs with user information"""
    logs = db.query(
        models.ActivityLog,
        models.User.username,
        models.User.role
    ).join(
        models.User, 
        models.ActivityLog.user_id == models.User.id
    ).order_by(
        models.ActivityLog.timestamp.desc()
    ).limit(limit).all()
    
    formatted_logs = []
    for log, username, user_role in logs:
        formatted_logs.append({
            "id": log.id,
            "user_id": log.user_id,
            "action": log.action,
            "target": log.target,
            "details": log.details,
            "timestamp": log.timestamp,
            "username": username,
            "user_role": user_role.value
        })
    
    return formatted_logs

def get_activity_logs_by_user(db: Session, user_id: int, limit: int = 50):
    """Get activity logs for a specific user"""
    logs = db.query(models.ActivityLog).filter(
        models.ActivityLog.user_id == user_id
    ).order_by(
        models.ActivityLog.timestamp.desc()
    ).limit(limit).all()
    
    return logs
