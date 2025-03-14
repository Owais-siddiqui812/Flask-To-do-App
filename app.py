
from flask import Flask, request, render_template,redirect,session
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)

basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///'+os.path.join(basedir,'Adb.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False
app.config['SECRET_KEY'] = 'your_secret_key_here'  # Secret key for session security

db=SQLAlchemy(app)
class Users(db.Model):
    __tablename__='users'
    id=db.Column(db.Integer,primary_key=True)
    username=db.Column(db.String(200),unique=True,nullable=False)
    password=db.Column(db.String(200),nullable=False)

class Task(db.Model):
    __tablename__='tasks'
    id=db.Column(db.Integer,primary_key=True)
    title=db.Column(db.String(200) ,nullable=False)
    Completed=db.Column(db.Boolean,default=False)
    created_on=db.Column(db.DateTime,server_default=db.func.now())
    user_id=db.Column(db.Integer,db.ForeignKey('users.id'),nullable=False)
    user = db.relationship('Users', backref=db.backref('tasks', lazy=True))
    
with app.app_context():
        db.create_all()
        
@app.route('/register',methods=['GET','POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if Users.query.filter_by(username=username).first():
            return 'Username already exists'
        
        New_user=Users(username=username,password=password)
        db.session.add(New_user)
        db.session.commit()
        return redirect('/login')
    
    return render_template('register.html')

@app.route('/login',methods=['GET','POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = Users.query.filter_by(username=username).first()
        if user and user.password == password:
            session['user_id']=user.id
            return redirect('/')
        else:
            return 'Invalid password'
        
    return render_template('login.html')

@app.route('/logout',methods=['GET','POST'])
def logout():
    session.pop('user_id',None)
    return redirect('/login')
                
    

@app.route('/')
def home():
    if 'user_id' not in session:
        return redirect('/login')

    # Corrected query
    tasks = Task.query.filter(Task.user_id == session['user_id']).all()
    
    return render_template('index.html', tasks=tasks)

@app.route('/add',methods=['POST'])
def add():
    if 'user_id' not in session:
        return redirect('/login')
    
    title=request.form.get('task')
    new_task=Task(title=title,user_id=session['user_id'])
    db.session.add(new_task)
    db.session.commit()
    return redirect('/')

@app.route('/delete/<int:task_id>')
def delete(task_id):
    if 'user_id'not in session:
        return redirect('/login')
    
    task=Task.query.get(task_id)
    if task and task.user_id == session['user_id']:  # Ensure user owns the task
        db.session.delete(task)
        db.session.commit()
    return redirect('/')

@app.route('/completed/<int:task_id>')
def completed(task_id):
    if 'user_id'not in session:
        return redirect('/login')
    
    task_c=Task.query.get(task_id)
    task_c.Completed=True
    db.session.commit()
    return redirect('/')
    

@app.route('/clear',methods=['POST'])
def clear():
    if 'user_id'not in session:
        return redirect('/login')
    Task.query.delete()
    db.session.commit()
    return redirect('/')


if __name__ == '__main__':
    app.run(debug=True)
    