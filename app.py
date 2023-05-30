from flask import Flask, render_template, jsonify, request
import json
import pickle
import uuid
from datetime import datetime

app = Flask(__name__)

""" # A json fájl betöltése
with open('projects.json', 'r') as file:
    projects_json = json.load(file)
    
# A projects változó konvertálása pickle formátumba és kiírása a projects.pickle fájlba
with open('projects.pickle', 'wb') as file:
    pickle.dump(projects_json, file)

# A projects változó beolvasása a pickle fájlból
with open('projects.pickle', 'rb') as file:
    data = pickle.load(file)
    projects = data['projects'] """

def save_data(data):
    with open('projects.pickle', 'wb') as file:
        pickle.dump(data, file)

def load_data():
    try:
        with open('projects.pickle', 'rb') as file:
            return pickle.load(file)
    except FileNotFoundError:
        return {"projects": []}
    
""" projects = [{
    'name': 'my first project',
    'tasks': [{
        'name': 'my first task',
        'completed': False
    }]
}] """


@app.route("/")
def home():
  return render_template("index.html.j2", name="Tomi")


@app.route("/projects")
def get_projects():
    return jsonify(load_data()), 200, {
        'Access-Control-Allow-Origin': 'http://127.0.0.1:8080'
    }


@app.route("/project", methods=['POST'])
def create_project():
    request_data = request.get_json()

    tasks = request_data.get('tasks', [])
    for task in tasks:
        task['task_id'] = uuid.uuid4().hex[:24]
        checklists = task.get('checklist', [])
        for checklist in checklists:
            checklist['checklist_id'] = uuid.uuid4().hex[:24]

    new_project = {
        'project_id': uuid.uuid4().hex[:24],
        'name': request_data['name'],
        'creation_date': datetime.utcnow().isoformat() + 'Z',  # add current UTC time in ISO 8601 format
        'completed': request_data['completed'],
        'tasks': tasks
    }
    
    data = load_data()
    data['projects'].append(new_project)
    save_data(data)

    return jsonify({'message': f'project created with id: {new_project["project_id"]}'}), 201


@app.route("/project/<string:project_id>")
def get_project(project_id):
    for project in load_data()['projects']:
        if project['project_id'] == project_id:
            return jsonify(project)
    return jsonify({'message': 'project not found'}), 404


@app.route("/project/<string:project_id>/tasks")
def get_project_tasks(project_id):
    for project in load_data()['projects']:
        if project['project_id'] == project_id:
            return jsonify({'tasks': project['tasks']})
    return jsonify({'message': 'project not found'}), 404


@app.route("/project/<string:project_id>/task", methods=['POST'])
def add_task_to_project(project_id):
    request_data = request.get_json()
    data = load_data()
    for project in data['projects']:
        if 'project_id' in project and project['project_id'] == project_id:
            if 'completed' not in request_data or type(
                    request_data['completed']) is not bool:
                return jsonify(
                    {'message': 'completed is required and must be a boolean'}), 400
            new_task = {
                'task_id': uuid.uuid4().hex[:24],
                'name': request_data['name'],
                'completed': request_data['completed']
            }
            project['tasks'].append(new_task)
            save_data(data)
            return jsonify(new_task), 201
    return jsonify({'message': 'project not found'}), 404

if __name__ == "__main__":
    app.run(debug=True)