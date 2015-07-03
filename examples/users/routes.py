import bottle

app = bottle.Bottle()

from cassandra.cqlengine.connection import execute


def index():
    execute(
        """
        INSERT INTO mykeyspa.users (name, credits, user_id)
        VALUES (%s, %s, %s)
        """,
        ("John O'Reilly", 42, 123)
    )

    return 'Hello Bunny my precious!!'
