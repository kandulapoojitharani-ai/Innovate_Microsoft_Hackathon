from flask import Flask, render_template, jsonify
from flask_cors import CORS
from config import Config
from database import init_db
from routes.api import api
from routes.webhooks import webhooks

def create_app():
    app = Flask(__name__, static_folder="static", template_folder="templates")
    app.config.from_object(Config)
    CORS(app, resources={r"/api/*": {"origins": app.config["CORS_ORIGINS"]}})
    init_db()
    app.register_blueprint(api, url_prefix="/api")
    app.register_blueprint(webhooks, url_prefix="/webhooks")

    @app.get("/")
    def index():
        return render_template("index.html")

    @app.get("/health")
    def health():
        return jsonify({"status": "ok", "service": "PulseOps API", "version": "1.0.0"})

    return app

app = create_app()
if __name__ == "__main__":
    import threading
    import webbrowser

    url = "http://127.0.0.1:5000"
    print("\\n" + "=" * 50)
    print("       PULSEOPS WEBSITE IS RUNNING")
    print("=" * 50)
    print(f"\\n Website URL: {url}")
    print("\\n Press CTRL+C to stop the server.")
    print("=" * 50 + "\\n")

    # Open the local website after the Flask server has had time to start.
    threading.Timer(1.5, lambda: webbrowser.open(url)).start()
    app.run(host="127.0.0.1", port=5000, debug=False)
