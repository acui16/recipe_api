
# README
# recipe_api
# Recipe RESTful API

# About
This is a RESTful API for adding, fetching, editing, and deleting a recipe. The project uses Python's Flask to build the RESTful API and Sqlite DB to store recipes.


# Adding a Recipe
HTTP Method: POST
URL: http://127.0.0.1:5000/api/v1/resources/recipes
Header: Content-Type: application/json
Body:
{
        "Category": "Sides",
        "Ingredients": "3 medium russet potatoes, 1 tablespoon olive oil",
        "Instruction": "1) Peel the potatoes and cut them into 1/4 inch by 3 inch strips. 2) Soak the potatoes in water for at least 30 minutes, then drain thoroughly and pat them dry with a paper towel. 3) Place the potatoes in a large bowl and add some oil to coat the potatoes evenly. 4) Preheat the Air Fryer to 350 degrees F (3–5minutes). Add the potatoes to cooking basket and cook for 20–30 minutes (350 degrees F) until golden and crisp.",
        "Name": "French Fries",
        "Notes": "Wait for 5 minutes before serving.",
        "Serving_Size": 3
}
Response: {"Id":"86516efe-4eae-11e9-b2af-98e0d98ade4d"}


# Fetching a Recipe
HTTP Method: GET
URL: http://127.0.0.1:5000/api/v1/resources/recipes?Id=86516efe-4eae-11e9-b2af-98e0d98ade4d&Name=Tempura&Category=Seafood 
Query Parameters: Id, Name, or Category


# Fetching All Recipes
HTTP Method: GET
URL: http://127.0.0.1:5000/api/v1/resources/recipes/all


# Editing a Recipe
HTTP Method: PATCH
URL: http://127.0.0.1:5000/api/v1/resources/recipes?Id=86516efe-4eae-11e9-b2af-98e0d98ade4d
Header: Content-Type: application/json
Query Parameter: Id
Body:
{
        "Category": "Sides",
        "Ingredients": "3 medium russet potatoes, 1 tablespoon olive oil",
        "Name": "French Fries",
        "Serving_Size": 3
}


# Deleting a Recipe
HTTP Method: DELETE
URL: http://127.0.0.1:5000/api/v1/resources/recipes?Id=86516efe-4eae-11e9-b2af-98e0d98ade4d
Query Parameter: Id





