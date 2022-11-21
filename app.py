# encoding utf-8
from flask import Flask,render_template,url_for,redirect,request,jsonify
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:postgres123@localhost:5432/todoapp'
# 其他适配器的写法，如psycopg2：
# app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql+psycopg2://postgres:postgres123@localhost:5432/example'
db = SQLAlchemy(app)
# db 是与我们的数据库交互的接口
# db.Model 创建和操作 数据模型
# db.session 创建和操作 数据库事务

class Todo(db.Model):
  __tablename__ = 'todos'  # 用于给表起名字
  id = db.Column(db.Integer, primary_key=True)
  description = db.Column(db.String(), nullable=False)
  
  def __repr__(self):
    return f'<Todo ID: {self.id}, description: {self.description}>'

ctx = app.app_context()
ctx.push()  # 这两句话解决没有content push 导致的报错
db.create_all()  # 没有则创建表，表存在的话不做任何操作

# # 在表中添加新记录的方式  ① 以下方法 或 ②通过cmd中的psql 中用sql语句进行添加
# person = Person(name='Amy')
# db.session.add(person)  # 事务的方式创建
# db.session.commit()

@app.route('/')
def index():
    # 一些查询语句：
    # >>> query = Person.query.filter(Person.name == 'Amy')
    # >>> query.first()
    # >>> query.all()
    return render_template('index.html',data = Todo.query.all())

@app.route('/todos/create',methods = ['POST'])
def create_todo():
  description = request.get_json()['description'] # 获取用户输入的数据
  todo = Todo(description=description)  # 创建一条记录
  db.session.add(todo)
  db.session.commit()
  return jsonify({
    'description':todo.description
  })

@app.route('/about')
def about():
    return render_template('about.html')

if __name__ == '__main__':
    app.run(debug=True)