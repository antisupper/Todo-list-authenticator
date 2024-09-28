from flask import Flask, render_template, request, redirect, session, flash, url_for
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
app = Flask(__name__)
app.secret_key = 'your_secret_key'

app.config["SQLALCHEMY_DATABASE_URI"] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    password_hash = db.Column(db.String(40), unique=True, nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
class Todo(db.Model):
    """A Model for an Item in the Todo List

    Args:
        db (_type_): database model

    Returns:
        __repr__: string rep.
    """
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(200), nullable=False)
    completed = db.Column(db.Integer, default=0)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        # f"Task {self.id}
        return '<Task %r' % self.id

@app.route("/")
def home():
    if 'username' in session:
        tasks = Todo.query.order_by(Todo.date_created).all()
        return render_template('dashboard.html', username=session['username'], tasks=tasks)
    return render_template('index.html')

@app.route("/login", methods=["POST"])
def login():
    username = request.form['username']
    password = request.form['password']

    user = User.query.filter_by(username=username).first()
    if user and user.check_password(password):
        session['username'] = username
        return redirect(url_for('dashboard'))
    else:
        flash("Invalid username....")
        return render_template('index.html', error="WRONG INFO...")
    
@app.route("/register", methods=['POST'])
def register():
    username = request.form['username']
    password = request.form['password']

    user = User.query.filter_by(username=username).first()
    if user:
        flash("This username has already been used")
        return render_template("index.html", error="username already exits")
    else:
        new_user = User(username=username)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()
        session['username'] = username
        return redirect(url_for('dashboard'))
    
@app.route('/dashboard')
def dashboard():
    if 'username' in session:
        tasks = Todo.query.order_by(Todo.date_created).all()
        return render_template('dashboard.html', username=session['username'], tasks=tasks)
    return redirect(url_for('home'))

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('home'))

@app.route('/', methods=["POST","GET"])
def add():
    """Main page for App

    Returns:
        page: home page
    """
    if request.method == "POST":
        task_content = request.form['content']
        new_task = Todo(content=task_content)
        try:
            db.session.add(new_task)
            db.session.commit()
            return redirect("/")
        except Exception as e:
            print(f"Error:{e}")
            return redirect('/')


@app.route("/delete/<int:id>")
def delete(id):
    task_to_delete = Todo.query.get_or_404(id)
    try:
        db.session.delete(task_to_delete)
        db.session.commit()
        return redirect("/")
    except Exception as e:
        print(f"ERROR:{e}")

@app.route("/update/<int:id>", methods = ["GET", "POST"])
def update(id:int):
    task = Todo.query.get_or_404(id)
    if request.method == "POST":
        task.content = request.form["content"]
        try:
            db.session.commit()
            return redirect("/")
        except Exception as e:
            print(f"ERROR:{e}")
    else:
        return render_template("update.html", task = task)


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug = True)