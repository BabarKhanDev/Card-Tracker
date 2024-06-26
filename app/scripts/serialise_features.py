import json
import psycopg
from config import load_database_config

config = load_database_config("../config.ini")
out = {}

with psycopg.connect(**config) as conn:
    with conn.cursor() as cur:
        cur.execute("select id, features from sdk_cache.card")
        response = cur.fetchall()
        for row in response:
            if row[1] is not None:
                card_id, array = row[0], row[1].strip("[]").split(",")
                out[card_id] = array

with open("../../serialised_features.json", "w", encoding='utf-8') as f:
    json.dump(out, f, ensure_ascii=False)
