from flask import Blueprint
app = Blueprint("general", __name__)

@app.route('/')
def main():  # put application's code here
    return 'Main page!'

@app.route('/about')
def about():  # put application's code here
    return 'about us!'