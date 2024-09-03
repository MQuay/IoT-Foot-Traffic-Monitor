from backend.app import app
from app.models import db

with app.app_context():
    db.drop_all()
    db.create_all()