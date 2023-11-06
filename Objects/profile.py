import sys
import traceback
from datetime import date
from os import path, mkdir, getlogin
import sqlite3



def scrub(table_name):
    return ''.join(char for char in table_name if char.isalnum())


class card:
    # Holds information regarding a single card in a deck
    def __init__(self, cardID, question, answer, score, date_played, repetitions, date_due):

        self.cardID = cardID
        self.question = question
        self.answer = answer
        self.score = score
        self.date_played = date_played
        self.repetitions = repetitions
        self.date_due = date_due


class deck:
    # Holds all cards in the deck.
    # There is possibly some functionality that can be added to this class beyond holding a list, so creating it now
    def __init__(self, cards):
        self.cards = cards


class Profile:
    # Interacts with the SQLite database
    def __init__(self, name, home_path):
        self.name = name
        self.home_path = home_path
        if not path.exists(self.home_path):
            mkdir(self.home_path)
        self.con = sqlite3.connect(path.join(home_path, "Database.db"))
        self.cur = self.con.cursor()

    def update_card(self, drawn_card, deck_title):

        sql = "UPDATE " + scrub(deck_title) + " SET score=?, date_completed=?, repetitions=?, date_due=? WHERE id=?"

        try:
            res = self.cur.execute(sql, (drawn_card.score, drawn_card.date_played, drawn_card.repetitions, drawn_card.date_due, drawn_card.cardID))
            self.con.commit()
        except sqlite3.Error as er:
            print('SQLite error: %s' % (' '.join(er.args)))
            print("Exception class is: ", er.__class__)
            print('SQLite traceback: ')
            exc_type, exc_value, exc_tb = sys.exc_info()
            print(traceback.format_exception(exc_type, exc_value, exc_tb))
        return res


    def add_deck(self, deck_title):

        sql = "SELECT name FROM sqlite_master WHERE type='table' AND name=" + "'" + scrub(deck_title) + "'"

        res = self.run_sql(sql)

        if str(res.fetchone()) == "None":
            sql_query = "CREATE TABLE " + scrub(deck_title) + "(id integer PRIMARY KEY, question string, answer string, score integer, date_completed datetime, repetitions integer, date_due datetime)"  # Apparently table names cant be parameterised, so scrub the input to prevent sql injections
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
        sql = "INSERT INTO " + scrub(deck_name) + "(question,answer,score,date_completed,repetitions,date_due) VALUES(?,?,?,?,?,?)"   # Needs parameters passing so running in this function rather than the general SQL run one
        try:
            res = self.cur.execute(sql, (question, answer, 2.5, date.today(), 0, date.today()))
            self.con.commit()
        except sqlite3.Error as er:
            print('SQLite error: %s' % (' '.join(er.args)))
            print("Exception class is: ", er.__class__)
            print('SQLite traceback: ')
            exc_type, exc_value, exc_tb = sys.exc_info()
            print(traceback.format_exception(exc_type, exc_value, exc_tb))
        return res

    def remove_card(self, deck_name, cardID):
        sql = "DELETE FROM " + scrub(deck_name) + " WHERE id = " + str(cardID)
        self.run_sql(sql)
        self.con.commit()

    def get_deck(self, deck_name):
        sql = "SELECT * FROM " + scrub(deck_name)
        res = self.run_sql(sql)
        cards = []
        for result in res.fetchall():
            cards.append(card(result[0], result[1], result[2], result[3], result[4], result[5], result[6]))
        return cards



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
