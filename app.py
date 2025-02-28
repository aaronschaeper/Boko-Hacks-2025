from flask import Flask
from extensions import db
from sqlalchemy import inspect
import os

# Import Blueprints
from routes.home import home_bp
from routes.hub import hub_bp
from routes.login import login_bp
from routes.register import register_bp
from routes.about import about_bp
from routes.apps import apps_bp
from routes.notes import notes_bp
from routes.admin import admin_bp, init_admin_db
from routes.files import files_bp
from routes.retirement import retirement_bp
from routes.news import news_bp  # Import the new news blueprint

# Import Models
from models.user import User
from models.note import Note
from models.admin import Admin
from models.file import File

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "supersecretkey")  # Use environment variable for security

# Database Configuration
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///boko_hacks.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Secure Uploads Folder
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Initialize Database
db.init_app(app)

# Register Blueprints
app.register_blueprint(home_bp)
app.register_blueprint(hub_bp)
app.register_blueprint(login_bp)
app.register_blueprint(register_bp)
app.register_blueprint(about_bp)
app.register_blueprint(apps_bp)
app.register_blueprint(notes_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(files_bp)
app.register_blueprint(news_bp)
app.register_blueprint(retirement_bp) 

def setup_database():
    """Setup database and initialize the default admin securely."""
    with app.app_context():
        inspector = inspect(db.engine)
        existing_tables = inspector.get_table_names()

        if not existing_tables:
            print("⚠️ No existing tables found. Creating new tables...")
            db.create_all()  # Create all tables
            init_admin_db()  # Initialize default admin
        else:
            print("✅ Existing tables found:", existing_tables)
            db.create_all()  # Ensure all models are in sync
            
        # Debugging - Print table structures
        debug_tables = ['users', 'notes', 'admins', 'files']
        for table in debug_tables:
            if table in inspector.get_table_names():
                print(f"\n📌 {table.capitalize()} table columns:")
                for column in inspector.get_columns(table):
                    print(f"- {column['name']}: {column['type']}")
            else:
                print(f"❌ {table} table does not exist!")

# Run the app
if __name__ == "__main__":
    setup_database()  # Ensure database and admin setup
    app.run(debug=True)
