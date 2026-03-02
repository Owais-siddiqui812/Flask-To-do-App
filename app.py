from flask import Flask, render_template, request, session, redirect
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import os 
app= Flask(__name__,template_folder='templates')

basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'task.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'mysecretkey'
db = SQLAlchemy(app)
class User(db.Model):
    __tablename__='users'
    id=db.Column(db.Integer,primary_key=True)
    username=db.Column(db.String(100),unique=True,nullable=False)
    password=db.Column(db.String(100),nullable=False)
    
class Task(db.Model):
    __tablename__='tasks'
    id=db.Column(db.Integer,primary_key=True)
    n_task=db.Column(db.String(200),nullable=False)
    start_date=db.Column(db.String(10),nullable=False)
    end_date=db.Column(db.String(10),nullable=False)
    completed=db.Column(db.Boolean,default=False)
    user_id=db.Column(db.Integer,db.ForeignKey('users.id'),nullable=False)
with app.app_context():
    db.create_all()
    
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method=='POST':
        username=request.form.get('username')
        password=request.form.get('password')
        if User.query.filter_by(username=username).first():
            return 'Username already exists'
        hashed_password = generate_password_hash(password)
        new_user=User(username=username,password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        return redirect('/login')
    return render_template('register.html')
        
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method=='POST':
        username=request.form.get('username')
        password=request.form.get('password')
        user=User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            return redirect('/')
        else:
            return 'Invalid credentials'
    return render_template('login.html')



def update_task_status(user_tasks):
    """Update the status of each task based on the current date."""
    today = datetime.today().date()
    
    for task in user_tasks:
        start_date = datetime.strptime(task.start_date, '%Y-%m-%d').date()
        end_date = datetime.strptime(task.end_date, '%Y-%m-%d').date()

        if task.completed:
            task.status = "✅ Completed"
        elif today < start_date:
            task.status = "📅 Upcoming"
        elif start_date <= today <= end_date:
            task.status = "⏳ Ongoing"
        else:
            task.status = "⏳ Expired"


@app.route('/')
def home():
    if 'user_id' not in session:
        return redirect('/login')
    user_tasks = Task.query.filter_by(user_id=session['user_id']).all()
    update_task_status(user_tasks)  # Update task statuses before rendering
    return render_template('index.html', tasks=user_tasks)

@app.route('/add', methods=['POST'])
def add():
    if 'user_id' not in session:
        return redirect('/login')
    task = request.form.get('task')
    start_date = request.form.get('start_date')
    end_date = request.form.get('end_date')

    new_task = Task(
        n_task=task, start_date=start_date, end_date=end_date, user_id=session['user_id']
    )
    db.session.add(new_task)
    db.session.commit()
    return redirect('/')

@app.route('/delete/<int:id>')
def delete(id):
    if 'user_id' not in session:
        return redirect('/login')

    task = Task.query.get_or_404(id)

    if task.user_id == session['user_id']:
        db.session.delete(task)
        db.session.commit()

    return redirect('/')

@app.route('/completed/<int:id>')
def completed(id):
    if 'user_id' not in session:
        return redirect('/login')

    task = Task.query.get_or_404(id)

    if task.user_id == session['user_id']:
        task.completed = True
        db.session.commit()

    return redirect('/')

@app.route('/clear', methods=['POST'])
def clear():
    if 'user_id' not in session:
        return redirect('/login')
    Task.query.filter_by(user_id=session['user_id']).delete()
    db.session.commit()
    return redirect('/')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect('/login')

if __name__ == '__main__':
    app.run(debug=True)
