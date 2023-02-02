import sqlite3
import sys

# Connect to database file and return a connection object
def connect_db(db_file):
    conn = None
    try:
        # Create a connection to the database file
        conn = sqlite3.connect(db_file)
        return conn
    except sqlite3.Error as e:
        # Print any errors
        print(e)
    return conn

# Create a table with field definitions in connection
def create_table(conn, t_name, flds):
    # Construct the SQL statement to create table
    sql = f'CREATE TABLE IF NOT EXISTS {t_name} ({flds});'
    try:
        # Execute SQL statement to create table
        c = conn.cursor()
        c.execute(sql)
    except sqlite3.Error as e:
        # Print errors
        print(e)

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

# Add sample data to the database tables
def add_data(conn):
    # Define sample data for the tables
    data = {"meals": ("breakfast", "brunch", "lunch", "supper"),
        "ingredients": ("milk", "cacao", "strawberry", "blueberry", "blackberry", "sugar"),
        "measures": ("ml", "g", "l", "cup", "tbsp", "tsp", "dsp", "")}

    # Create a cursor to execute SQL statements
    cur = conn.cursor()
    cur.execute("SELECT * FROM meals")
    rows = cur.fetchall()
    if len(rows) == 0:
        for d in data:
            for v in data[d]:
                cur.execute(f"INSERT INTO {d} ({d[:-1]}_name) VALUES ('{v}');")

    conn.commit()

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
