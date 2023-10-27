#import PyQt5
from PyQt5 import QtGui, QtCore, QtWidgets
import sys
from os import path, chdir, mkdir, getlogin

from PyQt5.QtWidgets import QMessageBox

import Windows.mainWindow
import Windows.addDeck
import Windows.viewDeck
import Windows.editDeck
from Objects.profile import Profile


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
        self.exitBtn.clicked.connect(self.close)


    def add_card(self):
        self.profile.add_card(self.deck_name, self.questionEdit.toPlainText(), self.answerEdit.toPlainText())

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


class RemoveDeckWindow(QtWidgets.QDialog, Windows.addDeck.Ui_Dialog):
    def __init__(self, profile, parent=None):
        super().__init__(parent)

        self.profile = profile

        self.setupUi(self)



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
