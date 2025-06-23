from flask import Flask
from models import db, Webhook, WebhookLog
from config import SQLALCHEMY_TRACK_MODIFICATIONS, SECRET_KEY
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DATABASE_URL")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = SQLALCHEMY_TRACK_MODIFICATIONS
app.config['SECRET_KEY'] = SECRET_KEY

db.init_app(app)

with app.app_context():
    db.create_all()
    print("✅ Tabelas criadas com sucesso no banco da Hostinger!")
