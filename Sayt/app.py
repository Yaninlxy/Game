from flask import Flask, render_template, request, redirect
import sqlite3

app = Flask(__name__)

# Функция для получения задач из базы данных
def get_tasks():
    conn = sqlite3.connect('tasks.db')
    c = conn.cursor()
    c.execute('SELECT rowid, task FROM tasks')
    tasks = c.fetchall()
    conn.close()
    return tasks

# Функция для добавления задачи в базу данных
def add_task(task):
    conn = sqlite3.connect('tasks.db')
    c = conn.cursor()
    c.execute('INSERT INTO tasks (task) VALUES (?)', (task,))
    conn.commit()
    conn.close()

# Функция для удаления задачи
def delete_task(task_id):
    conn = sqlite3.connect('tasks.db')
    c = conn.cursor()
    c.execute('DELETE FROM tasks WHERE rowid = ?', (task_id,))
    conn.commit()
    conn.close()

# Функция для редактирования задачи
def edit_task(task_id, new_task):
    conn = sqlite3.connect('tasks.db')
    c = conn.cursor()
    c.execute('UPDATE tasks SET task = ? WHERE rowid = ?', (new_task, task_id))
    conn.commit()
    conn.close()

# Создание таблицы, если она не существует
def init_db():
    conn = sqlite3.connect('tasks.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS tasks (
            task TEXT
        )
    ''')
    conn.commit()
    conn.close()

# Инициализируем базу данных
init_db()

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/todo', methods=['GET', 'POST'])
def todo():
    if request.method == 'POST':
        task = request.form.get('task')
        if task:
            add_task(task)
        return redirect('/todo')
    tasks = get_tasks()
    return render_template('todo.html', tasks=tasks)

@app.route('/delete/<int:task_id>')
def delete(task_id):
    delete_task(task_id)
    return redirect('/todo')

@app.route('/edit/<int:task_id>', methods=['GET', 'POST'])
def edit(task_id):
    if request.method == 'POST':
        new_task = request.form.get('task')
        if new_task:
            edit_task(task_id, new_task)
        return redirect('/todo')
    task = get_tasks()
    task_to_edit = next(t for t in task if t[0] == task_id)
    return render_template('edit.html', task=task_to_edit)

if __name__ == '__main__':
    app.run(debug=True)
