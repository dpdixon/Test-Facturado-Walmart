import jaydebeapi
from config import DB_CONFIG

def get_connection():
    conn = jaydebeapi.connect(
        DB_CONFIG["driver"],
        DB_CONFIG["url"],
        [DB_CONFIG["user"], DB_CONFIG["password"]],
        DB_CONFIG["jars"]
    )
    return conn
