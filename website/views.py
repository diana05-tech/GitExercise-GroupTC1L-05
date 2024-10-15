import os
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from flask_login import login_required, current_user
import requests
from werkzeug.utils import secure_filename


views = Blueprint('views', __name__)
SPOONACULAR_API_KEY = 'c445af8099a14368a0547bd7a5b8c3e5'
SPOONACULAR_API_URL = 'https://api.spoonacular.com/recipes/complexSearch'
SPOONACULAR_RECIPE_INFO_URL = 'https://api.spoonacular.com/recipes/{id}/information'

# Configure upload folder
UPLOAD_FOLDER = 'static/uploads'  # Change to your desired upload path
ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'gif', 'mp4'}  # Add more allowed extensions as needed

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

recipes = {
    'Italian': {
        'Vegan': {
            'Breakfast': {
                'Less than 30 minutes': 'Vegan Italian Frittata',
                '30-60 minutes': 'Vegan Risotto',
                'More than 60 minutes': 'Vegan Lasagna'
            },
            'Lunch': {
                'Less than 30 minutes': 'Vegan Caprese Salad',
                '30-60 minutes': 'Vegan Pasta Primavera',
                'More than 60 minutes': 'Vegan Gnocchi'
            },
            'Dinner': {
                'Less than 30 minutes': 'Vegan Pizza',
                '30-60 minutes': 'Vegan Spaghetti Bolognese',
                'More than 60 minutes': 'Vegan Eggplant Parmesan'
            }
        },
        'Gluten-Free': {
            'Breakfast': {
                'Less than 30 minutes': 'Gluten-Free Italian Omelette',
                '30-60 minutes': 'Gluten-Free Quiche',
                'More than 60 minutes': 'Gluten-Free Frittata'
            },
            'Lunch': {
                'Less than 30 minutes': 'Gluten-Free Caprese Salad',
                '30-60 minutes': 'Gluten-Free Pasta with Pesto',
                'More than 60 minutes': 'Gluten-Free Risotto'
            },
            'Dinner': {
                'Less than 30 minutes': 'Gluten-Free Pizza',
                '30-60 minutes': 'Gluten-Free Spaghetti',
                'More than 60 minutes': 'Gluten-Free Lasagna'
            }
        },
        'Sugar-Free': {
            'Breakfast': {
                'Less than 30 minutes': 'Sugar-Free Italian Yogurt Parfait',
                '30-60 minutes': 'Sugar-Free Italian Frittata',
                'More than 60 minutes': 'Sugar-Free Tiramisu'
            },
            'Lunch': {
                'Less than 30 minutes': 'Sugar-Free Caprese Salad',
                '30-60 minutes': 'Sugar-Free Pesto Pasta',
                'More than 60 minutes': 'Sugar-Free Zucchini Lasagna'
            },
            'Dinner': {
                'Less than 30 minutes': 'Sugar-Free Spaghetti Aglio e Olio',
                '30-60 minutes': 'Sugar-Free Eggplant Parmesan',
                'More than 60 minutes': 'Sugar-Free Osso Buco'
            }
        },
        'Heart-Healthy': {
            'Breakfast': {
                'Less than 30 minutes': 'Heart-Healthy Italian Oatmeal',
                '30-60 minutes': 'Heart-Healthy Smoothie Bowl',
                'More than 60 minutes': 'Heart-Healthy Vegetable Frittata'
            },
            'Lunch': {
                'Less than 30 minutes': 'Heart-Healthy Italian Chickpea Salad',
                '30-60 minutes': 'Heart-Healthy Quinoa Salad',
                'More than 60 minutes': 'Heart-Healthy Stuffed Peppers'
            },
            'Dinner': {
                'Less than 30 minutes': 'Heart-Healthy Grilled Vegetables',
                '30-60 minutes': 'Heart-Healthy Baked Salmon with Herbs',
                'More than 60 minutes': 'Heart-Healthy Ratatouille'
            }
        },
        'None': {
            'Breakfast': {
                'Less than 30 minutes': 'Classic Italian Omelette',
                '30-60 minutes': 'Breakfast Burrata with Toast',
                'More than 60 minutes': 'Italian Croissants'
            },
            'Lunch': {
                'Less than 30 minutes': 'Caprese Salad',
                '30-60 minutes': 'Spaghetti Carbonara',
                'More than 60 minutes': 'Slow-cooked Lasagna'
            },
            'Dinner': {
                'Less than 30 minutes': 'Garlic Bread',
                '30-60 minutes': 'Italian Risotto',
                'More than 60 minutes': 'Pizza Margherita'
            }
        }
    },
    'Mexican': {
        'Vegan': {
            'Breakfast': {
                'Less than 30 minutes': 'Vegan Chilaquiles',
                '30-60 minutes': 'Vegan Breakfast Tacos',
                'More than 60 minutes': 'Vegan Huevos Rancheros'
            },
            'Lunch': {
                'Less than 30 minutes': 'Vegan Mexican Quinoa Salad',
                '30-60 minutes': 'Vegan Enchiladas',
                'More than 60 minutes': 'Vegan Tacos al Pastor'
            },
            'Dinner': {
                'Less than 30 minutes': 'Vegan Quesadillas',
                '30-60 minutes': 'Vegan Fajitas',
                'More than 60 minutes': 'Vegan Mexican Stuffed Peppers'
            }
        },
        'Gluten-Free': {
            'Breakfast': {
                'Less than 30 minutes': 'Gluten-Free Mexican Scramble',
                '30-60 minutes': 'Gluten-Free Chilaquiles',
                'More than 60 minutes': 'Gluten-Free Breakfast Burrito'
            },
            'Lunch': {
                'Less than 30 minutes': 'Gluten-Free Mexican Street Corn Salad',
                '30-60 minutes': 'Gluten-Free Chicken Tacos',
                'More than 60 minutes': 'Gluten-Free Beef Enchiladas'
            },
            'Dinner': {
                'Less than 30 minutes': 'Gluten-Free Tacos',
                '30-60 minutes': 'Gluten-Free Chicken Fajitas',
                'More than 60 minutes': 'Gluten-Free Pork Carnitas'
            }
        },
        'Sugar-Free': {
            'Breakfast': {
                'Less than 30 minutes': 'Sugar-Free Mexican Smoothie',
                '30-60 minutes': 'Sugar-Free Breakfast Burrito',
                'More than 60 minutes': 'Sugar-Free Vegan Tamales'
            },
            'Lunch': {
                'Less than 30 minutes': 'Sugar-Free Mexican Salad',
                '30-60 minutes': 'Sugar-Free Chicken Tacos',
                'More than 60 minutes': 'Sugar-Free Beef Enchiladas'
            },
            'Dinner': {
                'Less than 30 minutes': 'Sugar-Free Chicken Fajitas',
                '30-60 minutes': 'Sugar-Free Stuffed Peppers',
                'More than 60 minutes': 'Sugar-Free Pork Carnitas'
            }
        },
        'Heart-Healthy': {
            'Breakfast': {
                'Less than 30 minutes': 'Heart-Healthy Mexican Avocado Toast',
                '30-60 minutes': 'Heart-Healthy Breakfast Burrito',
                'More than 60 minutes': 'Heart-Healthy Breakfast Bowl'
            },
            'Lunch': {
                'Less than 30 minutes': 'Heart-Healthy Mexican Bean Salad',
                '30-60 minutes': 'Heart-Healthy Chicken Salad',
                'More than 60 minutes': 'Heart-Healthy Quinoa Tacos'
            },
            'Dinner': {
                'Less than 30 minutes': 'Heart-Healthy Grilled Chicken',
                '30-60 minutes': 'Heart-Healthy Veggie Fajitas',
                'More than 60 minutes': 'Heart-Healthy Baked Salmon with Salsa'
            }
        },
        'None': {
            'Breakfast': {
                'Less than 30 minutes': 'Breakfast Burrito',
                '30-60 minutes': 'Chilaquiles',
                'More than 60 minutes': 'Breakfast Quesadilla'
            },
            'Lunch': {
                'Less than 30 minutes': 'Tacos',
                '30-60 minutes': 'Burrito Bowl',
                'More than 60 minutes': 'Mole Enchiladas'
            },
            'Dinner': {
                'Less than 30 minutes': 'Quesadillas',
                '30-60 minutes': 'Chicken Tacos',
                'More than 60 minutes': 'Pork Tamales'
            }
        }
    },
    'Indian': {
        'Vegan': {
            'Breakfast': {
                'Less than 30 minutes': 'Vegan Chana Dal Pancakes',
                '30-60 minutes': 'Vegan Masala Dosa',
                'More than 60 minutes': 'Vegan Upma'
            },
            'Lunch': {
                'Less than 30 minutes': 'Vegan Chickpea Salad',
                '30-60 minutes': 'Vegan Vegetable Biryani',
                'More than 60 minutes': 'Vegan Butter Chicken'
            },
            'Dinner': {
                'Less than 30 minutes': 'Vegan Aloo Gobi',
                '30-60 minutes': 'Vegan Palak Paneer',
                'More than 60 minutes': 'Vegan Biryani'
            }
        },
        'Gluten-Free': {
            'Breakfast': {
                'Less than 30 minutes': 'Gluten-Free Idli',
                '30-60 minutes': 'Gluten-Free Poha',
                'More than 60 minutes': 'Gluten-Free Dosa'
            },
            'Lunch': {
                'Less than 30 minutes': 'Gluten-Free Chickpea Curry',
                '30-60 minutes': 'Gluten-Free Vegetable Korma',
                'More than 60 minutes': 'Gluten-Free Chicken Tikka Masala'
            },
            'Dinner': {
                'Less than 30 minutes': 'Gluten-Free Saag Aloo',
                '30-60 minutes': 'Gluten-Free Dal Makhani',
                'More than 60 minutes': 'Gluten-Free Biryani'
            }
        },
        'Sugar-Free': {
            'Breakfast': {
                'Less than 30 minutes': 'Sugar-Free Masala Chai',
                '30-60 minutes': 'Sugar-Free Oatmeal',
                'More than 60 minutes': 'Sugar-Free Indian Smoothie'
            },
            'Lunch': {
                'Less than 30 minutes': 'Sugar-Free Vegetable Salad',
                '30-60 minutes': 'Sugar-Free Palak Chole',
                'More than 60 minutes': 'Sugar-Free Chicken Curry'
            },
            'Dinner': {
                'Less than 30 minutes': 'Sugar-Free Aloo Gobi',
                '30-60 minutes': 'Sugar-Free Methi Thepla',
                'More than 60 minutes': 'Sugar-Free Tandoori Chicken'
            }
        },
        'Heart-Healthy': {
            'Breakfast': {
                'Less than 30 minutes': 'Heart-Healthy Poha',
                '30-60 minutes': 'Heart-Healthy Vegetable Upma',
                'More than 60 minutes': 'Heart-Healthy Idli'
            },
            'Lunch': {
                'Less than 30 minutes': 'Heart-Healthy Lentil Salad',
                '30-60 minutes': 'Heart-Healthy Chickpea Curry',
                'More than 60 minutes': 'Heart-Healthy Vegetable Biryani'
            },
            'Dinner': {
                'Less than 30 minutes': 'Heart-Healthy Saag Paneer',
                '30-60 minutes': 'Heart-Healthy Vegetable Stir-fry',
                'More than 60 minutes': 'Heart-Healthy Tandoori Salmon'
            }
        },
        'None': {
            'Breakfast': {
                'Less than 30 minutes': 'Paneer Paratha',
                '30-60 minutes': 'Aloo Paratha',
                'More than 60 minutes': 'Masala Dosa'
            },
            'Lunch': {
                'Less than 30 minutes': 'Butter Chicken',
                '30-60 minutes': 'Biryani',
                'More than 60 minutes': 'Paneer Tikka'
            },
            'Dinner': {
                'Less than 30 minutes': 'Dal Tadka',
                '30-60 minutes': 'Chole Bhature',
                'More than 60 minutes': 'Chicken Biryani'
            }
        }
    },
    'Chinese': {
        'Vegan': {
            'Breakfast': {
                'Less than 30 minutes': 'Vegan Congee',
                '30-60 minutes': 'Vegan Scallion Pancakes',
                'More than 60 minutes': 'Vegan Dumplings'
            },
            'Lunch': {
                'Less than 30 minutes': 'Vegan Fried Rice',
                '30-60 minutes': 'Vegan Kung Pao Tofu',
                'More than 60 minutes': 'Vegan Mapo Tofu'
            },
            'Dinner': {
                'Less than 30 minutes': 'Vegan Vegetable Stir-fry',
                '30-60 minutes': 'Vegan Sweet and Sour Tofu',
                'More than 60 minutes': 'Vegan Hot Pot'
            }
        },
        'Gluten-Free': {
            'Breakfast': {
                'Less than 30 minutes': 'Gluten-Free Egg Drop Soup',
                '30-60 minutes': 'Gluten-Free Fried Rice',
                'More than 60 minutes': 'Gluten-Free Chinese Pancakes'
            },
            'Lunch': {
                'Less than 30 minutes': 'Gluten-Free Chicken Stir-fry',
                '30-60 minutes': 'Gluten-Free Beef and Broccoli',
                'More than 60 minutes': 'Gluten-Free Sweet and Sour Chicken'
            },
            'Dinner': {
                'Less than 30 minutes': 'Gluten-Free Vegetable Lo Mein',
                '30-60 minutes': 'Gluten-Free Orange Chicken',
                'More than 60 minutes': 'Gluten-Free Kung Pao Chicken'
            }
        },
        'Sugar-Free': {
            'Breakfast': {
                'Less than 30 minutes': 'Sugar-Free Congee',
                '30-60 minutes': 'Sugar-Free Green Tea Smoothie',
                'More than 60 minutes': 'Sugar-Free Egg Foo Young'
            },
            'Lunch': {
                'Less than 30 minutes': 'Sugar-Free Vegetable Stir-fry',
                '30-60 minutes': 'Sugar-Free Chicken Lettuce Wraps',
                'More than 60 minutes': 'Sugar-Free Beef Chow Fun'
            },
            'Dinner': {
                'Less than 30 minutes': 'Sugar-Free Kung Pao Chicken',
                '30-60 minutes': 'Sugar-Free Sweet and Sour Tofu',
                'More than 60 minutes': 'Sugar-Free Hot and Sour Soup'
            }
        },
        'Heart-Healthy': {
            'Breakfast': {
                'Less than 30 minutes': 'Heart-Healthy Congee',
                '30-60 minutes': 'Heart-Healthy Egg Drop Soup',
                'More than 60 minutes': 'Heart-Healthy Stir-fried Greens'
            },
            'Lunch': {
                'Less than 30 minutes': 'Heart-Healthy Vegetable Salad',
                '30-60 minutes': 'Heart-Healthy Chicken and Broccoli',
                'More than 60 minutes': 'Heart-Healthy Tofu Stir-fry'
            },
            'Dinner': {
                'Less than 30 minutes': 'Heart-Healthy Vegetable Lo Mein',
                '30-60 minutes': 'Heart-Healthy Steamed Fish',
                'More than 60 minutes': 'Heart-Healthy Braised Tofu'
            }
        },
        'None': {
            'Breakfast': {
                'Less than 30 minutes': 'Dim Sum',
                '30-60 minutes': 'Egg Fried Rice',
                'More than 60 minutes': 'Pork Buns'
            },
            'Lunch': {
                'Less than 30 minutes': 'Sweet and Sour Pork',
                '30-60 minutes': 'Beef Noodle Soup',
                'More than 60 minutes': 'Peking Duck'
            },
            'Dinner': {
                'Less than 30 minutes': 'Kung Pao Chicken',
                '30-60 minutes': 'Mapo Tofu',
                'More than 60 minutes': 'Szechuan Hot Pot'
            }
        }
    },
    'Middle-Eastern': {
        'Vegan': {
            'Breakfast': {
                'Less than 30 minutes': 'Vegan Shakshuka',
                '30-60 minutes': 'Vegan Ful Medames',
                'More than 60 minutes': 'Vegan Fattoush'
            },
            'Lunch': {
                'Less than 30 minutes': 'Vegan Chickpea Salad',
                '30-60 minutes': 'Vegan Hummus Wraps',
                'More than 60 minutes': 'Vegan Kofta'
            },
            'Dinner': {
                'Less than 30 minutes': 'Vegan Falafel',
                '30-60 minutes': 'Vegan Stuffed Peppers',
                'More than 60 minutes': 'Vegan Moussaka'
            }
        },
        'Gluten-Free': {
            'Breakfast': {
                'Less than 30 minutes': 'Gluten-Free Labneh with Olive Oil',
                '30-60 minutes': 'Gluten-Free Shakshuka',
                'More than 60 minutes': 'Gluten-Free Fattoush'
            },
            'Lunch': {
                'Less than 30 minutes': 'Gluten-Free Tabouli',
                '30-60 minutes': 'Gluten-Free Chicken Shawarma',
                'More than 60 minutes': 'Gluten-Free Beef Kofta'
            },
            'Dinner': {
                'Less than 30 minutes': 'Gluten-Free Lamb Chops',
                '30-60 minutes': 'Gluten-Free Chicken Tagine',
                'More than 60 minutes': 'Gluten-Free Moroccan Stew'
            }
        },
        'Sugar-Free': {
            'Breakfast': {
                'Less than 30 minutes': 'Sugar-Free Middle Eastern Yogurt Bowl',
                '30-60 minutes': 'Sugar-Free Hummus',
                'More than 60 minutes': 'Sugar-Free Vegan Baklava'
            },
            'Lunch': {
                'Less than 30 minutes': 'Sugar-Free Mediterranean Salad',
                '30-60 minutes': 'Sugar-Free Chicken Shawarma',
                'More than 60 minutes': 'Sugar-Free Beef Kebabs'
            },
            'Dinner': {
                'Less than 30 minutes': 'Sugar-Free Chicken Tagine',
                '30-60 minutes': 'Sugar-Free Lamb Kofta',
                'More than 60 minutes': 'Sugar-Free Moussaka'
            }
        },
        'Heart-Healthy': {
            'Breakfast': {
                'Less than 30 minutes': 'Heart-Healthy Mediterranean Breakfast Bowl',
                '30-60 minutes': 'Heart-Healthy Labneh with Fresh Veggies',
                'More than 60 minutes': 'Heart-Healthy Vegetable Frittata'
            },
            'Lunch': {
                'Less than 30 minutes': 'Heart-Healthy Chickpea Salad',
                '30-60 minutes': 'Heart-Healthy Chicken Salad',
                'More than 60 minutes': 'Heart-Healthy Quinoa Tabbouleh'
            },
            'Dinner': {
                'Less than 30 minutes': 'Heart-Healthy Grilled Chicken',
                '30-60 minutes': 'Heart-Healthy Vegetable Couscous',
                'More than 60 minutes': 'Heart-Healthy Moroccan Stew'
            }
        },
        'None': {
            'Breakfast': {
                'Less than 30 minutes': 'Foul Medames',
                '30-60 minutes': 'Shakshuka',
                'More than 60 minutes': 'Simit'
            },
            'Lunch': {
                'Less than 30 minutes': 'Chicken Shawarma',
                '30-60 minutes': 'Beef Kebabs',
                'More than 60 minutes': 'Lamb Tagine'
            },
            'Dinner': {
                'Less than 30 minutes': 'Chicken Kofta',
                '30-60 minutes': 'Beef Moussaka',
                'More than 60 minutes': 'Stuffed Peppers'
            }
        }
    }
}

@views.route('/')
@login_required        
def home():
    return render_template("home.html",user=current_user)

@views.route('/profile')
@login_required
def profile():
    
    return render_template("profile.html", user=current_user)

@views.route('/index')
def index():
    return render_template('index.html')

@views.route('/result')
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

@views.route('/recipe/<int:recipe_id>')
def recipe_details(recipe_id):
    # Make a request to Spoonacular API for detailed recipe information
    response = requests.get(SPOONACULAR_RECIPE_INFO_URL.format(id=recipe_id), params={
        'apiKey': SPOONACULAR_API_KEY,
        'includeNutrition': True  # Ensure nutrition information is included
    })
    if response.status_code == 200:
        recipe = response.json()
        # Safeguard if nutrition info is missing
        if 'nutrition' not in recipe:
            recipe['nutrition'] = {'nutrients': [{'amount': 'N/A', 'unit': ''}] * 3}  # Default values
    else:
        recipe = None

    return render_template('recipe.html', recipe=recipe)

@views.route('/add-recipe', methods=['GET', 'POST'])
def add_recipe():
    if request.method == 'POST':
        title = request.form['title']
        ingredients = request.form['ingredients']
        instructions = request.form['instructions']
        
        image = request.files['image']
        video = request.files.get('video')  # Optional

        # Handle image upload
        image_filename = None
        if image and allowed_file(image.filename):
            image_filename = secure_filename(image.filename.replace(" ", "_"))  # Ensure a safe filename
            image_path = os.path.join(UPLOAD_FOLDER, image_filename)  # Adjust path
            os.makedirs(UPLOAD_FOLDER, exist_ok=True)  # Ensure the folder exists
            image.save(image_path)  # Save the image to the upload folder
        
         # Handle video upload if present
        video_filename = None
        if video and allowed_file(video.filename):
            video_filename = secure_filename(video.filename.replace(" ", "_"))  # Ensure a safe filename
            video_path = os.path.join(UPLOAD_FOLDER, video_filename)  # Adjust path
            os.makedirs(UPLOAD_FOLDER, exist_ok=True)  # Ensure the folder exists
            video.save(video_path)  # Save the video to the upload folder
# Initialize uploaded_recipes if not in session
        uploaded_recipes = session.get('uploaded_recipes', [])
        recipe_id = len(uploaded_recipes) + 1


        # Store the uploaded recipe in the session (or database)
        uploaded_recipes.append({
            'id': recipe_id,
            'title': title,
            'ingredients': ingredients,
            'instructions': instructions,
            'image': image_filename,
            'video': video_filename if video else None  # Optional field
        })
        session['uploaded_recipes'] = uploaded_recipes
          # Redirect to a confirmation page or the user's profile
        return redirect(url_for('views.view_own_recipes'))  # or another page

    return render_template('add_recipe.html')  # For GET requests
@views.route('/my-recipes')
def view_own_recipes():
    uploaded_recipes = session.get('uploaded_recipes', [])
    return render_template('view_own_recipes.html', recipes=uploaded_recipes)

# New route to view a single recipe
@views.route('/view-recipe/<int:recipe_id>')
def view_recipe(recipe_id):
    uploaded_recipes = session.get('uploaded_recipes', [])
    recipe = next((r for r in uploaded_recipes if r['id'] == recipe_id), None)
    
    if recipe:
        return render_template('view_own_recipe.html', recipe=recipe, recipe_id=recipe_id)
    else:
        return "Recipe not found", 404

# New route to delete a recipe
@views.route('/delete-recipe/<int:recipe_id>', methods=['POST'])
def delete_recipe(recipe_id):
    uploaded_recipes = session.get('uploaded_recipes', [])
    uploaded_recipes = [r for r in uploaded_recipes if r['id'] != recipe_id]
    
    session['uploaded_recipes'] = uploaded_recipes
    return redirect(url_for('views.view_own_recipes'))
    
@views.route('/add-to-favorites/<int:recipe_id>', methods=['POST'])
def add_to_favorites(recipe_id):
    # Retrieve recipe information from Spoonacular API
    response = requests.get(SPOONACULAR_RECIPE_INFO_URL.format(id=recipe_id), params={
        'apiKey': SPOONACULAR_API_KEY
    })
    if response.status_code == 200:
        recipe = response.json()

        # Check if the session has a 'favorites' key
        if 'favorites' not in session:
            session['favorites'] = []

        # Add the recipe to the favorites list if not already present
        favorites = session['favorites']
        if recipe_id not in [r['id'] for r in favorites]:
            favorites.append({
                'id': recipe['id'],
                'title': recipe['title'],
                'image': recipe['image']
            })
            session['favorites'] = favorites  # Update session with new list

    return redirect(url_for('views.favs_recipes'))

@views.route('/remove-favorite/<int:recipe_id>', methods=['POST'])
def remove_favorite(recipe_id):
    # Retrieve the current favorites from the session
    favorites = session.get('favorites', [])

    # Remove the recipe from the list if it exists
    favorites = [recipe for recipe in favorites if recipe['id'] != recipe_id]
    
    # Update the session with the new list
    session['favorites'] = favorites
    
    # Redirect back to the favorites page
    return redirect(url_for('views.favs_recipes'))


@views.route('/favs-recipes')
def favs_recipes():
    # Retrieve the favorites from the session
    favorites = session.get('favorites', [])
    return render_template('favs_recipes.html', favorites=favorites)

@views.route('/scale-recipe/<int:recipe_id>', methods=['POST'])
def scale_recipe(recipe_id):
    scaling_factor = int(request.form.get('scaling_factor', 1))
    response = requests.get(SPOONACULAR_RECIPE_INFO_URL.format(id=recipe_id), params={
        'apiKey': SPOONACULAR_API_KEY,
        'includeNutrition': True
    })

    if response.status_code == 200:
        recipe = response.json()
        scaled_ingredients = []
        for ingredient in recipe.get('extendedIngredients', []):
            scaled_amount = ingredient['amount'] * scaling_factor
            scaled_ingredients.append({
                'name': ingredient['name'],
                'amount': scaled_amount,
                'unit': ingredient['unit']
            })

        recipe['scaled_ingredients'] = scaled_ingredients
    else:
        recipe = None

    return render_template('recipe.html', recipe=recipe, scaling_factor=scaling_factor)


@views.route('/personalized-recipe', methods=['GET', 'POST'])
def personalized_recipe():
    if request.method == 'POST':
        cuisine = request.form.get('cuisine')
        diet = request.form.get('diet')
        meal_type = request.form.get('meal_type')
        prep_time = request.form.get('prep_time')

        # Fetch the recipe from the dictionary
        recipe = recipes.get(cuisine, {}).get(diet, {}).get(meal_type, {}).get(prep_time, 'No recipe found for your selection.')

        return render_template('personalized_recipe.html', recipe=recipe, cuisine=cuisine, diet=diet, meal_type=meal_type, prep_time=prep_time)
    
    return render_template('personalized_recipe.html',recipe =None)