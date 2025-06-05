from flask import Flask, redirect, url_for, flash
from flask_wtf import FlaskForm, RecaptchaField
from wtforms import StringField,PasswordField
from wtforms.validators import InputRequired, length,AnyOf

from flask_wtf.csrf import CSRFProtect
import config
import extensions
from blueprints.general import app as general
from blueprints.admin import app as admin
from blueprints.user import app as user

from flask_login import LoginManager

from models.user import User

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = config.SQLALCHEMY_DATABASE_URI
app.config['SECRET_KEY'] = config.SECRET_KEY
extensions.db.init_app(app)

# Added2
app.config["RECAPTCHA_PUBLIC_KEY"] = config.RECAPTCHA_PUBLIC_KEY
app.config["RECAPTCHA_PRIVATE_KEY"] = config.RECAPTCHA_PRIVATE_KEY
# app.config["VERIFY_URL"] = config.VERIFY_URL
# app.config['TESTING']=True

app.register_blueprint(general)
app.register_blueprint(admin)
app.register_blueprint(user)


csrf = CSRFProtect(app)

login_manager = LoginManager()
login_manager.init_app(app)
@login_manager.user_loader
def load_user(user_id):
        # return User.get(user_id) or next line
        return User.query.filter(User.id == user_id).first()


@login_manager.unauthorized_handler
def unauthorized():
        flash('Please login!')
        return redirect(url_for('user.login'))


@app.context_processor
def inject_dict_for_all_templates():
    return dict(myconfig=config)

with app.app_context():
    extensions.db.create_all()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
