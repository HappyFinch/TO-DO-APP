# encoding utf-8
from flask import Flask,render_template,url_for,redirect,request,jsonify,abort
from flask_sqlalchemy import SQLAlchemy
import sys 
from flask_migrate import Migrate

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:postgres123@localhost:5432/todoapp'
# 其他适配器的写法，如psycopg2：
# app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql+psycopg2://postgres:postgres123@localhost:5432/example'
db = SQLAlchemy(app)
# db 是与我们的数据库交互的接口
# db.Model 创建和操作 数据模型
# db.session 创建和操作 数据库事务
migrate = Migrate(app,db)  # 创建迁移类

class Todo(db.Model):
  __tablename__ = 'todos'  # 用于给表起名字
  id = db.Column(db.Integer, primary_key=True)
  description = db.Column(db.String(), nullable=False)
  completed = db.Column(db.Boolean,nullable = False,default = False)
  list_id = db.Column(db.Integer, db.ForeignKey('todolists.id'),nullable = False)
  
  def __repr__(self):
    return f'<Todo ID: {self.id}, description: {self.description}>'

class Todolist(db.Model):   # 待办分类的表
   __tablename__ = 'todolists'  # 用于给表起名字
   id = db.Column(db.Integer, primary_key=True)
   name = db.Column(db.String(), nullable=False)
   completed = db.Column(db.Boolean,nullable = False,default = False)
   todos = db.relationship('Todo',backref = 'list', lazy = True)


ctx = app.app_context()
ctx.push()  # 这两句话解决没有content push 导致的报错
# db.create_all()  # 没有则创建表，表存在的话不做任何操作(用了迁移之后 不需要这句话了)

# # 在表中添加新记录的方式  ① 以下方法 或 ②通过cmd中的psql 中用sql语句进行添加
# person = Person(name='Amy')
# db.session.add(person)  # 事务的方式创建
# db.session.commit()

# todolist的完成框修改
@app.route('/todolists/<todolist_id>/set-completed', methods=['POST']) 
def set_completed_todolist(todolist_id):
  try:
    completed = request.get_json()['completed']
    todolist = Todolist.query.get(todolist_id)
    todolist.completed = completed
    if completed == True:
      todos = Todo.query.filter_by(list_id=todolist_id).all()
      for i in todos:
        i.completed = completed     
      # todos = todolist.todos   # 不会用
      # todos.completed = completed
    db.session.commit()
  except:
    db.session.rollback()
  finally:
    db.session.close()
  return redirect(url_for('index'))

@app.route('/todolists/<todolist_id>', methods=['DELETE'])
def delete_todolist(todolist_id):
  try:
    deleted_id = Todolist.query.filter_by(id=todolist_id)
    db.session.delete(deleted_id)
    db.session.commit()
  except:
    db.session.rollback()
  finally:
    db.session.close()
    return redirect(url_for('index'))
  

@app.route('/todolists/create',methods = ['POST'])
def create_todolist():
  error = False
  body ={}
  try:
    name = request.get_json()['name'] # 获取用户输入的数据
    todolist = Todolist(name=name)  # 创建一条记录
    db.session.add(todolist)
    db.session.commit()
    body['name'] = todolist.name
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info)
  finally:
    db.session.close()
  if not error:
    return jsonify(body)
  else:
    abort (500)  

@app.route('/todos/create',methods = ['POST'])
def create_todo():
  error = False
  body ={}
  try:
    description = request.get_json()['description'] # 获取用户输入的数据
    list_id = request.get_json()['list_id']
    todo = Todo(description=description)  # 创建一条记录
    active_list = Todolist.query.get(list_id)
    todo.list = active_list
    db.session.add(todo)
    db.session.commit()
    body['description'] = todo.description
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info)
  finally:
    db.session.close()
  if not error:
    return jsonify(body)
  else:
    abort (500)  


@app.route('/todos/<todo_id>', methods=['DELETE'])
def delete_todo(todo_id):
  try:
    Todo.query.filter_by(id=todo_id).delete()
    db.session.commit()
  except:
    db.session.rollback()
  finally:
    db.session.close()
  return jsonify({ 'success': True })

@app.route('/todos/<todo_id>/set-completed', methods=['POST'])
def set_completed_todo(todo_id):
  change = False
  listid = 0
  try:
    completed = request.get_json()['completed']
    print('completed', completed)
    todo = Todo.query.get(todo_id)
    todo.completed = completed
    if completed == False:
      if todo.list_id == True:
        change = True
        listid = todo.list_id
    db.session.commit()
  except:
    db.session.rollback()
  finally:
    db.session.close()
  return jsonify({'change':change,'listid':listid})

@app.route('/lists/<list_id>')
def get_list_todos(list_id):
    # 一些查询语句：
    # >>> query = Person.query.filter(Person.name == 'Amy')
    return render_template('index.html',
    todolists = Todolist.query.order_by('id').all(), 
    active_list = Todolist.query.get(list_id),
    todos = Todo.query.filter_by(list_id=list_id).order_by('id').all())

@app.route('/')
def index():
    return redirect(url_for('get_list_todos',list_id = 1))

@app.route('/about')
def about():
    return render_template('about.html')

if __name__ == '__main__':
    app.run(debug=True)