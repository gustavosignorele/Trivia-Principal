# importamos la instancia de la BD
from apptrivia import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash


class Categoria(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    descripcion = db.Column(db.String(64), index=True, unique=True)
    preguntas = db.relationship('Pregunta', backref='categoria', lazy='dynamic')
    def __repr__(self):
        return '<Categoria: {}>'.format(self.descripcion)


class Pregunta(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(255), nullable=False, unique=True)
    categoria_id = db.Column(db.Integer, db.ForeignKey('categoria.id'))
    respuestas = db.relationship('Respuesta', backref='pregunta', lazy='dynamic')

    def __repr__(self):
        return '<Pregunta %s>' % self.text

class Respuesta(db.Model):
    # campo id es el Primary Key de la tabla
    id = db.Column(db.Integer, primary_key=True)
    # Texto que tiene la respuesta
    text = db.Column(db.String(255), nullable=False, unique=True)
    # ¿Es la respuesta correcta a la Pregunta? Lo defino en este campo booleano, que no sea Nulo, y que x defecto sea False
    correcta = db.Column(db.Boolean, nullable=False, default=False)
    # Esta respuesta corresponde a una pregunta exacta, guardo el id de esa pregunta
    pregunta_id = db.Column(db.Integer, db.ForeignKey('pregunta.id'))

    def __repr__(self):
        return '<Respuesta %s>' % self.text

class User(db.Model, UserMixin):
    __tablename__ = 'trivia_user'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(256), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)
    roles = db.relationship('Role', backref='user', lazy='dynamic')

    def __repr__(self):
        return '<User {} - Email {}>'.format(self.name, self.email)

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def is_admin(self):
        return self.is_admin

    def save(self):
        if not self.id:
            db.session.add(self)
        db.session.commit()


    @staticmethod
    def get_by_id(id):
        return User.query.get(id)

    @staticmethod
    def get_by_email(email):
        return User.query.filter_by(email=email).first()


class Role(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    rolename = db.Column(db.String(60), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('trivia_user.id'))