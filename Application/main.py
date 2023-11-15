import math
import os.path
import random
import time
from datetime import datetime, timedelta, date

from PyQt5 import QtCore, QtWidgets
import sys
from os import path, getlogin

from PyQt5.QtWidgets import QMessageBox

import Windows.addDeck
import Windows.viewDeck
import Windows.editDeck
import Windows.playDeck
import Windows.settings
from Objects.profile import Profile


def gen_score(old_score, quality_score):
    # Generates an EF (Ease Factor) for a card, based on SuperMemos SM-2 algorithm
    res = old_score + (0.1 - (5 - quality_score) * (0.08 + (5 - quality_score) * 0.02))
    if res > 2.5:
        return 2.5
    elif res < 1.1:
        return 1.1
    else:
        return res


class PlayDeckWindow(QtWidgets.QDialog, Windows.playDeck.Ui_Dialog):
    # This class is passed a number of cards, shuffles them, and displays them one at a time prompting an answer.
    # It is also passed a connection to the SQLite database.
    def __init__(self, profile, deck_name, cards, repetitions_flag, settings, parent=None):
        super().__init__(parent)

        self.spelling_error = 0  # Number of errors the user makes per card
        self.allowed_errors = int(settings.value(
            "allowed_errors"))  # Max number of errors that can be made per card whilst maintaining perfect score
        self.error_limit = int(settings.value("error_limit"))  # Max number of errors before card is failed
        self.perfect_time_limit = int(settings.value(
            "perfect_time_limit"))  # Number of seconds that an answer must be given in order to achieve a 5.
        self.incorrect_limit = int(settings.value(
            "incorrect_limit")) * 1000  # Number of seconds before card is failed, convert to milliseconds

        self.answer_timer = QtCore.QTimer()  # Keeps track of how long the user has to answer
        self.answer_timer.setSingleShot(True)  # Want it to fire once when incorrect_limit is met
        self.answer_timer.timeout.connect(self.time_out)

        self.repetitions_flag = repetitions_flag  # If doing revisions, this flag enables updates to the database. Otherwise, we dont want to modify anything
        self.profile = profile  # DB connection

        random.shuffle(cards)
        self.cards = cards
        self.deck_name = deck_name
        self.setupUi(self)
        self.setWindowTitle(deck_name)

        self.answerEdit.installEventFilter(
            self)  # Connecting event to answer edit, pressing enter will input answer/draw card
        self.exitBtn.clicked.connect(self.close)
        self.skipBtn.clicked.connect(self.skip_question)
        self.drawn_card = None  # Keeping track of current card
        self.start_time = None  # This is set to current time when a card is drawn, for comparison to when answered.
        self.answering_flag = False  # Pressing enter will draw a card/input an answer. This flag keeps track of which occurs

        self.resultLabel.setAlignment(
            QtCore.Qt.AlignCenter)  # This has unintended side effects when defined in the class, so setting here.

        self.questionLabel.setText(deck_name)

        # self.setWindowState(QtCore.Qt.WindowMaximized)  # self.showMaximised has some strange side effects, this produces the desired result.

    def gen_due_date(self):
        # Generates when a card is next due to be drawn. Based on supermems SM-2 spaced repetition algorithm
        if self.drawn_card.repetitions <= 1:
            return datetime.today().date() + timedelta(days=1)
        elif self.drawn_card.repetitions == 2:
            return datetime.today().date() + timedelta(days=6)
        else:
            return datetime.today().date() + timedelta(
                days=math.floor((self.drawn_card.repetitions - 1) * self.drawn_card.score))

    def draw_card(self):
        # If there is a card to draw, remove it from list of cards and set it as the drawn card. Initialise variables and clear elements on UI for new card.
        if len(self.cards) > 0:
            self.update_result_label("background-color:white", "")
            self.answering_flag = True
            self.drawn_card = self.cards.pop(0)
            self.spelling_error = 0
            self.start_time = time.time()
            self.questionLabel.setText(self.drawn_card.question)
            self.answerEdit.clear()
            self.answerEdit.setFocus()
            self.answer_timer.start(self.incorrect_limit)
        else:
            # If deck is finished (no cards to draw), clear everything and inform user.
            self.questionLabel.clear()
            self.answerEdit.clear()
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Information)
            msg.setText(self.deck_name + " finished")
            msg.setWindowTitle(self.deck_name)
            msg.exec()
            self.close()

    def check_answer(self):
        # If answer is correct, generate quality of answer and update card. If not correct, increment mistakes counter.
        # When mistakes counter == error_limit, card marked as failed.
        if self.answerEdit.text().rstrip().lstrip().lower() == self.drawn_card.answer.lower():
            self.answering_flag = False
            self.update_result_label("background-color:green", "Correct!")
            timer = time.time() - self.start_time
            self.answer_timer.stop()
            # Generate quality of response using the spelling mistakes and time taken. Anything lower than 3 is a fail.
            if timer < self.perfect_time_limit and self.spelling_error <= self.allowed_errors:
                quality = 5
            elif (timer > self.perfect_time_limit) ^ (self.spelling_error > self.allowed_errors):
                quality = 4
            # elif timer > self.perfect_time_limit and self.spelling_error:
            else:
                quality = 3
            self.update_card(quality)
        else:
            self.spelling_error = self.spelling_error + 1
            display_str = "Incorrect - " + self.answerEdit.text()
            self.answerEdit.clear()
            self.update_result_label("background-color:orange", display_str)
            if self.spelling_error >= self.error_limit:
                self.skip_question()

    def time_out(self):
        # If time limit is reached, skip question
        self.update_card(2)
        self.answering_flag = False
        display_str = "Times up - " + self.drawn_card.answer
        self.update_result_label("background-color:red", display_str)
        print("Times up!")

    def skip_question(self):
        # If time limit is not reached, but another parameter is met, skip question. These need to be two separate functions. Probably a better way to do this?
        if self.answering_flag:
            self.answer_timer.stop()
            self.update_card(2)
            self.answering_flag = False
            display_str = "Fail - " + self.drawn_card.answer
            self.update_result_label("background-color:red", display_str)
            self.answerEdit.setFocus()
            print("Skipped")

    def update_result_label(self, colour, display_str):
        # Results label displays correct, incorrect, etc.
        self.resultLabel.setStyleSheet(colour)
        self.resultLabel.setText(display_str)

    def update_card(self, quality):
        # repetitions_flag used to determine if revisions are being done. If true, then DB needs to be updated with due dates.
        # We only need to generate new scores if quality of response is >2. 2 or less is a fail, and the card is treated as a new card.
        if self.repetitions_flag:
            if quality > 2:
                self.drawn_card.repetitions = self.drawn_card.repetitions + 1
                current_score = self.drawn_card.score
                self.drawn_card.score = gen_score(current_score, quality)
            else:
                self.drawn_card.repetitions = 0

            self.drawn_card.date_played = date.today()

            self.drawn_card.date_due = self.gen_due_date()

            self.profile.update_card(self.drawn_card, self.deck_name)

    def eventFilter(self, obj, event):
        # Handles enter keypresses. Enter will draw a card when one is needed to give user time to read correct response if needed.
        # Otherwise it will enter the answer.
        if event.type() == QtCore.QEvent.KeyPress and obj is self.answerEdit:
            if event.key() == QtCore.Qt.Key_Return and self.answerEdit.hasFocus():
                if self.answering_flag:
                    self.check_answer()
                else:
                    self.draw_card()
        return super().eventFilter(obj, event)


def write_settings(settings_dict, settings):
    # Write settings to settings file. settings_dict keys will be the settings, and their values the value.
    # More options can be easily added this way changing only one thing.
    for key in settings_dict:
        settings.setValue(key, settings_dict[key])


class settingsWindow(QtWidgets.QDialog, Windows.settings.Ui_Dialog):
    # Settings window has boxes containing values for each setting. Can be applied and written in settings file.
    def __init__(self, settings, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.settings = settings
        self.allowed_errors.setValue(int(self.settings.value("allowed_errors")))
        self.error_limit.setValue(int(self.settings.value("error_limit")))
        self.perfect_time.setValue(int(self.settings.value("perfect_time_limit")))
        self.incorrect_limit.setValue(int(self.settings.value("incorrect_limit")))

        self.setWindowTitle("Settings")

        self.exitBtn.clicked.connect(self.close)
        self.applyBtn.clicked.connect(self.update_button)

    def update_button(self):
        res = self.update_settings()
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setText(res)
        msg.setWindowTitle("Message")
        msg.exec()

    def update_settings(self):
        # Ensure legitimate settings for each option, and pass to update settings function. Message returned and displayed in a message box to inform of result
        if 0 < self.allowed_errors.value() < self.error_limit.value():
            if 0 < self.perfect_time.value() < self.incorrect_limit.value():
                new_settings = {"allowed_errors": self.allowed_errors.value(),
                                "error_limit": self.error_limit.value(),
                                "perfect_time_limit": self.perfect_time.value(),
                                "incorrect_limit": self.incorrect_limit.value()}
                write_settings(new_settings, self.settings)

                return "Settings changed successfully"
            else:
                return "Error - Please ensure that the incorrect time limit is higher than the perfect score limit"
        else:
            return "Error - Please ensure that the error limit is higher than the allowed mistakes"


def get_settings():
    # returns a settings file. Creates one with default settings if none exists.
    if os.path.exists(path.join(path.expanduser("~"), ".SpaceLearn", "SpaceLearn.conf")):
        return QtCore.QSettings(path.join(path.expanduser("~"), ".SpaceLearn", "SpaceLearn.conf"),
                                QtCore.QSettings.IniFormat)
    else:
        settings = QtCore.QSettings(path.join(path.expanduser("~"), ".SpaceLearn", "SpaceLearn.conf"),
                                    QtCore.QSettings.IniFormat)
        default_settings = {"allowed_errors": 1,
                            "error_limit": 5,
                            "perfect_time_limit": 10,
                            "incorrect_limit": 30}
        write_settings(default_settings, settings)
        return settings


def edit_settings():
    # Launch window for editing settings
    dialog = settingsWindow(get_settings())
    dialog.exec()
    return


def get_cards_due(cards):
    # Return just the cards that are due to be completed for revisions
    return [x for x in cards if datetime.strptime(x.date_due, '%Y-%m-%d').date() <= date.today()]


class ViewDecksWindow(QtWidgets.QDialog, Windows.viewDeck.Ui_Dialog):
    # Main window of application. Displays all decks and revisions due, as well as options to add, edit, and play decks.
    def __init__(self, parent=None):
        super().__init__(parent)

        # Sets up connection to SQLite database, creating it if not existing.
        self.profile = Profile(getlogin(), path.join(path.expanduser("~"), ".SpaceLearn"))

        self.setupUi(self)

        self.setWindowTitle("Space Learn")

        # Populates list of decks.
        self.update_list()

        # Connecting UI to functions.
        self.addBtn.clicked.connect(self.add_deck)
        self.removeBtn.clicked.connect(self.remove_deck)
        self.editBtn.clicked.connect(self.edit_deck)
        self.exitBtn.clicked.connect(self.close)
        self.playBtn.clicked.connect(self.play_deck)
        self.settingsBtn.clicked.connect(edit_settings)

        self.selected_deck = None
        self.listWidget.itemClicked.connect(self.list_click)

    def closeEvent(self, event):
        # Closing DB gracefully on app close
        print("Closing app")
        self.profile.close_db()

    def play_deck(self):
        # Ensure a deck is selected.
        if self.selected_deck is not None:
            cards = self.profile.get_deck(self.selected_deck)

            # Determining method of play. Just revisions or whole deck? More can be added as needed.
            match self.playBox.currentText():
                case "Revisions":
                    cards = get_cards_due(cards)
                case "Entire Deck":
                    print("Entire deck loaded")
            # If there are cards to play, pass to the playdeckwindow.
            if len(cards) > 0:
                dialog = PlayDeckWindow(self.profile, self.selected_deck, cards, True, get_settings())
                dialog.exec()
                self.update_list()
            else:
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Information)
                msg.setText("No cards to play")
                msg.setWindowTitle("Message")
                msg.exec()

    def list_click(self, item):
        # Keep track of which deck is selected
        print(item.text())
        self.selected_deck = item.text()

    def update_list(self):
        # Update the lists displaying deck and repetitions due.
        self.listWidget.clear()
        self.repsList.clear()
        names = self.profile.get_deck_names()
        for name in names:
            deck = self.profile.get_deck(name)
            revisions = get_cards_due(deck)
            display = "Revisions due: " + str(len(revisions))
            self.repsList.insertItem(0, display)
            self.listWidget.insertItem(0, name)  # First argument passed is position in list, this ensures that its always first

    def add_deck(self):
        # Launch dialog to add a new deck to the database
        dialog = AddDeckWindow(self.profile)
        dialog.exec()
        self.update_list()

    def remove_deck(self):
        # Remove deck from database after asking for confirmation
        if self.selected_deck is not None:
            query = QtWidgets.QMessageBox
            res = query.question(self, 'Delete Deck', 'Are you sure you want to delete ' + self.selected_deck + '?',
                                 query.Yes | query.No)
            if res == query.Yes:
                self.profile.remove_deck(self.selected_deck)
                self.update_list()
                self.selected_deck = None  # Failsafe in case selected is not set to None when removed

    def edit_deck(self):
        # Launch dialog to add/remove cards from deck.
        if self.selected_deck is not None:
            dialog = EditDeckWindow(self.profile, self.selected_deck)
            dialog.exec()
            self.update_list()


class EditDeckWindow(QtWidgets.QDialog, Windows.editDeck.Ui_Dialog):
    # Provides a UI for adding/removing cards to a deck.
    def __init__(self, profile, deck_name, parent=None):
        super().__init__(parent)

        self.profile = profile  # Passed DB connection

        self.deck_name = deck_name

        self.setupUi(self)
        self.setWindowTitle(str(deck_name))

        # Connecting UI elements to functions
        self.addBtn.clicked.connect(self.add_card)
        self.removeBtn.clicked.connect(self.remove_card)
        self.exitBtn.clicked.connect(self.close)

        self.selected_card = None
        self.cardList.itemClicked.connect(self.list_click)

        # Keeps track of positions of cards in list, using card IDs
        self.list_map = {}

        # Add listener for key press on edit boxes to allow easy adding of cards.
        self.answerEdit.installEventFilter(self)
        self.questionEdit.installEventFilter(self)

        self.update_card_list()

    def list_click(self):
        # Keep track of which card is clicked
        self.selected_card = self.list_map[self.cardList.currentRow()]
        print(self.selected_card)

    def add_card(self):
        # Add new card to the deck
        if len(self.questionEdit.text()) > 0 and len(self.answerEdit.text()) > 0:
            self.profile.add_card(self.deck_name, self.questionEdit.text(), self.answerEdit.text())
            self.update_card_list()
            self.questionEdit.clear()
            self.answerEdit.clear()
            self.questionEdit.setFocus()

    def remove_card(self):
        # Remove card from deck
        if self.selected_card is not None:
            self.profile.remove_card(self.deck_name, self.selected_card)
            self.update_card_list()
            self.selected_card = None

    def eventFilter(self, obj, event):
        # Listener for key press on edit boxes to allow easy adding of cards.
        if event.type() == QtCore.QEvent.KeyPress and (obj is self.answerEdit or obj is self.questionEdit):
            if event.key() == QtCore.Qt.Key_Return and (obj is self.answerEdit or obj is self.questionEdit):
                self.add_card()
        return super().eventFilter(obj, event)

    def update_card_list(self):
        # Updates UI to display new cards/remove removed cards
        self.cardList.clear()
        cards = self.profile.get_deck(self.deck_name)
        list_pos = 0
        for single_card in cards:
            display_str = str(single_card.question) + "   -   " + str(single_card.answer)
            self.cardList.insertItem(list_pos, display_str)
            self.list_map[list_pos] = single_card.cardID
            list_pos = list_pos + 1


class AddDeckWindow(QtWidgets.QDialog, Windows.addDeck.Ui_Dialog):
    # Simple dialog to add a new deck to the database
    def __init__(self, profile, parent=None):
        super().__init__(parent)

        self.profile = profile

        self.setupUi(self)

        self.addDeckBtn.clicked.connect(self.add_deck)
        self.cancelBtn.clicked.connect(self.close)

    def add_deck(self):
        res = self.profile.add_deck(self.plainTextEdit.toPlainText())
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setText(res)
        msg.setWindowTitle("Message")
        msg.exec()


def application():
    app = QtWidgets.QApplication(sys.argv)

    first_window = ViewDecksWindow()
    # first_window.showMaximized()       # Not really enough info on the screen to justify showing maximised...
    first_window.show()

    # Set the form title
    first_window.setWindowTitle("Space Learn")

    # Run the program
    sys.exit(app.exec())


def main():
    print("App start")
    application()


if __name__ == '__main__':
    main()
