# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui\viewDeck.ui'
#
# Created by: PyQt5 UI code generator 5.15.10
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(400, 300)
        Dialog.setStyleSheet("background-color: rgb(255, 211, 228);\n"
"background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1, stop:0 rgba(198, 117, 223, 255), stop:1 rgba(255, 255, 255, 255));\n"
"border-color: rgb(241, 185, 255);")
        self.horizontalLayout = QtWidgets.QHBoxLayout(Dialog)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.playBtn = QtWidgets.QPushButton(Dialog)
        self.playBtn.setObjectName("playBtn")
        self.verticalLayout.addWidget(self.playBtn)
        self.editBtn = QtWidgets.QPushButton(Dialog)
        self.editBtn.setStyleSheet("background-color: rgb(255, 211, 228);")
        self.editBtn.setObjectName("editBtn")
        self.verticalLayout.addWidget(self.editBtn)
        self.addBtn = QtWidgets.QPushButton(Dialog)
        self.addBtn.setStyleSheet("background-color: rgb(255, 211, 228);")
        self.addBtn.setObjectName("addBtn")
        self.verticalLayout.addWidget(self.addBtn)
        self.removeBtn = QtWidgets.QPushButton(Dialog)
        self.removeBtn.setStyleSheet("background-color: rgb(255, 211, 228);")
        self.removeBtn.setObjectName("removeBtn")
        self.verticalLayout.addWidget(self.removeBtn)
        self.exitBtn = QtWidgets.QPushButton(Dialog)
        self.exitBtn.setStyleSheet("background-color: rgb(255, 211, 228);")
        self.exitBtn.setObjectName("exitBtn")
        self.verticalLayout.addWidget(self.exitBtn)
        self.horizontalLayout.addLayout(self.verticalLayout)
        self.listWidget = QtWidgets.QListWidget(Dialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.listWidget.sizePolicy().hasHeightForWidth())
        self.listWidget.setSizePolicy(sizePolicy)
        self.listWidget.setObjectName("listWidget")
        self.horizontalLayout.addWidget(self.listWidget)

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Dialog"))
        self.playBtn.setText(_translate("Dialog", "Play"))
        self.editBtn.setText(_translate("Dialog", "Edit (Add cards)"))
        self.addBtn.setText(_translate("Dialog", "Add"))
        self.removeBtn.setText(_translate("Dialog", "Remove"))
        self.exitBtn.setText(_translate("Dialog", "Exit"))
