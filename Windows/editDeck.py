# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui\editDeck.ui'
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
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(Dialog)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout()
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.removeBtn = QtWidgets.QPushButton(Dialog)
        self.removeBtn.setObjectName("removeBtn")
        self.verticalLayout_3.addWidget(self.removeBtn)
        self.editBtn = QtWidgets.QPushButton(Dialog)
        self.editBtn.setObjectName("editBtn")
        self.verticalLayout_3.addWidget(self.editBtn)
        self.exitBtn = QtWidgets.QPushButton(Dialog)
        self.exitBtn.setObjectName("exitBtn")
        self.verticalLayout_3.addWidget(self.exitBtn)
        self.horizontalLayout.addLayout(self.verticalLayout_3)
        self.cardList = QtWidgets.QListWidget(Dialog)
        self.cardList.setObjectName("cardList")
        self.horizontalLayout.addWidget(self.cardList)
        self.verticalLayout_2.addLayout(self.horizontalLayout)
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.addBtn = QtWidgets.QPushButton(Dialog)
        self.addBtn.setObjectName("addBtn")
        self.horizontalLayout_2.addWidget(self.addBtn)
        self.questionEdit = QtWidgets.QPlainTextEdit(Dialog)
        self.questionEdit.setMaximumSize(QtCore.QSize(16777215, 50))
        self.questionEdit.setObjectName("questionEdit")
        self.horizontalLayout_2.addWidget(self.questionEdit)
        self.answerEdit = QtWidgets.QPlainTextEdit(Dialog)
        self.answerEdit.setMaximumSize(QtCore.QSize(16777215, 50))
        self.answerEdit.setObjectName("answerEdit")
        self.horizontalLayout_2.addWidget(self.answerEdit)
        self.verticalLayout.addLayout(self.horizontalLayout_2)
        self.verticalLayout_2.addLayout(self.verticalLayout)

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Dialog"))
        self.removeBtn.setText(_translate("Dialog", "Remove"))
        self.editBtn.setText(_translate("Dialog", "Edit"))
        self.exitBtn.setText(_translate("Dialog", "Exit"))
        self.addBtn.setText(_translate("Dialog", "Add"))
        self.questionEdit.setPlainText(_translate("Dialog", "Question"))
        self.answerEdit.setPlainText(_translate("Dialog", "Answer"))
