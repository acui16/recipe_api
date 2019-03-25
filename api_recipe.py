import flask
from flask import request, jsonify
import sqlite3
import datetime
import uuid

# get a web application instance
app = flask.Flask(__name__)
app.config["DEBUG"] = True


# Read a table row into a dictionary
def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


# Endpoint for path=/
@app.route('/', methods=['GET'])
def home():
    return '''<h1>Welcome to the recipe archive!</h1>
<p>A prototype API for recipes.</p>'''


# Endpoint for /api/v1/resources/recipes/all. It returns all existing recipes.
@app.route('/api/v1/resources/recipes/all', methods=['GET'])
def api_all():
    conn = sqlite3.connect('recipes.db')
    conn.row_factory = dict_factory
    cur = conn.cursor()
    all_recipes = cur.execute('SELECT * FROM recipes;').fetchall()

    return jsonify(all_recipes)


# Returns error message for status code 400
@app.errorhandler(400)
def bad_request(e):
    return "The request is not valid, status=400"


# Returns error message for status code 404
@app.errorhandler(404)
def resource_not_found(e):
    return "The resource could not be found, status=404"


# Returns error message for status code 500
@app.errorhandler(500)
def server_error(e):
    return "The server encountered an error, status=500"


# Endpoint for /api/v1/resources/recipes. It handles Fetch/Add/Edit/Delete recipes.
@app.route('/api/v1/resources/recipes', methods=['GET', 'POST', 'PATCH', 'DELETE'])
def handle_request():
    if request.method == 'GET':
        return do_get()
    if request.method == 'POST':
        return do_post()
    if request.method == 'DELETE':
        return do_delete()
    if request.method == 'PATCH':
        return do_patch()


# Process request for fetching a recipe
def do_get():
    query_parameters = request.args

    recipe_id = query_parameters.get('Id')
    name = query_parameters.get('Name')
    category = query_parameters.get('Category')

    query = "SELECT * FROM recipes WHERE"
    to_filter = []

    if recipe_id:
        query += ' id=? AND'
        to_filter.append(recipe_id)
    if name:
        query += ' name=? AND'
        to_filter.append(name)
    if category:
        query += ' category=? AND'
        to_filter.append(category)
    if not (recipe_id or name or category):
        return resource_not_found(404)

    query = query[:-4] + ";"

    conn = sqlite3.connect('recipes.db')
    conn.row_factory = dict_factory
    cur = conn.cursor()

    results = cur.execute(query, to_filter).fetchall()
    conn.close()
    return jsonify(results)


# Process request for adding a recipe
def do_post():
    results = request.get_json()
    name_value = results.get('Name')
    ingredients_value = results.get('Ingredients')
    instruction_value = results.get('Instruction')
    serving_size_value = results.get('Serving_Size')
    category_value = results.get('Category')
    notes_value = results.get('Notes')

    now = datetime.datetime.now()
    create_time = str(now)
    modify_time = str(now)

    recipe_id = str(uuid.uuid1())

    # Connecting to the database file
    conn = sqlite3.connect("recipes.db")
    cur = conn.cursor()

    insert_statement = "INSERT INTO recipes (Name, Ingredients, Instruction, Serving_Size, " \
                       "Category, Notes, Date_Added, Date_Modified, Id) " \
                       "VALUES ('{Name_Value}', '{Ingredients_Value}', '{Instruction_Value}', " \
                       "{Serving_Size_Value}, '{Category_Value}', '{Notes_Value}', '{Date_Added_V}', " \
                       "'{Date_Modified_V}', '{Id_Value}')"\
                       .format(Name_Value=name_value, Ingredients_Value=ingredients_value,
                               Instruction_Value=instruction_value, Serving_Size_Value=serving_size_value,
                               Category_Value=category_value, Notes_Value=notes_value, Date_Added_V=create_time,
                               Date_Modified_V=modify_time, Id_Value=recipe_id)
    try:
        cur.execute(insert_statement)
    except sqlite3.IntegrityError:
        print('ERROR: insert failed')
        return server_error(500)

    conn.commit()
    conn.close()
    return 'Recipe ' + name_value + ' with Id=' + recipe_id + ' created.'


# Process request for deleting a recipe
def do_delete():
    query_parameters = request.args
    recipe_id = query_parameters.get('Id')
    if not recipe_id:
        return bad_request(400)

    delete_statement = "DELETE FROM recipes WHERE id=?"
    to_filter = []
    to_filter.append(recipe_id)

    # Connecting to the database file
    conn = sqlite3.connect('recipes.db')
    cur = conn.cursor()
    cur.execute(delete_statement, to_filter)
    conn.commit()
    conn.close()
    return 'Recipe ' + recipe_id + ' deleted.'


# Process request for editing a recipe
def do_patch():
    query_parameters = request.args
    recipe_id = query_parameters.get('Id')
    if not recipe_id:
        return bad_request(400)

    results = request.get_json()
    name_value = results.get('Name')
    ingredients_value = results.get('Ingredients')
    instruction_value = results.get('Instruction')
    serving_size_value = results.get('Serving_Size')
    category_value = results.get('Category')
    notes_value = results.get('Notes')

    update_statement = "UPDATE recipes SET"
    to_filter = []
    if name_value:
        update_statement = update_statement + ' name=?,'
        to_filter.append(name_value)
    if ingredients_value:
        update_statement = update_statement + ' ingredients=?,'
        to_filter.append(ingredients_value)
    if instruction_value:
        update_statement = update_statement + ' instruction=?,'
        to_filter.append(instruction_value)
    if serving_size_value:
        update_statement = update_statement + ' serving_Size=?,'
        to_filter.append(serving_size_value)
    if notes_value:
        update_statement = update_statement + ' notes=?,'
        to_filter.append(notes_value)
    if category_value:
        update_statement = update_statement + ' category=?,'
        to_filter.append(category_value)

    if not (name_value or ingredients_value or instruction_value or serving_size_value or notes_value or category_value):
        return bad_request(400)

    now = datetime.datetime.now()
    modify_time = str(now)

    update_statement = update_statement + ' Date_Modified=?'
    to_filter.append(modify_time)

    update_statement = update_statement + ' WHERE id=?'
    to_filter.append(recipe_id)

    # Connecting to the database file
    conn = sqlite3.connect('recipes.db')
    cur = conn.cursor()

    cur.execute(update_statement, to_filter)
    conn.commit()
    conn.close()

    return 'Recipe ' + recipe_id + ' updated.'


app.run()
