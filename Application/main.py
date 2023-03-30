#import PyQt5
from PyQt5 import QtGui, QtCore, QtWidgets
import sys
from os import path, chdir, mkdir, getlogin
from Windows.mainWindow import Ui_MainWindow
from Objects.profile import Profile



class MyWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(MyWindow, self).__init__()

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)


def application():
    app = QtWidgets.QApplication(sys.argv)

    first_window = MyWindow()
    first_window.show()
    # Set window size
    #first_window.resize(400, 300)

    # Set the form title
    first_window.setWindowTitle("Space Learn")

    # Run the program
    sys.exit(app.exec())
    return


def main():

    user = Profile(getlogin(), path.join(path.expanduser("~"), ".SpaceLearn"))

    print(user.add_deck("testdeck"))

    print(user.remove_deck("testdeck"))

    user.close_db()


if __name__ == '__main__':
    main()
