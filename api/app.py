from flask_cors import CORS
from flask_jwt_extended import JWTManager, jwt_required, create_access_token
from flask import Flask, request, jsonify, redirect, url_for
from functools import wraps
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate 
import datetime
import os


app = Flask(__name__)
FRONTEND_URL = 'http://localhost:5173'
CORS(app, resources={r'/api/*':{'origins': FRONTEND_URL}})

# Configuración de la clave secreta JWT
app.config["JWT_SECRET_KEY"] = os.environ.get("JWT_SECRET_KEY")
jwt = JWTManager(app)

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
migrate = Migrate(app, db)

class Word(db.Model):
    __tablename__ = 'words'
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(120), unique=True, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    def __repr__(self):
        return f'<Word {self.text}>'


@app.route('/')
def home():
    '''Redirect to frontend home'''
    return redirect(FRONTEND_URL)


@app.route('/api/login', methods=['POST'])
def login():
    # En una app real, aquí validarías usuario y contraseña.
    # Por ahora, simularemos un login exitoso.
    
    # Creamos un token de acceso para una identidad ficticia (ej: 'user_id_1')
    access_token = create_access_token(identity='client_app')
    return jsonify(access_token=access_token)
  


@app.route('/api/time')
@jwt_required()
def time_now():
    """ Retunt current time """
    current_time = datetime.datetime.now()
    formated_time = current_time.strftime('%Y-%m-%d %H:%M:%S')
    return jsonify({'time':formated_time})


if __name__ == '__main__':
    # El servidor Gunicorn de Docker NO usa este bloque.
    # Este bloque es SOLO para desarrollo local o "testing" fuera de Docker.
    
    # 1. Aseguramos que las tablas existan si corremos localmente
    with app.app_context():
        db.create_all()
        
    # 2. Corremos Flask en modo debug para "hot-reloading"
    app.run(debug=True)