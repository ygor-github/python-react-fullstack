# api/app.py

from flask_cors import CORS
from flask_jwt_extended import JWTManager, jwt_required, create_access_token
from flask import Flask, request, jsonify, redirect, url_for
from functools import wraps # Ya no se usa, pero es buena práctica mantenerla por si se necesita
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate 
import datetime
import os


# --- Inicialización de Flask y Configuración de la DB ---
app = Flask(__name__)
FRONTEND_URL = os.environ.get('FRONTEND_URL')

# Configuración de CORS: Permite solo al frontend acceder a las rutas /api/*
CORS(app, resources={r'/api/*':{'origins': FRONTEND_URL}})

# Configuración de la clave secreta JWT (cargada desde el .env)
app.config["JWT_SECRET_KEY"] = os.environ.get("JWT_SECRET_KEY")
jwt = JWTManager(app)

# Configuración de SQLAlchemy
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
migrate = Migrate(app, db)


# --- Modelo de Base de Datos ---
class Word(db.Model):
    __tablename__ = 'words'
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(120), unique=True, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    
    def __repr__(self):
        return f'<Word {self.text}>'


# --- Rutas de la Aplicación ---

@app.route('/')
def home():
    '''Redirect to frontend home'''
    return redirect(FRONTEND_URL)


@app.route('/api/login', methods=['POST'])
def login():
    # Simula un login exitoso y emite un token JWT.
    access_token = create_access_token(identity='client_app')
    return jsonify(access_token=access_token)
  

@app.route('/api/time')
@jwt_required()
def time_now():
    """ Retorna la hora actual del servidor. Requiere un token válido. """
    current_time = datetime.datetime.now()
    formated_time = current_time.strftime('%Y-%m-%d %H:%M:%S')
    return jsonify({'time':formated_time})


@app.route('/api/words', methods=['POST'])
@jwt_required()
def save_word():
    """ Guarda una nueva palabra en la base de datos. Requiere token. """
    data = request.get_json()
    if not data or 'text' not in data:
        return jsonify({"message": "Missing 'text' field in request"}), 400

    new_word_text = data['text']
    new_word = Word(text=new_word_text)
    
    try:
        db.session.add(new_word)
        db.session.commit()
        return jsonify({"message": "Word saved successfully", "word": new_word_text}), 201
    except Exception as e:
        db.session.rollback()
        # En el caso de que la palabra ya exista (unique=True)
        print(f"Database error: {e}")
        return jsonify({"message": "Could not save word (possibly duplicate or DB error)"}), 400


@app.route('/api/words', methods=['GET'])
@jwt_required()
def get_words():
    """ Retorna la lista de todas las palabras guardadas. Requiere token. """
    words = Word.query.order_by(Word.timestamp.desc()).all()
    
    output = []
    for word in words:
        output.append({
            'id': word.id,
            'text': word.text,
            'timestamp': word.timestamp.strftime('%Y-%m-%d %H:%M:%S') 
        })
        
    return jsonify(output), 200


# --- Modo de Desarrollo ---
if __name__ == '__main__':
    # Este bloque es SOLO para desarrollo local o "testing" fuera de Docker.
    
    # Aseguramos que las tablas existan si corremos localmente
    with app.app_context():
        # db.create_all() (Comentado si usamos migraciones, pero útil si no se usan)
        db.create_all()
        
    # Corremos Flask en modo debug para "hot-reloading"
    app.run(debug=True)