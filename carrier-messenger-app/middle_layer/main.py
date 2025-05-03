from flask import Flask
from flask_cors import CORS
from api.user_routes import user_bp
# from api.message_routes import message_bp  # Only if you're keeping message routes modular

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)

app.register_blueprint(user_bp, url_prefix='/')
# app.register_blueprint(message_bp, url_prefix='/')  # Uncomment once you're ready to use this

@app.route('/')
def index():
    return {"message": "Hello from Flask backend!"}

if __name__ == '__main__':
    app.run(debug=True)