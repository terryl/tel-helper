from flask import Flask
from config import Config
from models import db

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    db.init_app(app)
    
    with app.app_context():
        db.create_all()
    
    from routes.account_routes import account_bp
    from routes.message_routes import message_bp
    from routes.reply_routes import reply_bp
    from routes.scanner_routes import scanner_bp
    
    app.register_blueprint(account_bp, url_prefix='/accounts')
    app.register_blueprint(message_bp, url_prefix='/messages')
    app.register_blueprint(reply_bp, url_prefix='/replies')
    app.register_blueprint(scanner_bp, url_prefix='/scanner')
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
