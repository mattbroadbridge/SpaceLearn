#import PyQt5
import math
import os.path
import random
import time
from datetime import datetime, timedelta, date

from PyQt5 import QtGui, QtCore, QtWidgets
import sys
from os import path, chdir, mkdir, getlogin

from PyQt5.QtGui import QTextCursor
from PyQt5.QtWidgets import QMessageBox

import Windows.mainWindow
import Windows.addDeck
import Windows.viewDeck
import Windows.editDeck
import Windows.playDeck
import Windows.settings
from Objects.profile import Profile, card


class PlayDeckWindow(QtWidgets.QDialog, Windows.playDeck.Ui_Dialog):
    def __init__(self, profile, deck_name, cards, repetitions_flag, settings, parent=None):
        super().__init__(parent)
        self.spelling_error = 0
        self.allowed_errors = int(settings.value("allowed_errors"))
        self.error_limit = int(settings.value("error_limit"))
        self.perfect_time_limit = int(settings.value("perfect_time_limit"))        # Number of seconds that an answer must be given in order to achieve a 5. TODO implement settings so this can be modified by the user
        self.incorrect_limit = int(settings.value("incorrect_limit")) * 1000        # Convert to miliseconds
        self.answer_timer = QtCore.QTimer()
        self.answer_timer.setSingleShot(True)
        self.answer_timer.timeout.connect(self.time_out)
        self.repetitions_flag = repetitions_flag
        self.profile = profile
        random.shuffle(cards)
        self.cards = cards
        self.deck_name = deck_name
        self.setupUi(self)
        self.setWindowTitle(deck_name)
        self.answerEdit.installEventFilter(self)
        self.exitBtn.clicked.connect(self.close)
        self.skipBtn.clicked.connect(self.skip_question)
        self.drawn_card = None
        self.start_time = None
        self.draw_card()


        #self.setWindowState(QtCore.Qt.WindowMaximized)  # self.showMaximised has some strange side effects, this produces the desired result.



    def gen_score(self, old_score, quality_score):
        res = old_score+(0.1-(5-quality_score)*(0.08+(5-quality_score)*0.02))
        if res > 2.5:
            return 2.5
        elif res < 1.1:
            return 1.1
        else:
            return res

    def gen_due_date(self):
        if self.drawn_card.repetitions <= 1:
            return datetime.today().date() + timedelta(days=1)
        elif self.drawn_card.repetitions == 2:
            return datetime.today().date() + timedelta(days=6)
        else:
            return datetime.today().date() + timedelta(days=math.floor((self.drawn_card.repetitions - 1) * self.drawn_card.score))


    def draw_card(self):
        if len(self.cards) > 0:
            self.drawn_card = self.cards.pop(0)
            self.spelling_error = 0
            self.start_time = time.time()
            self.questionLabel.setText(self.drawn_card.question)
            self.answerEdit.clear()
            self.answerEdit.setFocus()
            self.answer_timer.start(self.incorrect_limit)
        else:
            self.questionLabel.clear()
            self.answerEdit.clear()
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Information)
            msg.setText(self.deck_name + " finished")
            msg.setWindowTitle(self.deck_name)
            msg.exec()
            self.close()

    def check_answer(self):
        if self.answerEdit.text().rstrip().lstrip() == self.drawn_card.answer:
            timer = time.time() - self.start_time
            self.answer_timer.stop()
            if timer < self.perfect_time_limit and self.spelling_error <= self.allowed_errors:
                quality = 5
            elif (timer > self.perfect_time_limit) ^ (self.spelling_error > self.allowed_errors):
                quality = 4
            #elif timer > self.perfect_time_limit and self.spelling_error:
            else:
                quality = 3
            self.update_card(quality)
            self.draw_card()
        else:
            self.spelling_error = self.spelling_error + 1
            if self.spelling_error >= self.error_limit:
                self.skip_question()

    # If time limit is reached, skip question
    def time_out(self):
        self.update_card(2)
        self.draw_card()
        print("Times up!")

    # If time limit is not reached, but another parameter is met, skip question. These need to be two separate functions. Probably a better way to do this?
    def skip_question(self):
        self.answer_timer.stop()
        self.update_card(2)
        self.draw_card()
        print("Skipped")


    def update_card(self, quality):

        if self.repetitions_flag:
            if quality > 2:
                self.drawn_card.repetitions = self.drawn_card.repetitions + 1
                current_score = self.drawn_card.score
                self.drawn_card.score = self.gen_score(current_score, quality)
            else:
                self.drawn_card.repetitions = 0

            self.drawn_card.date_played = date.today()

            self.drawn_card.date_due = self.gen_due_date()

            self.profile.update_card(self.drawn_card, self.deck_name)

    def eventFilter(self, obj, event):
        if event.type() == QtCore.QEvent.KeyPress and obj is self.answerEdit:
            if event.key() == QtCore.Qt.Key_Return and self.answerEdit.hasFocus():
                self.check_answer()
        return super().eventFilter(obj, event)


def writeSettings(settings_dict, settings):
    settings.setValue('allowed_errors', settings_dict["allowed_errors"])
    settings.setValue('error_limit', settings_dict["error_limit"])
    settings.setValue('perfect_time_limit', settings_dict["perfect_time_limit"])
    settings.setValue('incorrect_limit', settings_dict["incorrect_limit"])


class settingsWindow(QtWidgets.QDialog, Windows.settings.Ui_Dialog):
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

        if 0 < self.allowed_errors.value() < self.error_limit.value():
            if 0 < self.perfect_time.value() < self.incorrect_limit.value():
                new_settings = {"allowed_errors": self.allowed_errors.value(),
                                "error_limit": self.error_limit.value(),
                                "perfect_time_limit": self.perfect_time.value(),
                                "incorrect_limit": self.incorrect_limit.value()}
                writeSettings(new_settings, self.settings)

                return "Settings changed successfully"
            else:
                return "Error - Please ensure that the incorrect time limit is higher than the perfect score limit"
        else:
            return "Error - Please ensure that the error limit is higher than the allowed mistakes"





class ViewDecksWindow(QtWidgets.QDialog, Windows.viewDeck.Ui_Dialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.profile = Profile(getlogin(), path.join(path.expanduser("~"), ".SpaceLearn"))

        self.setupUi(self)

        self.setWindowTitle("View Decks")

        self.update_list()

        self.addBtn.clicked.connect(self.add_deck)
        self.removeBtn.clicked.connect(self.remove_deck)
        self.editBtn.clicked.connect(self.edit_deck)
        self.exitBtn.clicked.connect(self.close)
        self.playBtn.clicked.connect(self.play_deck)
        self.settingsBtn.clicked.connect(self.edit_settings)

        self.selected_deck = None
        self.listWidget.itemClicked.connect(self.list_click)


    def get_settings(self):
        if os.path.exists(path.join(path.expanduser("~"), ".SpaceLearn", "SpaceLearn.conf")):
            return QtCore.QSettings(path.join(path.expanduser("~"), ".SpaceLearn", "SpaceLearn.conf"), QtCore.QSettings.IniFormat)
        else:
            settings = QtCore.QSettings(path.join(path.expanduser("~"), ".SpaceLearn", "SpaceLearn.conf"), QtCore.QSettings.IniFormat)
            default_settings = {"allowed_errors": 1,
                                "error_limit": 5,
                                "perfect_time_limit": 10,
                                "incorrect_limit": 30}
            writeSettings(default_settings, settings)
            return settings

    def closeEvent(self, event):
        print("Closing app")
        self.profile.close_db()


    def edit_settings(self):
        dialog = settingsWindow(self.get_settings())
        dialog.exec()
        return

    def play_deck(self):
        if self.selected_deck is not None:
            cards = self.profile.get_deck(self.selected_deck)

            match self.playBox.currentText():
                case "Revisions":
                    cards = [x for x in cards if datetime.strptime(x.date_due, '%Y-%m-%d').date() <= date.today()]
                case "Entire Deck":
                    print("Entire deck loaded")

            if len(cards) > 0:
                dialog = PlayDeckWindow(self.profile, self.selected_deck, cards, True, self.get_settings())
                dialog.exec()
            else:
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Information)
                msg.setText("No cards to play")
                msg.setWindowTitle("Message")
                msg.exec()


    def list_click(self, item):
        print(item.text())
        self.selected_deck = item.text()

    def update_list(self):
        self.listWidget.clear()
        names = self.profile.get_deck_names()
        for name in names:
            self.listWidget.insertItem(0, name)    # First argument passed is position in list, this ensures that its always first

    def add_deck(self):
        dialog = AddDeckWindow(self.profile)
        dialog.exec()
        self.update_list()

    def remove_deck(self):
        if self.selected_deck is not None:
            query = QtWidgets.QMessageBox
            res = query.question(self, 'Delete Deck', 'Are you sure you want to delete ' + self.selected_deck + '?', query.Yes | query.No)
            if res == query.Yes:
                self.profile.remove_deck(self.selected_deck)
                self.update_list()
                self.selected_deck = None       # Failsafe in case selected is not set to None when removed

    def edit_deck(self):
        if self.selected_deck is not None:
            dialog = EditDeckWindow(self.profile, self.selected_deck)
            dialog.exec()


class EditDeckWindow(QtWidgets.QDialog, Windows.editDeck.Ui_Dialog):
    def __init__(self, profile, deck_name, parent=None):
        super().__init__(parent)

        self.profile = profile

        self.deck_name = deck_name

        self.setupUi(self)
        self.setWindowTitle(str(deck_name))

        self.addBtn.clicked.connect(self.add_card)
        self.removeBtn.clicked.connect(self.remove_card)
        self.exitBtn.clicked.connect(self.close)

        self.selected_card = None
        self.cardList.itemClicked.connect(self.list_click)

        self.list_map = {}

        self.update_card_list()

    def list_click(self):
        self.selected_card = self.list_map[self.cardList.currentRow()]
        print(self.selected_card)

    def add_card(self):
        self.profile.add_card(self.deck_name, self.questionEdit.toPlainText(), self.answerEdit.toPlainText())
        self.update_card_list()


    def remove_card(self):
        if self.selected_card is not None:
            self.profile.remove_card(self.deck_name, self.selected_card)
            self.update_card_list()
            self.selected_card = None


    def update_card_list(self):
        self.cardList.clear()
        cards = self.profile.get_deck(self.deck_name)
        list_pos = 0
        for single_card in cards:
            display_str = str(single_card.cardID) + ") " + str(single_card.question) + "   -   " + str(single_card.answer)
            self.cardList.insertItem(list_pos, display_str)
            self.list_map[list_pos] = single_card.cardID
            list_pos = list_pos + 1


class AddDeckWindow(QtWidgets.QDialog, Windows.addDeck.Ui_Dialog):
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
    first_window.showMaximized()
    # Set window size
    #first_window.resize(400, 300)

    # Set the form title
    first_window.setWindowTitle("Space Learn")

    # Run the program
    sys.exit(app.exec())
    return


def main():
    print("App start")
    application()


if __name__ == '__main__':
    main()
