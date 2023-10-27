import sys
import traceback
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

        sql = "SELECT name FROM sqlite_master WHERE type='table' AND name=" + "'" + scrub(deck_title) + "'"

        res = self.run_sql(sql)

        if str(res.fetchone()) == "None":
            sql_query = "CREATE TABLE " + scrub(deck_title) + "(id integer PRIMARY KEY, question string, answer string, score integer)"  # Apparently table names cant be parameterised, so scrub the input to prevent sql injections
            self.run_sql(sql_query)
            return deck_title + " added"
        else:
            return "Error - " + deck_title + " already exists"

    def remove_deck(self, deck_title):

        sql = "SELECT name FROM sqlite_master WHERE type='table' AND name=" + "'" + scrub(deck_title) + "'"

        res = self.run_sql(sql)

        if not str(res.fetchone()) == "None":
            sql_query = "DROP TABLE " + scrub(deck_title)             # Apparently table names cant be parameterised, so scrub the input to prevent sql injections.
            self.run_sql(sql_query)                                       # User input is selection from menu, but better safe than sorry
            return deck_title + " removed"
        else:
            return "Error - You shouldn't see this"

    def get_deck_names(self):
        sql = "SELECT name FROM sqlite_master WHERE type='table'"
        res = self.run_sql(sql)
        return [x[0] for x in res.fetchall()]

    def add_card(self, deck_name, question, answer):
        sql = "INSERT INTO " + scrub(deck_name) + "(question,answer,score) VALUES(?,?,?)"   # Needs parameters passing so running in this function rather than the general SQL run one
        try:
            res = self.cur.execute(sql, (question, answer, "PLACEHOLDER"))
            self.con.commit()
        except sqlite3.Error as er:
            print('SQLite error: %s' % (' '.join(er.args)))
            print("Exception class is: ", er.__class__)
            print('SQLite traceback: ')
            exc_type, exc_value, exc_tb = sys.exc_info()
            print(traceback.format_exception(exc_type, exc_value, exc_tb))
        return res


    def run_sql(self, sql):
        try:
            res = self.cur.execute(sql)
        except sqlite3.Error as er:
            res = "SQL ERROR"
            print('SQLite error: %s' % (' '.join(er.args)))
            print("Exception class is: ", er.__class__)
            print('SQLite traceback: ')
            exc_type, exc_value, exc_tb = sys.exc_info()
            print(traceback.format_exception(exc_type, exc_value, exc_tb))
        return res

    def close_db(self):
        self.cur.close()
        self.con.close()
