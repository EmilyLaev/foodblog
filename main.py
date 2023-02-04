import sqlite3
import sys
import argparse

# Define dictionaries with initial data for tables
data = {"meals": ("breakfast", "brunch", "lunch", "supper"),
        "ingredients": ("milk", "cacao", "strawberry", "blueberry", "blackberry", "sugar"),
        "measures": ("ml", "g", "l", "cup", "tbsp", "tsp", "dsp", "")}

# Function to create tables in SQLite database
def create_tables(database):
    # Connect to the database and create a cursor object
    conn = sqlite3.connect(database)
    food = conn.cursor()

    # Enable foreign keys for the database
    food.execute("PRAGMA foreign_keys = ON;")
    conn.commit()
        
    # Create tables for ingredients, measures, meals, recipes, serve, and quantity
    food.execute(f"CREATE TABLE IF NOT EXISTS ingredients(ingredient_id INTEGER PRIMARY KEY, ingredient_name TEXT NOT NULL UNIQUE);")
    food.execute(f"CREATE TABLE IF NOT EXISTS measures(measure_id INTEGER PRIMARY KEY, measure_name TEXT UNIQUE);")
    food.execute(f"CREATE TABLE IF NOT EXISTS meals(meal_id INTEGER PRIMARY KEY, meal_name TEXT NOT NULL UNIQUE);")
    food.execute(f"CREATE TABLE IF NOT EXISTS recipes(recipe_id INTEGER PRIMARY KEY, recipe_name TEXT NOT NULL, recipe_description TEXT);")
    food.execute(f"CREATE TABLE IF NOT EXISTS serve(serve_id INTEGER PRIMARY KEY, recipe_id INTEGER NOT NULL, meal_id INTEGER NOT NULL, "
                   f"FOREIGN KEY(recipe_id) REFERENCES recipes(recipe_id), FOREIGN KEY(meal_id) REFERENCES meals(meal_id));")
    food.execute(f"CREATE TABLE IF NOT EXISTS quantity(quantity_id INTEGER PRIMARY KEY, recipe_id INTEGER NOT NULL, quantity INTEGER NOT NULL, measure_id INTEGER NOT NULL, ingredient_id INTEGER NOT NULL, "
                   f"FOREIGN KEY(recipe_id) REFERENCES recipes(recipe_id), FOREIGN KEY(measure_id) REFERENCES measures(measure_id), FOREIGN KEY(ingredient_id) REFERENCES ingredients(ingredient_id));")

    # Commit changes to the database
    conn.commit()

    # Insert initial data for tables into the database
    for table in data:
        for item in data[table]:
            try:
                food.execute(f"INSERT INTO {table}({table[:-1]}_name) VALUES('{item}')")
            except sqlite3.IntegrityError:
                print(f"{item} integrity")
                # Pass if an integrity error occurs
                pass
    # Commit changes to the database and close the connection
    conn.commit()
    conn.close()

        
# Function to add data to the database
# Connect to the database and create cursor for SQL commands
def feeding_database(database):
    conn = sqlite3.connect(database)
    food = conn.cursor()
        
    # Continuously prompt for recipe input
    while True:
        print("Pass the empty recipe name to exit.")
        name = input("Recipe name: ")
        
        # If recipe name is empty, return from the function
        if name == "":
            return
        description = input('Recipe description: ')
        # Insert the recipe into the `recipes` table
        recipe_id = food.execute(f"INSERT INTO recipes(recipe_name, recipe_description) VALUES('{name}', '{description}')").lastrowid
        conn.commit()
        meals_data = food.execute(f"SELECT * FROM meals")
        print(" ".join([str(measure[0]) + ") " + measure[1] + " " for measure in meals_data.fetchall()]))
        meals = input("Enter proposed meals separated by a space: ").split(" ")
        
        # Insert the meal-recipe relation into the `serve` table
        for meal in meals:
            food.execute(f"INSERT INTO serve(meal_id, recipe_id) VALUES('{meal}', '{recipe_id}')")
        conn.commit()
        
        # Continuously prompt for ingredient input
        while True:
            ingredient = input("Input quantity of ingredient <press enter to stop>: ").split(" ")
            # If ingredient is empty, stop the ingredient input loop and commit the changes
            if ingredient[0] == "":
                conn.commit()
                break
            # Check if the input is in the correct format
            elif any([len(ingredient) < 2, len(ingredient) > 3]):
                print("Wrong form! Should be [quantity <measure> ingredient]!")
            else:
                # Retrieve the measure and ingredient IDs
                if len(ingredient) == 2:
                    i_measure = food.execute(f"SELECT measure_id FROM measures WHERE measure_name = ''").fetchall()
                    i_ingredient = food.execute(f"SELECT ingredient_id FROM ingredients WHERE ingredient_name LIKE '%{ingredient[1]}%'").fetchall()
                else:
                    i_measure = food.execute(f"SELECT measure_id FROM measures WHERE measure_name LIKE '{ingredient[1]}%'").fetchall()
                    i_ingredient = food.execute(f"SELECT ingredient_id FROM ingredients WHERE ingredient_name LIKE '%{ingredient[2]}%'").fetchall()
                # Check if the measure and ingredient IDs are conclusive
                if any([len(i_measure) !=1, len(i_ingredient) != 1]):
                    if len(i_measure) == 0:
                        print("There is no such a measure!")
                    elif len(i_measure) !=1:
                        print("The measure is not conclusive!")
                    if len(i_ingredient) == 0:
                        print("There is no such a ingredient!")
                    elif len(i_ingredient) !=1:
                        print("The ingredient is not conclusive!")
                else:
                    food.execute(f"INSERT INTO quantity(recipe_id, quantity, measure_id, ingredient_id) VALUES('{recipe_id}', '{ingredient[0]}', '{i_measure[0][0]}','{i_ingredient[0][0]}')")
 

def print_query(database, ingredients, meals):
    # Connects to the SQLite database
    conn = sqlite3.connect(database)
    food = conn.cursor()
    quantity, quantity_out, q_o = [], [], []
     
    # Loop through the ingredients to retrieve the recipe_id from the 'quantity' table 
    # where the ingredient_id matches the given ingredient name
    for ingredient in ingredients.split(","):
        quantity.append(set(number[0] for number in food.execute(f"SELECT recipe_id FROM quantity where ingredient_id in (SELECT ingredient_id FROM ingredients WHERE ingredient_name = '{ingredient}')").fetchall()))
    quantity = set.intersection(*quantity)

    # Loop through the meals to retrieve the recipe_id from the 'serve' table 
    # where the meal_id matches the given meal name
    for meal in meals.split(","):
        quantity_out.append(set(number[0] for number in food.execute(f"SELECT recipe_id FROM serve WHERE meal_id in (SELECT meal_id FROM meals WHERE meal_name = '{meal}')").fetchall()))
    # If there is only one meal, find the intersection of the sets of recipe_id
    if len(meals.split(",")) == 1:
        q_o = set.intersection(*quantity_out)
    else:
        for q_all in [*quantity_out]:
            for q in q_all:
                if q in quantity:
                    q_o.append(q)

    # Get the recipe_name from the 'recipes' table for the recipe_id found from the previous steps
    recipes = ", ".join([food.execute(f"SELECT recipe_name FROM recipes WHERE recipe_id = '{i_d}'").fetchone()[0] for i_d in set.intersection(quantity, q_o)])

    # Prints the recipe names found or a message indicating that no such recipes exist in the database
    print(f"Recipes selected for you: {recipes}" if recipes else "There are no such recipes in the database.")
    pass

# Parser statements to parse command line arguments
parser = argparse.ArgumentParser()
parser.add_argument('File')
parser.add_argument('--ingredients')
parser.add_argument('--meals')
args = parser.parse_args()

# Calls the other functions to run depending on ingredients given
if not args.ingredients:
    create_tables(sys.argv[1])
    feeding_database(sys.argv[1])
else:
    print_query(args.File, args.ingredients, args.meals)
