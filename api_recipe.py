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
    # get all rows from recipes table and convert them into an array of dictionaries
    all_recipes = cur.execute('SELECT * FROM recipes;').fetchall()
    conn.close()

    # return all recipes
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
    # Based on the http method, call their corresponding handling function
    if request.method == 'GET':
        return do_get()
    if request.method == 'POST':
        return do_post()
    if request.method == 'DELETE':
        return do_delete()
    if request.method == 'PATCH':
        return do_patch()


# Process request for fetching one or more recipes
# 1. get the query parameters from request
# 2. construct a select statement with the data
# 3. execute the select statement to fetch the recipes from recipes table
def do_get():
    # request.args
    query_parameters = request.args
    # get the query parameters from request
    recipe_id = query_parameters.get('Id')
    name = query_parameters.get('Name')
    category = query_parameters.get('Category')

    # construct a select statement with the parameters
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

    # remove the extra ' AND' from end of the string
    query = query[:-4] + ";"

    # connect to the database
    conn = sqlite3.connect('recipes.db')
    conn.row_factory = dict_factory
    cur = conn.cursor()

    # execute the select statement and convert all rows into an array of dictionaries
    results = cur.execute(query, to_filter).fetchall()
    conn.close()

    # convert the array into a json and return it
    return jsonify(results)


# Process request for adding a recipe
# 1. get the json data from the request
# 2. construct an insert statement with the data
# 3. execute the insert statement to add the recipe as a row in recipes table
# 4. return recipe id in json as the response
def do_post():
    # get the json data from the request
    results = request.get_json()
    name_value = results.get('Name')
    ingredients_value = results.get('Ingredients')
    instruction_value = results.get('Instruction')
    serving_size_value = results.get('Serving_Size')
    category_value = results.get('Category')
    notes_value = results.get('Notes')

    # get the current system time and use it as "Date_Added" and "Date_Modified"
    now = datetime.datetime.now()
    create_time = str(now)
    modify_time = str(now)

    # generate a uuid and use it as the id of the recipe
    recipe_id = str(uuid.uuid1())

    # Connecting to the database file
    conn = sqlite3.connect("recipes.db")
    cur = conn.cursor()

    # construct an insert statement with input data
    insert_statement = "INSERT INTO recipes (Name, Ingredients, Instruction, Serving_Size, " \
                       "Category, Notes, Date_Added, Date_Modified, Id) " \
                       "VALUES ('{Name_Value}', '{Ingredients_Value}', '{Instruction_Value}', " \
                       "{Serving_Size_Value}, '{Category_Value}', '{Notes_Value}', '{Date_Added_V}', " \
                       "'{Date_Modified_V}', '{Id_Value}')"\
                       .format(Name_Value=name_value, Ingredients_Value=ingredients_value,
                               Instruction_Value=instruction_value, Serving_Size_Value=serving_size_value,
                               Category_Value=category_value, Notes_Value=notes_value, Date_Added_V=create_time,
                               Date_Modified_V=modify_time, Id_Value=recipe_id)
    # execute the insert statement
    try:
        cur.execute(insert_statement)
    except sqlite3.IntegrityError:
        print('ERROR: insert failed')
        return server_error(500)

    conn.commit()
    conn.close()

    # return the recipe id in the response
    return '{"Id":"' + recipe_id + '"}'


# Process request for deleting a recipe
# 1. get the query parameter 'Id' from request
# 2. construct a delete statement based on Id
# 3. execute the delete statement to delete the recipe identified by 'Id' from recipes table
def do_delete():
    # get the query parameter 'Id' from request.
    query_parameters = request.args
    recipe_id = query_parameters.get('Id')
    if not recipe_id:
        return bad_request(400)

    # construct a delete statement based on Id
    delete_statement = "DELETE FROM recipes WHERE id=?"
    to_filter = []
    to_filter.append(recipe_id)

    # Connecting to the database file
    conn = sqlite3.connect('recipes.db')
    cur = conn.cursor()

    # execute the delete statement to delete the recipe
    cur.execute(delete_statement, to_filter)
    conn.commit()
    conn.close()

    # return a confirmation message
    return 'Recipe ' + recipe_id + ' deleted.'


# Process request for editing a recipe
# 1. get the query parameter 'Id' from request
# 2. get the json data from the request
# 3. construct an update statement with the data
# 4. execute the update statement to update the recipe identified by 'Id' in recipes table
def do_patch():
    # get the query parameter 'Id' from request
    query_parameters = request.args
    recipe_id = query_parameters.get('Id')
    if not recipe_id:
        return bad_request(400)

    # get the json data from the request
    results = request.get_json()
    name_value = results.get('Name')
    ingredients_value = results.get('Ingredients')
    instruction_value = results.get('Instruction')
    serving_size_value = results.get('Serving_Size')
    category_value = results.get('Category')
    notes_value = results.get('Notes')

    # construct an update statement with the data.
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

    # at least one attribute needs to be passed in the request, or return 400 error
    if not (name_value or ingredients_value or instruction_value or serving_size_value or notes_value or category_value):
        return bad_request(400)

    # get the current time for "Date_Modified"
    now = datetime.datetime.now()
    modify_time = str(now)

    update_statement = update_statement + ' Date_Modified=?'
    to_filter.append(modify_time)

    update_statement = update_statement + ' WHERE id=?'
    to_filter.append(recipe_id)

    # Connecting to the database file
    conn = sqlite3.connect('recipes.db')
    cur = conn.cursor()

    # execute the update statement
    cur.execute(update_statement, to_filter)
    conn.commit()
    conn.close()

    # return confirmation message
    return 'Recipe ' + recipe_id + ' updated.'


# start the application
app.run()
