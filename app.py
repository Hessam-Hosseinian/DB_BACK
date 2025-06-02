from dotenv import load_dotenv
from flask import Flask
from flask_session import Session
import os
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
load_dotenv()
app.secret_key = os.getenv("SECRET_KEY")
app.config['SESSION_TYPE'] = 'filesystem'
CORS(app, supports_credentials=True)
from routes.user_routes import user_bp
from routes.game_routes import game_bp
from routes.category_routes import category_bp
app.register_blueprint(category_bp)

app.register_blueprint(user_bp)
app.register_blueprint(game_bp)


@app.route("/routes")
def list_routes():
    output = []
    for rule in app.url_map.iter_rules():
        methods = ','.join(sorted(rule.methods - {"HEAD", "OPTIONS"}))
        output.append({
            "endpoint": rule.endpoint,
            "methods": methods,
            "route": str(rule)
        })
    return {"routes": output}
if __name__ == '__main__':

    app.run(debug=True)
