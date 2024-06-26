from pokemontcgsdk import Set
from pokemontcgsdk import RestClient
import psycopg
from pgvector.psycopg import register_vector
from tqdm import tqdm

from scripts.config import load_database_config
from scripts.database import cache_set
from scripts.config import load_tcg_api_key
from scripts.vision import create_model_and_preprocess


def setup_database():
    config = load_database_config("../config.ini")
    with psycopg.connect(**config) as conn:
        register_vector(conn)

        with conn.cursor() as cur:

            cur.execute('CREATE EXTENSION IF NOT EXISTS vector')
            print("Successfully registered vector extension")

            # Database initialisation
            with open("../sql/init.sql", "r") as file:
                sql_commands = file.read()

            sql_commands = sql_commands.split(";")
            for command in sql_commands:
                if command == "":
                    continue
                try:
                    cur.execute(command)
                except Exception as e:
                    print("Error executing command:", e)
            print("Successfully Configured Database")

            # Cache all cards
            tcg_api_key = load_tcg_api_key("../config.ini")
            RestClient.configure(tcg_api_key)
            model, preprocess, device = create_model_and_preprocess()
            for s in tqdm(Set.all()):
                cache_set(conn, cur, s, model, preprocess, device)
            print("Successfully Cached All Sets")

        conn.commit()


if "__main__" == __name__:
    setup_database()
