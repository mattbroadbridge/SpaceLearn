#import PyQt5
from datetime import datetime, timedelta

from PyQt5 import QtGui, QtCore, QtWidgets
import sys
from os import path, chdir, mkdir, getlogin

from PyQt5.QtWidgets import QMessageBox

import Windows.mainWindow
import Windows.addDeck
import Windows.viewDeck
import Windows.editDeck
from Objects.profile import Profile, card


class MyWindow(QtWidgets.QMainWindow, Windows.mainWindow.Ui_MainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)


        self.setupUi(self)

        # This variable holds an instance of an opened window, to stop pythons garbage collection immediately shutting it
        #self.dialog = None

        # Connecting elements of the UI to functions
        self.viewBtn.clicked.connect(self.view_decks)
        #self.RemoveBtn.clicked.connect(self.remove_deck)

        self.profile = Profile(getlogin(), path.join(path.expanduser("~"), ".SpaceLearn"))

    def view_decks(self):
        dialog = ViewDecksWindow(self.profile)
        dialog.exec()

    def closeEvent(self, event):
        print("Closing app")
        self.profile.close_db()

class PlayDeckWindow(QtWidgets.QDialog, Windows.viewDeck.Ui_Dialog):  # TODO Change this to play deck window when designed.

    def __init__(self, profile, cards, parent=None):
        super().__init__(parent)

        self.profile = profile

        self.cards = cards

        self.setupUi(self)

        self.setWindowTitle("Play Deck")    # TODO Display deck name

    def gen_score(self, played_card, quality_score):
        return played_card.score+(0.1-(5-quality_score)*(0.08+(5-quality_score)*0.02))

    def gen_due_date(self, played_card):    # TODO Test this
        if played_card.repetitions <= 1:
            return datetime.today() + timedelta(days=1)
        elif played_card.repetitions == 2:
            return datetime.today() + timedelta(days=6)
        else:
            return (played_card.repetitions - 1) * played_card.score





class ViewDecksWindow(QtWidgets.QDialog, Windows.viewDeck.Ui_Dialog):
    def __init__(self, profile, parent=None):
        super().__init__(parent)

        self.profile = profile

        self.setupUi(self)

        self.setWindowTitle("View Decks")

        self.update_list()

        self.addBtn.clicked.connect(self.add_deck)
        self.removeBtn.clicked.connect(self.remove_deck)
        self.editBtn.clicked.connect(self.edit_deck)
        self.exitBtn.clicked.connect(self.close)

        self.selected_deck = None
        self.listWidget.itemClicked.connect(self.list_click)

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

    first_window = MyWindow()
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
