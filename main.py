import sqlite3
import sys

def connect_db(db_file):
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except sqlite3.Error as e:
        print(e)
    return conn

def create_table(conn, t_name, flds):
    sql = f'CREATE TABLE IF NOT EXISTS {t_name} ({flds});'
    try:
        c = conn.cursor()
        c.execute(sql)
    except sqlite3.Error as e:
        print(e)

def create_db(db_name):
    conn = connect_db(db_name)
    flds = '''  measure_id INTEGER PRIMARY KEY,
                measure_name TEXT UNIQUE'''
    create_table(conn, 'measures', flds)
    flds = '''  ingredient_id INTEGER PRIMARY KEY,
                ingredient_name TEXT NOT NULL UNIQUE'''
    create_table(conn, 'ingredients', flds)
    flds = '''  meal_id INTEGER PRIMARY KEY,
                meal_name TEXT NOT NULL UNIQUE'''
    create_table(conn, 'meals', flds)
    return conn

def add_data(conn):
    data = {"meals": ("breakfast", "brunch", "lunch", "supper"),
        "ingredients": ("milk", "cacao", "strawberry", "blueberry", "blackberry", "sugar"),
        "measures": ("ml", "g", "l", "cup", "tbsp", "tsp", "dsp", "")}

    cur = conn.cursor()
    cur.execute("SELECT * FROM meals")
    rows = cur.fetchall()
    if len(rows) == 0:
        for d in data:
            for v in data[d]:
                cur.execute(f"INSERT INTO {d} ({d[:-1]}_name) VALUES ('{v}');")

    conn.commit()

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