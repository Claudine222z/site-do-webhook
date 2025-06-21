from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Webhook(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    token = db.Column(db.String(255), nullable=False)
    endpoint = db.Column(db.String(255), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    request_count = db.Column(db.Integer, default=0)
    last_request = db.Column(db.DateTime)
    
    # Relacionamento com logs
    logs = db.relationship('WebhookLog', backref='webhook', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Webhook {self.name}>'

class WebhookLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    webhook_id = db.Column(db.Integer, db.ForeignKey('webhook.id'), nullable=False)
    method = db.Column(db.String(10), nullable=False)
    headers = db.Column(db.Text)
    data = db.Column(db.Text)
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.String(255))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<WebhookLog {self.id}>'
