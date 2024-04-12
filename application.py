import uuid
import os
from flask import Flask, jsonify, request
from models import db, BlackList, BlackListSchema
from email_validator import validate_email, EmailNotValidError

blackListSchema = BlackListSchema()

application = Flask(__name__)

# basedir = os.path.abspath(os.path.dirname(__file__))
# application.config['SQLALCHEMY_DATABASE_URI'] =\
#     'sqlite:///' + os.path.join(basedir, 'test_database.db')

application.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://{}:{}@{}:{}/{}".format( \
os.environ.get('RDS_USERNAME') or 'postgres', \
os.environ.get('DB_PASSWORD') or 'postgres', \
os.environ.get('RDS_HOSTNAME') or 'localhost', \
os.environ.get('RDS_PORT') or '5432', \
os.environ.get('RDS_PASSWORD') or 'blacklist_db')

application.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
application.config['PROPAGATE_EXCEPTIONS'] = True

app_context = application.app_context()
app_context.push()

db.init_app(application)
db.create_all()

@application.post("/blacklist")
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
        return jsonify({'error': str(e)}), 400
    
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

@application.get("/blacklist/<string:email>")
def get(email):
    token = request.headers.get('Authorization') 
    if token is None: 
        return "Unauthorized", 401
    
    email_instance = BlackList.query.filter_by(email=email).first()

    if email_instance is None: 
        return "Not found", 404

    return jsonify(blackListSchema.dump(email_instance))

@application.get("/blacklist/ping")
def ping():
    return "pong"

if __name__ == "__main__":
    application.run(port = 5000, debug = True)