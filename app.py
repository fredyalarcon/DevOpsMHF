from flask import Flask, jsonify, request
from models import db, BlackList, BlackListSchema
import uuid
import os
from email_validator import validate_email, EmailNotValidError

blackListSchema = BlackListSchema()

app = Flask(__name__)

basedir = os.path.abspath(os.path.dirname(__file__))
# app.config['SQLALCHEMY_DATABASE_URI'] =\
#     'sqlite:///' + os.path.join(basedir, 'test_database.db')

app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://{}:{}@{}:{}/{}".format( \
os.environ.get('DB_USER') or 'postgres', \
os.environ.get('DB_PASSWORD') or 'postgres', \
os.environ.get('DB_HOST') or 'localhost', \
os.environ.get('DB_PORT') or '5432', \
os.environ.get('DB_NAME') or 'blacklist_db')

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['PROPAGATE_EXCEPTIONS'] = True

app_context = app.app_context()
app_context.push()

db.init_app(app)
db.create_all()

@app.post("/blacklists")
def create():
    token = request.headers.get('Authorization') 
    if token is None: 
        return "Unauthorized", 401
    
    data = request.json
    ip = request.remote_addr
    email = data.get('email')
    idApp = data.get('idApp')

    required_fields = ['email', 'idApp', 'description']
    for field in required_fields:
        if field not in data:
            return f"La etiqueta del campo '{field}' es requerido.", 400
    required_fields = ['email', 'idApp']
    for field in required_fields:
        if not data[field]:
            return f"El campo '{field}' no puede estar vacío.", 402
    if len(data['description']) > 255:
            return "El motivo por el que se agrega a la lista es demasiado largo.", 406
    
    try:
        validate_email(email)
    except EmailNotValidError as e:
        return jsonify({'error': str(e)}), 403
    
    try:
        uuid.UUID(idApp)
    except ValueError:
        return "El campo 'idApp' debe ser un UUID válido.", 405
    
    email_filtro = BlackList.query.filter_by(email=email).first()

    if email_filtro is None:
        email_instance = BlackList( \
        idApp = idApp, \
        email = data['email'], \
        description = data['description'], \
        ip = ip \
        )
        db.session.add(email_instance)
        db.session.commit()
        return jsonify(blackListSchema.dump(email_instance))
    else:
        return f"El email '{email}' ya se encuentra en la lista negra.", 407

@app.get("/blacklists/<string:email>")
def get(email):
    token = request.headers.get('Authorization') 
    if token is None: 
        return "Unauthorized", 401
    
    email_instance = BlackList.query.filter_by(email=email).first()

    if email_instance is None: 
        return "Not found", 404

    return jsonify(blackListSchema.dump(email_instance))

if __name__ == "__main__":
    app.run(port = 5000, debug = True)