from common.config import load_database_config
from common.database import connect

# Set up database
config = load_database_config("../config.ini")
conn = connect(config)
cursor = conn.cursor()
with open("../sql/init.sql", "r") as file:
    sql_commands = file.read()

sql_commands = sql_commands.split(";")
for command in sql_commands:
    if command == "":
        continue
    try:
        cursor.execute(command)
    except Exception as e:
        print("Error executing command:", e)

# TODO create feature vectors for each card and store them in our database

conn.commit()
cursor.close()
conn.close()
