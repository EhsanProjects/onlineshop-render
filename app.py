from flask import Flask
from flask_wtf.csrf import CSRFProtect
import config
import extensions
from blueprints.general import app as general
from blueprints.admin import app as admin
from blueprints.user import app as user

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = config.SQLALCHEMY_DATABASE_URI
app.config['SECRET_KEY'] = config.SECRET_KEY
extensions.db.init_app(app)

app.register_blueprint(general)
app.register_blueprint(admin)
app.register_blueprint(user)
csrf = CSRFProtect(app)
with app.app_context():
    extensions.db.create_all()

if __name__ == '__main__':
    app.run(debug=True)
