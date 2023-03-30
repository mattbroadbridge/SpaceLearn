from os import path, mkdir, getlogin
import sqlite3


def scrub(table_name):
    return ''.join(char for char in table_name if char.isalnum())


class Profile:
    def __init__(self, name, home_path):
        self.name = name
        self.home_path = home_path
        if not path.exists(self.home_path):
            mkdir(self.home_path)
        self.con = sqlite3.connect(path.join(home_path, "Database.db"))
        self.cur = self.con.cursor()

    def add_deck(self, deck_title):

        res = self.cur.execute("SELECT ? FROM sqlite_master WHERE type='table' AND name=?", (deck_title, deck_title))

        if str(res.fetchone()) == "None":
            sql_query = "CREATE TABLE " + scrub(deck_title) + "(card, score)"  # Apparently table names cant be parameterised, so scrub the input to prevent sql injections
            self.cur.execute(sql_query)
            return deck_title + " added"
        else:
            return "Error - " + deck_title + " already exists"

    def remove_deck(self, deck_title):

        res = self.cur.execute("SELECT ? FROM sqlite_master WHERE name=?", (deck_title, deck_title))

        if not str(res.fetchone()) == "None":
            sql_query = "DROP TABLE " + scrub(deck_title)             # Apparently table names cant be parameterised, so scrub the input to prevent sql injections.
            self.cur.execute(sql_query)                                        # User input is selection from menu, but better safe than sorry
            return deck_title + " removed"
        else:
            return "Error - You shouldn't see this"


    def close_db(self):
        self.cur.close()
        self.con.close()

