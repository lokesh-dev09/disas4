import os
import logging

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from werkzeug.middleware.proxy_fix import ProxyFix
from apscheduler.schedulers.background import BackgroundScheduler

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class Base(DeclarativeBase):
    pass


db = SQLAlchemy(model_class=Base)
# create the app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)  # needed for url_for to generate with https

# Configure the database (SQLite for development, can be changed to a proper DB for production)
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///disaster_data.db")
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Initialize the app with the extension
db.init_app(app)

# Create a scheduler for background data updates
scheduler = BackgroundScheduler()

with app.app_context():
    # Import the models here for table creation
    import models  # noqa: F401
    
    # Create all tables
    db.create_all()
    
    # Import and start data collection (only if not already running)
    from data_collection import setup_data_collection, initialize_reference_data
    
    # Initialize reference data (disaster types and states)
    initialize_reference_data()
    
    # Setup scheduled data collection (runs every 6 hours)
    if not scheduler.running:
        setup_data_collection(scheduler)
        scheduler.start()
        logger.info("Started background data collection scheduler")
