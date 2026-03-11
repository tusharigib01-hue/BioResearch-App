from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), default="researcher")

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    focus = db.Column(db.String(200), nullable=False)
    start_date = db.Column(db.String(20))
    lead = db.Column(db.String(120))


# 🧬 Sample Model (CORE RESEARCH ENTITY)
class Sample(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sample_code = db.Column(db.String(50), unique=True, nullable=False)
    sample_type = db.Column(db.String(100))
    disease = db.Column(db.String(120))
    storage = db.Column(db.String(120))
    status = db.Column(db.String(50))

    project_id = db.Column(db.Integer, db.ForeignKey("project.id"))
    project = db.relationship("Project", backref="samples")
