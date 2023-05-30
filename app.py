from flask import Flask, render_template, jsonify, request
import json
import pickle

app = Flask(__name__)

# A json fájl betöltése
with open('projects.json', 'r') as file:
    projects_json = json.load(file)
    
# A projects változó konvertálása pickle formátumba és kiírása a projects.pickle fájlba
with open('projects.pickle', 'wb') as file:
    pickle.dump(projects_json, file)

# A projects változó beolvasása a pickle fájlból
with open('projects.pickle', 'rb') as file:
    data = pickle.load(file)
    projects = data['projects']


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
  return jsonify({'projects': projects}), 200, {
      # add Access-Control-Allow-Origin header
      'Access-Control-Allow-Origin': 'http://127.0.0.1:8080'
  }


@app.route("/project", methods=['POST'])
def create_project():
  request_data = request.get_json()
  new_project = {'id': len(projects)+1, 'name': request_data['name'], 'tasks': request_data['tasks']}
  projects.append(new_project)
  return jsonify(new_project), 201


@app.route("/project/<string:project_id>")
def get_project(project_id):
  for project in projects:
    if project['project_id'] == project_id:
      return jsonify(project)
  return jsonify({'message': 'project not found'}), 404


@app.route("/project/<string:project_id>/tasks")
def get_project_tasks(project_id):
  for project in projects:
    if project['project_id'] == project_id:
      return jsonify({'tasks': project['tasks']})
  return jsonify({'message': 'project not found'}), 404


@app.route("/project/<string:project_id>/task", methods=['POST'])
def add_task_to_project(project_id):
  request_data = request.get_json()
  for project in projects:
    if 'project_id' in project and project['project_id'] == project_id:
      if 'completed' not in request_data or type(
          request_data['completed']) is not bool:
        return jsonify(
            {'message': 'completed is required and must be a boolean'}), 400
      new_task = {
          'name': request_data['name'],
          'completed': request_data['completed']
      }
      project['tasks'].append(new_task)
      return jsonify(new_task), 201
  return jsonify({'message': 'project not found'}), 404
