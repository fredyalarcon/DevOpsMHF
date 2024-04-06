from flask import Flask, jsonify, request
from models import db, BlackList, BlackListSchema
import uuid
import os

blackListSchema = BlackListSchema()

app = Flask(__name__)

basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] =\
    'sqlite:///' + os.path.join(basedir, 'test_database.db')

# app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://postgres:postgres@localhost:5432/user_db"
# app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://{}:{}@{}:{}/{}".format(os.environ.get('DB_USER'), \
# os.environ.get('DB_PASSWORD'), \
# os.environ.get('DB_HOST'), \
# os.environ.get('DB_PORT'), \
# os.environ.get('DB_NAME'))
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
    email_instance = BlackList( \
        idApp = str(uuid.uuid4()), \
        email = data['email'], \
        description = data['description'], \
        ip = data['ip'] \
    )

    db.session.add(email_instance)
    db.session.commit()
    return jsonify(blackListSchema.dump(email_instance))

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