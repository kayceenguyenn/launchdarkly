from flask import Flask
from dotenv import load_dotenv
import os

load_dotenv()

from routes.quote import quote_bp
from routes.history import history_bp
from routes.fundamentals import fundamentals_bp
from routes.news import news_bp
from routes.search import search_bp
from routes.indicators import indicators_bp
from routes.movers import movers_bp
from routes.health import health_bp

app = Flask(__name__)

app.register_blueprint(quote_bp)
app.register_blueprint(history_bp)
app.register_blueprint(fundamentals_bp)
app.register_blueprint(news_bp)
app.register_blueprint(search_bp)
app.register_blueprint(indicators_bp)
app.register_blueprint(movers_bp)
app.register_blueprint(health_bp)

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(debug=True, port=port)
