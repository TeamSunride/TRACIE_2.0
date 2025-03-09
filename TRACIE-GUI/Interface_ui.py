# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'Interface.ui'
##
## Created by: Qt User Interface Compiler version 6.6.1
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QMetaObject, QSize, Qt)
from PySide6.QtGui import (QAction, QFont)
from PySide6.QtWidgets import (QComboBox, QFrame, QGridLayout,
    QLabel, QLineEdit, QPushButton,
    QSizePolicy, QStatusBar, QTabWidget, QWidget)

from pyqtgraph import PlotWidget

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(1300, 670)
        self.actionNew = QAction(MainWindow)
        self.actionNew.setObjectName(u"actionNew")
        self.actionadd = QAction(MainWindow)
        self.actionadd.setObjectName(u"actionadd")
        self.actionPreferences = QAction(MainWindow)
        self.actionPreferences.setObjectName(u"actionPreferences")
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.gridLayout_2 = QGridLayout(self.centralwidget)
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.tabWidget = QTabWidget(self.centralwidget)
        self.tabWidget.setObjectName(u"tabWidget")
        self.configureTab = QWidget()
        self.configureTab.setObjectName(u"configureTab")
        self.gridLayout_7 = QGridLayout(self.configureTab)
        self.gridLayout_7.setObjectName(u"gridLayout_7")
        self.gridLayout_6 = QGridLayout()
        self.gridLayout_6.setObjectName(u"gridLayout_6")
        self.label_14 = QLabel(self.configureTab)
        self.label_14.setObjectName(u"label_14")
        sizePolicy = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_14.sizePolicy().hasHeightForWidth())
        self.label_14.setSizePolicy(sizePolicy)
        self.label_14.setMinimumSize(QSize(10, 10))
        self.label_14.setBaseSize(QSize(10, 10))

        self.gridLayout_6.addWidget(self.label_14, 0, 0, 1, 1)

        self.connectionStatusResultLabel = QLabel(self.configureTab)
        self.connectionStatusResultLabel.setObjectName(u"connectionStatusResultLabel")

        self.gridLayout_6.addWidget(self.connectionStatusResultLabel, 2, 4, 1, 1)

        self.label_16 = QLabel(self.configureTab)
        self.label_16.setObjectName(u"label_16")
        sizePolicy.setHeightForWidth(self.label_16.sizePolicy().hasHeightForWidth())
        self.label_16.setSizePolicy(sizePolicy)

        self.gridLayout_6.addWidget(self.label_16, 4, 0, 1, 1)

        self.label_15 = QLabel(self.configureTab)
        self.label_15.setObjectName(u"label_15")
        sizePolicy1 = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.label_15.sizePolicy().hasHeightForWidth())
        self.label_15.setSizePolicy(sizePolicy1)
        font = QFont()
        font.setBold(True)
        self.label_15.setFont(font)
        self.label_15.setAlignment(Qt.AlignCenter)

        self.gridLayout_6.addWidget(self.label_15, 2, 0, 1, 1)

        self.deviceConnectButton = QPushButton(self.configureTab)
        self.deviceConnectButton.setObjectName(u"deviceConnectButton")
        self.deviceConnectButton.setFont(font)

        self.gridLayout_6.addWidget(self.deviceConnectButton, 2, 2, 1, 1)

        self.line_2 = QFrame(self.configureTab)
        self.line_2.setObjectName(u"line_2")
        self.line_2.setFrameShape(QFrame.HLine)
        self.line_2.setFrameShadow(QFrame.Sunken)

        self.gridLayout_6.addWidget(self.line_2, 6, 0, 1, 5)

        self.label_17 = QLabel(self.configureTab)
        self.label_17.setObjectName(u"label_17")
        self.label_17.setFont(font)
        self.label_17.setContextMenuPolicy(Qt.DefaultContextMenu)
        self.label_17.setAlignment(Qt.AlignCenter)

        self.gridLayout_6.addWidget(self.label_17, 2, 3, 1, 1)

        self.line = QFrame(self.configureTab)
        self.line.setObjectName(u"line")
        sizePolicy2 = QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.line.sizePolicy().hasHeightForWidth())
        self.line.setSizePolicy(sizePolicy2)
        self.line.setFrameShape(QFrame.HLine)
        self.line.setFrameShadow(QFrame.Sunken)

        self.gridLayout_6.addWidget(self.line, 3, 0, 1, 5)

        self.deviceComboBox = QComboBox(self.configureTab)
        self.deviceComboBox.setObjectName(u"deviceComboBox")

        self.gridLayout_6.addWidget(self.deviceComboBox, 2, 1, 1, 1)

        self.channel1Button = QPushButton(self.configureTab)
        self.channel1Button.setObjectName(u"channel1Button")

        self.gridLayout_6.addWidget(self.channel1Button, 4, 1, 1, 1)

        self.channel2Button = QPushButton(self.configureTab)
        self.channel2Button.setObjectName(u"channel2Button")

        self.gridLayout_6.addWidget(self.channel2Button, 4, 2, 1, 1)


        self.gridLayout_7.addLayout(self.gridLayout_6, 0, 0, 1, 1)

        self.tabWidget.addTab(self.configureTab, "")
        self.flightTab = QWidget()
        self.flightTab.setObjectName(u"flightTab")
        self.flightTab.setContextMenuPolicy(Qt.DefaultContextMenu)
        self.gridLayout_3 = QGridLayout(self.flightTab)
        self.gridLayout_3.setObjectName(u"gridLayout_3")
        self.gridLayout = QGridLayout()
        self.gridLayout.setObjectName(u"gridLayout")
        self.label_8 = QLabel(self.flightTab)
        self.label_8.setObjectName(u"label_8")

        self.gridLayout.addWidget(self.label_8, 3, 6, 1, 1)

        self.flightPlotsTimeSelectionComboBox = QComboBox(self.flightTab)
        self.flightPlotsTimeSelectionComboBox.setObjectName(u"flightPlotsTimeSelectionComboBox")

        self.gridLayout.addWidget(self.flightPlotsTimeSelectionComboBox, 8, 2, 1, 2)

        self.line_3 = QFrame(self.flightTab)
        self.line_3.setObjectName(u"line_3")
        self.line_3.setFrameShape(QFrame.HLine)
        self.line_3.setFrameShadow(QFrame.Sunken)

        self.gridLayout.addWidget(self.line_3, 7, 2, 1, 7)

        self.flightPackageAgeLabel = QLabel(self.flightTab)
        self.flightPackageAgeLabel.setObjectName(u"flightPackageAgeLabel")
        font1 = QFont()
        font1.setPointSize(20)
        self.flightPackageAgeLabel.setFont(font1)
        self.flightPackageAgeLabel.setFrameShape(QFrame.Box)
        self.flightPackageAgeLabel.setAlignment(Qt.AlignCenter)

        self.gridLayout.addWidget(self.flightPackageAgeLabel, 4, 7, 1, 2)

        self.line_4 = QFrame(self.flightTab)
        self.line_4.setObjectName(u"line_4")
        self.line_4.setFrameShape(QFrame.VLine)
        self.line_4.setFrameShadow(QFrame.Sunken)

        self.gridLayout.addWidget(self.line_4, 0, 0, 9, 1)

        self.flightAltitudeLabel = QLabel(self.flightTab)
        self.flightAltitudeLabel.setObjectName(u"flightAltitudeLabel")
        self.flightAltitudeLabel.setFont(font1)
        self.flightAltitudeLabel.setFrameShape(QFrame.Box)
        self.flightAltitudeLabel.setAlignment(Qt.AlignCenter)

        self.gridLayout.addWidget(self.flightAltitudeLabel, 1, 3, 1, 2)

        self.label_12 = QLabel(self.flightTab)
        self.label_12.setObjectName(u"label_12")

        self.gridLayout.addWidget(self.label_12, 1, 2, 1, 1)

        self.label_5 = QLabel(self.flightTab)
        self.label_5.setObjectName(u"label_5")
        sizePolicy3 = QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        sizePolicy3.setHorizontalStretch(0)
        sizePolicy3.setVerticalStretch(0)
        sizePolicy3.setHeightForWidth(self.label_5.sizePolicy().hasHeightForWidth())
        self.label_5.setSizePolicy(sizePolicy3)

        self.gridLayout.addWidget(self.label_5, 4, 6, 1, 1)

        self.flightSNRLabel = QLabel(self.flightTab)
        self.flightSNRLabel.setObjectName(u"flightSNRLabel")
        self.flightSNRLabel.setFont(font1)
        self.flightSNRLabel.setFrameShape(QFrame.Box)
        self.flightSNRLabel.setAlignment(Qt.AlignCenter)

        self.gridLayout.addWidget(self.flightSNRLabel, 4, 3, 1, 2)

        self.flightMaxAltitudeLabel = QLabel(self.flightTab)
        self.flightMaxAltitudeLabel.setObjectName(u"flightMaxAltitudeLabel")
        self.flightMaxAltitudeLabel.setFont(font1)
        self.flightMaxAltitudeLabel.setFrameShape(QFrame.Box)
        self.flightMaxAltitudeLabel.setAlignment(Qt.AlignCenter)

        self.gridLayout.addWidget(self.flightMaxAltitudeLabel, 1, 7, 1, 2)

        self.flightLongitudeLabel = QLabel(self.flightTab)
        self.flightLongitudeLabel.setObjectName(u"flightLongitudeLabel")
        self.flightLongitudeLabel.setFont(font1)
        self.flightLongitudeLabel.setFrameShape(QFrame.Box)
        self.flightLongitudeLabel.setAlignment(Qt.AlignCenter)

        self.gridLayout.addWidget(self.flightLongitudeLabel, 0, 7, 1, 2)

        self.label_7 = QLabel(self.flightTab)
        self.label_7.setObjectName(u"label_7")

        self.gridLayout.addWidget(self.label_7, 2, 6, 1, 1)

        self.label_2 = QLabel(self.flightTab)
        self.label_2.setObjectName(u"label_2")
        sizePolicy3.setHeightForWidth(self.label_2.sizePolicy().hasHeightForWidth())
        self.label_2.setSizePolicy(sizePolicy3)

        self.gridLayout.addWidget(self.label_2, 3, 2, 1, 1)

        self.flightHeadingLabel = QLabel(self.flightTab)
        self.flightHeadingLabel.setObjectName(u"flightHeadingLabel")
        self.flightHeadingLabel.setFont(font1)
        self.flightHeadingLabel.setFrameShape(QFrame.Box)
        self.flightHeadingLabel.setAlignment(Qt.AlignCenter)

        self.gridLayout.addWidget(self.flightHeadingLabel, 6, 3, 1, 2)

        self.flightSIVLabel = QLabel(self.flightTab)
        self.flightSIVLabel.setObjectName(u"flightSIVLabel")
        self.flightSIVLabel.setFont(font1)
        self.flightSIVLabel.setFrameShape(QFrame.Box)
        self.flightSIVLabel.setAlignment(Qt.AlignCenter)

        self.gridLayout.addWidget(self.flightSIVLabel, 3, 7, 1, 2)

        self.label_24 = QLabel(self.flightTab)
        self.label_24.setObjectName(u"label_24")

        self.gridLayout.addWidget(self.label_24, 2, 2, 1, 1)

        self.flightRSSILabel = QLabel(self.flightTab)
        self.flightRSSILabel.setObjectName(u"flightRSSILabel")
        self.flightRSSILabel.setFont(font1)
        self.flightRSSILabel.setFrameShape(QFrame.Box)
        self.flightRSSILabel.setFrameShadow(QFrame.Plain)
        self.flightRSSILabel.setAlignment(Qt.AlignCenter)

        self.gridLayout.addWidget(self.flightRSSILabel, 3, 3, 1, 2)

        self.label_6 = QLabel(self.flightTab)
        self.label_6.setObjectName(u"label_6")

        self.gridLayout.addWidget(self.label_6, 6, 6, 1, 1)

        self.line_5 = QFrame(self.flightTab)
        self.line_5.setObjectName(u"line_5")
        self.line_5.setFrameShape(QFrame.HLine)
        self.line_5.setFrameShadow(QFrame.Sunken)

        self.gridLayout.addWidget(self.line_5, 5, 2, 1, 7)

        self.flightRangeLabel = QLabel(self.flightTab)
        self.flightRangeLabel.setObjectName(u"flightRangeLabel")
        self.flightRangeLabel.setFont(font1)
        self.flightRangeLabel.setFrameShape(QFrame.Box)
        self.flightRangeLabel.setAlignment(Qt.AlignCenter)

        self.gridLayout.addWidget(self.flightRangeLabel, 2, 3, 1, 2)

        self.flightLongitudeLineEdit = QLineEdit(self.flightTab)
        self.flightLongitudeLineEdit.setObjectName(u"flightLongitudeLineEdit")

        self.gridLayout.addWidget(self.flightLongitudeLineEdit, 8, 8, 1, 1)

        self.label_3 = QLabel(self.flightTab)
        self.label_3.setObjectName(u"label_3")
        sizePolicy3.setHeightForWidth(self.label_3.sizePolicy().hasHeightForWidth())
        self.label_3.setSizePolicy(sizePolicy3)

        self.gridLayout.addWidget(self.label_3, 4, 2, 1, 1)

        self.label_13 = QLabel(self.flightTab)
        self.label_13.setObjectName(u"label_13")
        self.label_13.setFont(font)
        self.label_13.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)

        self.gridLayout.addWidget(self.label_13, 8, 4, 1, 1)

        self.flightGPSFixLabel = QLabel(self.flightTab)
        self.flightGPSFixLabel.setObjectName(u"flightGPSFixLabel")
        self.flightGPSFixLabel.setFont(font1)
        self.flightGPSFixLabel.setFrameShape(QFrame.Box)
        self.flightGPSFixLabel.setAlignment(Qt.AlignCenter)

        self.gridLayout.addWidget(self.flightGPSFixLabel, 2, 7, 1, 2)

        self.label_4 = QLabel(self.flightTab)
        self.label_4.setObjectName(u"label_4")

        self.gridLayout.addWidget(self.label_4, 6, 2, 1, 1)

        self.label_10 = QLabel(self.flightTab)
        self.label_10.setObjectName(u"label_10")

        self.gridLayout.addWidget(self.label_10, 1, 6, 1, 1)

        self.label_11 = QLabel(self.flightTab)
        self.label_11.setObjectName(u"label_11")

        self.gridLayout.addWidget(self.label_11, 0, 6, 1, 1)

        self.label_9 = QLabel(self.flightTab)
        self.label_9.setObjectName(u"label_9")

        self.gridLayout.addWidget(self.label_9, 0, 2, 1, 1)

        self.label_18 = QLabel(self.flightTab)
        self.label_18.setObjectName(u"label_18")

        self.gridLayout.addWidget(self.label_18, 8, 7, 1, 1)

        self.flightGoogleMapsButton = QPushButton(self.flightTab)
        self.flightGoogleMapsButton.setObjectName(u"flightGoogleMapsButton")
        self.flightGoogleMapsButton.setFont(font)

        self.gridLayout.addWidget(self.flightGoogleMapsButton, 10, 2, 1, 3)

        self.flightElevationLabel = QLabel(self.flightTab)
        self.flightElevationLabel.setObjectName(u"flightElevationLabel")
        self.flightElevationLabel.setFont(font1)
        self.flightElevationLabel.setFrameShape(QFrame.Box)
        self.flightElevationLabel.setAlignment(Qt.AlignCenter)

        self.gridLayout.addWidget(self.flightElevationLabel, 6, 7, 1, 2)

        self.exportKMLButton = QPushButton(self.flightTab)
        self.exportKMLButton.setObjectName(u"exportKMLButton")
        self.exportKMLButton.setFont(font)

        self.gridLayout.addWidget(self.exportKMLButton, 10, 6, 1, 1)

        self.zeroAltitudeButton = QPushButton(self.flightTab)
        self.zeroAltitudeButton.setObjectName(u"zeroAltitudeButton")
        self.zeroAltitudeButton.setFont(font)

        self.gridLayout.addWidget(self.zeroAltitudeButton, 10, 7, 1, 2)

        self.flightLatitudeLineEdit = QLineEdit(self.flightTab)
        self.flightLatitudeLineEdit.setObjectName(u"flightLatitudeLineEdit")

        self.gridLayout.addWidget(self.flightLatitudeLineEdit, 8, 6, 1, 1)

        self.flightLatitudeLabel = QLabel(self.flightTab)
        self.flightLatitudeLabel.setObjectName(u"flightLatitudeLabel")
        font2 = QFont()
        font2.setPointSize(20)
        font2.setStyleStrategy(QFont.PreferDefault)
        self.flightLatitudeLabel.setFont(font2)
        self.flightLatitudeLabel.setFrameShape(QFrame.Box)
        self.flightLatitudeLabel.setAlignment(Qt.AlignCenter)

        self.gridLayout.addWidget(self.flightLatitudeLabel, 0, 3, 1, 2)

        self.flightAltitudeGraphicsView = PlotWidget(self.flightTab)
        self.flightAltitudeGraphicsView.setObjectName(u"flightAltitudeGraphicsView")
        self.flightAltitudeGraphicsView.setMinimumSize(QSize(600, 500))

        self.gridLayout.addWidget(self.flightAltitudeGraphicsView, 0, 1, 8, 1)


        self.gridLayout_3.addLayout(self.gridLayout, 0, 1, 1, 1)

        self.tabWidget.addTab(self.flightTab, "")


        self.gridLayout_2.addWidget(self.tabWidget, 1, 0, 1, 1)

        MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)

        self.tabWidget.setCurrentIndex(1)


        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"MainWindow", None))
        self.actionNew.setText(QCoreApplication.translate("MainWindow", u"New", None))
        self.actionadd.setText(QCoreApplication.translate("MainWindow", u"add", None))
        self.actionPreferences.setText(QCoreApplication.translate("MainWindow", u"Preferences", None))
        self.label_14.setText(QCoreApplication.translate("MainWindow", u"<html><head/><body><p align=\"center\"><span style=\" font-size:14pt; font-weight:700;\"> CONNECT TO TRACIE TRACKER</span></p></body></html>", None))
        self.connectionStatusResultLabel.setText(QCoreApplication.translate("MainWindow", u"Disconnected", None))
        self.label_16.setText(QCoreApplication.translate("MainWindow", u"<html><head/><body><p align=\"center\"><span style=\" font-size:16pt; font-weight:700;\">Change Channel</span></p></body></html>", None))
        self.label_15.setText(QCoreApplication.translate("MainWindow", u"Device:", None))
        self.deviceConnectButton.setText(QCoreApplication.translate("MainWindow", u"CONNECT", None))
        self.label_17.setText(QCoreApplication.translate("MainWindow", u"Connection Status:", None))
        self.channel1Button.setText(QCoreApplication.translate("MainWindow", u"Channel 1 (2405MHz)", None))
        self.channel2Button.setText(QCoreApplication.translate("MainWindow", u"Channel 2 (2410MHz)", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.configureTab), QCoreApplication.translate("MainWindow", u"Config", None))
        self.label_8.setText(QCoreApplication.translate("MainWindow", u"<html><head/><body><p align=\"center\"><span style=\" font-size:26pt; font-weight:700;\">Satellites in View</span></p></body></html>", None))
        self.flightPackageAgeLabel.setText(QCoreApplication.translate("MainWindow", u"<html><head/><body><p align=\"center\"><span style=\" font-size:20pt;\">0</span></p></body></html>", None))
        self.flightAltitudeLabel.setText(QCoreApplication.translate("MainWindow", u"<html><head/><body><p align=\"center\"><span style=\" font-size:20pt;\">0.00</span></p></body></html>", None))
        self.label_12.setText(QCoreApplication.translate("MainWindow", u"<html><head/><body><p align=\"center\"><span style=\" font-size:26pt; font-weight:700;\">Altitude</span></p></body></html>", None))
        self.label_5.setText(QCoreApplication.translate("MainWindow", u"<html><head/><body><p align=\"center\"><span style=\" font-size:26pt; font-weight:700;\">Packet Age</span></p></body></html>", None))
        self.flightSNRLabel.setText(QCoreApplication.translate("MainWindow", u"<html><head/><body><p align=\"center\"><span style=\" font-size:20pt;\">10.25</span></p></body></html>", None))
        self.flightMaxAltitudeLabel.setText(QCoreApplication.translate("MainWindow", u"<html><head/><body><p align=\"center\"><span style=\" font-size:20pt;\">0.00</span></p></body></html>", None))
        self.flightLongitudeLabel.setText(QCoreApplication.translate("MainWindow", u"<html><head/><body><p align=\"center\"><span style=\" font-size:20pt;\">0.00</span></p></body></html>", None))
        self.label_7.setText(QCoreApplication.translate("MainWindow", u"<html><head/><body><p align=\"center\"><span style=\" font-size:26pt; font-weight:700;\">GPS Fix</span></p></body></html>", None))
        self.label_2.setText(QCoreApplication.translate("MainWindow", u"<html><head/><body><p align=\"center\"><span style=\" font-size:26pt; font-weight:700;\">RSSI</span></p></body></html>", None))
        self.flightHeadingLabel.setText(QCoreApplication.translate("MainWindow", u"<html><head/><body><p align=\"center\"><span style=\" font-size:20pt;\">300.0</span></p></body></html>", None))
        self.flightSIVLabel.setText(QCoreApplication.translate("MainWindow", u"<html><head/><body><p align=\"center\"><span style=\" font-size:20pt;\">0</span></p></body></html>", None))
        self.label_24.setText(QCoreApplication.translate("MainWindow", u"<html><head/><body><p align=\"center\"><span style=\" font-size:26pt; font-weight:700;\">Range</span></p></body></html>", None))
        self.flightRSSILabel.setText(QCoreApplication.translate("MainWindow", u"<html><head/><body><p align=\"center\"><span style=\" font-size:20pt;\">-10.0</span></p></body></html>", None))
        self.label_6.setText(QCoreApplication.translate("MainWindow", u"<html><head/><body><p align=\"center\"><span style=\" font-size:26pt; font-weight:700;\">Elevation</span></p></body></html>", None))
        self.flightRangeLabel.setText(QCoreApplication.translate("MainWindow", u"<html><head/><body><p align=\"center\"><span style=\" font-size:20pt;\">0.00</span></p></body></html>", None))
        self.label_3.setText(QCoreApplication.translate("MainWindow", u"<html><head/><body><p align=\"center\"><span style=\" font-size:26pt; font-weight:700;\">SNR</span></p></body></html>", None))
        self.label_13.setText(QCoreApplication.translate("MainWindow", u"Your Location (Lat, Long)", None))
        self.flightGPSFixLabel.setText(QCoreApplication.translate("MainWindow", u"<html><head/><body><p align=\"center\"><span style=\" font-size:20pt;\">0</span></p></body></html>", None))
        self.label_4.setText(QCoreApplication.translate("MainWindow", u"<html><head/><body><p align=\"center\"><span style=\" font-size:26pt; font-weight:700;\">Heading</span></p></body></html>", None))
        self.label_10.setText(QCoreApplication.translate("MainWindow", u"<html><head/><body><p align=\"center\"><span style=\" font-size:26pt; font-weight:700;\">Max Altitude</span></p></body></html>", None))
        self.label_11.setText(QCoreApplication.translate("MainWindow", u"<html><head/><body><p align=\"center\"><span style=\" font-size:26pt; font-weight:700;\">Longitude</span></p></body></html>", None))
        self.label_9.setText(QCoreApplication.translate("MainWindow", u"<html><head/><body><p align=\"center\"><span style=\" font-size:26pt; font-weight:700;\">Latitude</span></p></body></html>", None))
        self.label_18.setText(QCoreApplication.translate("MainWindow", u",", None))
        self.flightGoogleMapsButton.setText(QCoreApplication.translate("MainWindow", u"GOOGLE MAPS IT ", None))
        self.flightElevationLabel.setText(QCoreApplication.translate("MainWindow", u"<html><head/><body><p align=\"center\"><span style=\" font-size:20pt;\">0.00</span></p></body></html>", None))
        self.exportKMLButton.setText(QCoreApplication.translate("MainWindow", u"Export KML", None))
        self.zeroAltitudeButton.setText(QCoreApplication.translate("MainWindow", u"Zero altitude", None))
        self.flightLatitudeLabel.setText(QCoreApplication.translate("MainWindow", u"<html><head/><body><p align=\"center\"><span style=\" font-size:20pt;\">0.00</span></p></body></html>", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.flightTab), QCoreApplication.translate("MainWindow", u"Flight", None))
    # retranslateUi

