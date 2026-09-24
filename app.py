# Rohail 
# I have used Flask framework with Json for backend.
# To store the data, I used the CSV at the backend to store and show the data.



# Imported modules
from flask import Flask, render_template, request, jsonify
import csv
import os


# This will be shown in the heading of frontend linked.
app = Flask(__name__)
CSV_FILE = os.path.join(os.path.dirname(__file__), 'tasks.csv')
FIELDNAMES = ['id', 'title', 'priority', 'due_date', 'status']


# Opening the CSv file with the headers
def init_csv():
    # Creating the header row for the CSV
    if not os.path.exists(CSV_FILE):
        with open(CSV_FILE, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
            writer.writeheader()




# This will read every line into the Dictionary
def read_tasks():
    init_csv()
    with open(CSV_FILE, 'r', newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        return list(reader)

# Writing down the actual tasks.
def write_tasks(tasks):
    with open(CSV_FILE, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(tasks)

# Going to the next lin.
def get_next_id(tasks):
    if not tasks:
        return 1
    return max(int(t['id']) for t in tasks) + 1


# Actual Page of frontend
@app.route('/')
def index():
    return render_template('index.html')


# This is will return all of the tasks as the json file.
@app.route('/api/tasks', methods=['GET'])
def get_tasks():
    tasks = read_tasks()
    return jsonify(tasks), 200



# This will recieve a new task as Json and append into the csv file attached in the folder. 
@app.route('/api/tasks', methods=['POST'])
def add_task():
    data = request.get_json(silent=True) or {}
    title = (data.get('title') or '').strip()
    priority = (data.get('priority') or '').strip()
    due_date = (data.get('due_date') or '').strip()

    # Handling the error.
    if not title or not priority or not due_date:
        return jsonify({'error': 'Title, priority and due date are all required.'}), 400
    tasks = read_tasks()
    new_task = {
        'id': str(get_next_id(tasks)),
        'title': title,
        'priority': priority,
        'due_date': due_date,
        'status': 'Pending'
    }
    tasks.append(new_task)
    write_tasks(tasks)
    return jsonify(new_task), 201




# Recieve the user side and change the status.
@app.route('/api/tasks/complete', methods=['POST'])
def complete_task():
    data = request.get_json(silent=True) or {}
    task_id = str(data.get('id', '')).strip()
    if not task_id:
        return jsonify({'error': 'Task id is required.'}), 400
    tasks = read_tasks()
    found = False
    for t in tasks:
        if t['id'] == task_id:
            t['status'] = 'Completed'
            found = True
            break # exit from this block

    if not found: # Otherwise! 
        return jsonify({'error': f'Task with id {task_id} not found.'}), 404
    write_tasks(tasks)
    return jsonify({'message': 'Task marked complete.'}), 200




# This is the delete feature 
@app.route('/api/tasks/<task_id>', methods=['DELETE'])
def delete_task(task_id):
   
    task_id = str(task_id).strip()
    tasks = read_tasks()

    remaining_tasks = [task for task in tasks if task['id'] != task_id]
    # if the task not found
    if len(remaining_tasks) == len(tasks):
        return jsonify({
            'error': f'Task with id {task_id} not found.'
        }), 404
    # Rewrite without CSV

    write_tasks(remaining_tasks)

    return jsonify({
        'message': 'Task deleted successfully.'
    }), 200



# Resolving the error
if __name__ == '__main__':
    init_csv()

    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
