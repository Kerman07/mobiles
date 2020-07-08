from app import bcrypt, db, login
from datetime import datetime
from flask_login import UserMixin


class Admin(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(140))
    password = db.Column(db.String(128))

    def set_password(self, password):
        self.password = bcrypt.generate_password_hash(password).decode('utf')

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password, password)


class Phone(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    maker = db.Column(db.String(140))
    model = db.Column(db.String(140))
    img_link = db.Column(db.String(140))
    specs = db.Column(db.Text)
    memory = db.Column(db.Integer)
    ram = db.Column(db.Integer)
    price = db.Column(db.Integer)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)

    def __repr__(self):
        return f'<Phone {self.maker} + {self.model}'


@login.user_loader
def load_user(id):
    return Admin.query.get(int(id))
