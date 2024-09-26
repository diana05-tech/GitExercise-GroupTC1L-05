import webbrowser
from flask import Flask, render_template, request
import requests

app = Flask(__name__)

# Spoonacular API key and endpoint
SPOONACULAR_API_KEY = 'c445af8099a14368a0547bd7a5b8c3e5'
SPOONACULAR_API_URL = 'https://api.spoonacular.com/recipes/complexSearch'
SPOONACULAR_RECIPE_INFO_URL = 'https://api.spoonacular.com/recipes/{id}/information'

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/result')
def result():
    query = request.args.get('query', '')

    # Make a request to Spoonacular API
    response = requests.get(SPOONACULAR_API_URL, params={
        'apiKey': SPOONACULAR_API_KEY,
        'query': query,
        'number': 10,  # Number of results to return
        'addRecipeInformation': True  # Include additional information like sourceUrl
    })

    # Debugging: Print the status code and response
    print(f"Status Code: {response.status_code}")
    print(f"Response JSON: {response.json()}")

    # Check for request success
    if response.status_code == 200:
        data = response.json()
        recipes = data.get('results', [])
    else:
        recipes = []

    return render_template('result.html', query=query, recipes=recipes)

@app.route('/recipe/<int:recipe_id>')
def recipe_details(recipe_id):
    # Make a request to Spoonacular API for detailed recipe information
    response = requests.get(SPOONACULAR_RECIPE_INFO_URL.format(id=recipe_id), params={
        'apiKey': SPOONACULAR_API_KEY
    })

    if response.status_code == 200:
        recipe = response.json()
    else:
        recipe = None

    return render_template('recipe.html', recipe=recipe)

if __name__ == '__main__':
    webbrowser.open('http://127.0.0.1:5000/')
    app.run(debug=True)
