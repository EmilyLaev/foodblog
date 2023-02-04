import sqlite3
import sys
import argparse


data = {"meals": ("breakfast", "brunch", "lunch", "supper"),
        "ingredients": ("milk", "cacao", "strawberry", "blueberry", "blackberry", "sugar"),
        "measures": ("ml", "g", "l", "cup", "tbsp", "tsp", "dsp", "")}


def create_tables(database):
    conn = sqlite3.connect(database)
    food = conn.cursor()
    food.execute("PRAGMA foreign_keys = ON;")
    conn.commit()
    food.execute(f"CREATE TABLE IF NOT EXISTS ingredients(ingredient_id INTEGER PRIMARY KEY, ingredient_name TEXT NOT NULL UNIQUE);")
    food.execute(f"CREATE TABLE IF NOT EXISTS measures(measure_id INTEGER PRIMARY KEY, measure_name TEXT UNIQUE);")
    food.execute(f"CREATE TABLE IF NOT EXISTS meals(meal_id INTEGER PRIMARY KEY, meal_name TEXT NOT NULL UNIQUE);")
    food.execute(f"CREATE TABLE IF NOT EXISTS recipes(recipe_id INTEGER PRIMARY KEY, recipe_name TEXT NOT NULL, recipe_description TEXT);")
    food.execute(f"CREATE TABLE IF NOT EXISTS serve(serve_id INTEGER PRIMARY KEY, recipe_id INTEGER NOT NULL, meal_id INTEGER NOT NULL, "
                   f"FOREIGN KEY(recipe_id) REFERENCES recipes(recipe_id), FOREIGN KEY(meal_id) REFERENCES meals(meal_id));")
    food.execute(f"CREATE TABLE IF NOT EXISTS quantity(quantity_id INTEGER PRIMARY KEY, recipe_id INTEGER NOT NULL, quantity INTEGER NOT NULL, measure_id INTEGER NOT NULL, ingredient_id INTEGER NOT NULL, "
                   f"FOREIGN KEY(recipe_id) REFERENCES recipes(recipe_id), FOREIGN KEY(measure_id) REFERENCES measures(measure_id), FOREIGN KEY(ingredient_id) REFERENCES ingredients(ingredient_id));")

    conn.commit()
    for table in data:
        for item in data[table]:
            try:
                food.execute(f"INSERT INTO {table}({table[:-1]}_name) VALUES('{item}')")
            except sqlite3.IntegrityError:
                print(f"{item} integrity")

                pass
    conn.commit()
    conn.close()

        
def feeding_database(database):
    conn = sqlite3.connect(database)
    food = conn.cursor()
    while True:
        print("Pass the empty recipe name to exit.")
        name = input("Recipe name: ")
        if name == "":
            return
        description = input('Recipe description: ')
        recipe_id = food.execute(f"INSERT INTO recipes(recipe_name, recipe_description) VALUES('{name}', '{description}')").lastrowid
        conn.commit()
        meals_data = food.execute(f"SELECT * FROM meals")
        print(" ".join([str(measure[0]) + ") " + measure[1] + " " for measure in meals_data.fetchall()]))
        meals = input("Enter proposed meals separated by a space: ").split(" ")
        for meal in meals:
            food.execute(f"INSERT INTO serve(meal_id, recipe_id) VALUES('{meal}', '{recipe_id}')")
        conn.commit()
        while True:
            ingredient = input("Input quantity of ingredient <press enter to stop>: ").split(" ")
            if ingredient[0] == "":
                conn.commit()
                break
            elif any([len(ingredient) < 2, len(ingredient) > 3]):
                print("Wrong form! Should be [quantity <measure> ingredient]!")
            else:
                if len(ingredient) == 2:
                    i_measure = food.execute(f"SELECT measure_id FROM measures WHERE measure_name = ''").fetchall()
                    i_ingredient = food.execute(f"SELECT ingredient_id FROM ingredients WHERE ingredient_name LIKE '%{ingredient[1]}%'").fetchall()
                else:
                    i_measure = food.execute(f"SELECT measure_id FROM measures WHERE measure_name LIKE '{ingredient[1]}%'").fetchall()
                    i_ingredient = food.execute(f"SELECT ingredient_id FROM ingredients WHERE ingredient_name LIKE '%{ingredient[2]}%'").fetchall()
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
 

# Create the database and return a connection object
def create_db(db_name):
    conn = connect_db(db_name)
    flds = '''  measure_id INTEGER PRIMARY KEY,
                measure_name TEXT UNIQUE'''
    # Create measures table
    create_table(conn, 'measures', flds)
    flds = '''  ingredient_id INTEGER PRIMARY KEY,
                ingredient_name TEXT NOT NULL UNIQUE'''
    # Create ingredients table
    create_table(conn, 'ingredients', flds)
    # Define fields for ingredients
    flds = '''  meal_id INTEGER PRIMARY KEY,
                meal_name TEXT NOT NULL UNIQUE'''
    # Create meals table
    create_table(conn, 'meals', flds)
    return conn


def print_query(database, ingredients, meals):
    conn = sqlite3.connect(database)
    food = conn.cursor()
    quantity, quantity_out, q_o = [], [], []
    for ingredient in ingredients.split(","):
        quantity.append(set(number[0] for number in food.execute(f"SELECT recipe_id FROM quantity where ingredient_id in (SELECT ingredient_id FROM ingredients WHERE ingredient_name = '{ingredient}')").fetchall()))
    quantity = set.intersection(*quantity)
    for meal in meals.split(","):
        quantity_out.append(set(number[0] for number in food.execute(f"SELECT recipe_id FROM serve WHERE meal_id in (SELECT meal_id FROM meals WHERE meal_name = '{meal}')").fetchall()))
    if len(meals.split(",")) == 1:
        q_o = set.intersection(*quantity_out)
    else:
        for q_all in [*quantity_out]:
            for q in q_all:
                if q in quantity:
                    q_o.append(q)

    recipes = ", ".join([food.execute(f"SELECT recipe_name FROM recipes WHERE recipe_id = '{i_d}'").fetchone()[0] for i_d in set.intersection(quantity, q_o)])

    print(f"Recipes selected for you: {recipes}" if recipes else "There are no such recipes in the database.")
    pass


parser = argparse.ArgumentParser()
parser.add_argument('File')
parser.add_argument('--ingredients')
parser.add_argument('--meals')
args = parser.parse_args()

if not args.ingredients:
    create_tables(sys.argv[1])
    feeding_database(sys.argv[1])
else:
    print_query(args.File, args.ingredients, args.meals)


# Main function to create the database and add sample data
def main():
    args = sys.argv
    if len(args) != 2:
        print('Specify the DB name as an argument')
        exit()

    db_name = args[1]
    conn = create_db(db_name)
    add_data(conn)
    print('db_name =', db_name)

if __name__ == "__main__":
    main()
