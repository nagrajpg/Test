from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy 

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'

db = SQLAlchemy(app)

class User(db.Model):
    user_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    login = db.Column(db.String(50))
    avatar = db.Column(db.String(50))
    user_type = db.Column(db.String(50))
    profile = db.Column(db.String(50))


@app.route('/user/<int:page_num>')
def user(page_num):
    users = User.query.paginate(per_page=25, page=page_num, error_out=True)

    return render_template('index.html', users=users)

if __name__ == '__main__':
    app.run(debug=True)