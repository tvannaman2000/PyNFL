import sys, os
import mysql.connector
import xml.etree.ElementTree as ET

#from PyQt5.QtSql import QSqlDatabase
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.uic import loadUi
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QApplication, QToolBar, QAction, QLabel, QMainWindow, QMenu, QFileDialog
from PyQt5.QtWidgets import QCheckBox, QStatusBar, QSplashScreen, QDialog, QHBoxLayout,QPushButton
import time
from myconn import connect_to_mysql
from dbconfig import Ui_DbConfig
from LoadTeam import LoadTeam
from login import get_db_config
from view_roster import Ui_view_roster



class Window(QMainWindow):
    """Main Window."""
    def __init__(self, parent=None):
        """Initializer."""
        super().__init__(parent)
        self.setWindowTitle("PyNFL for XOR NFL Challenge")
        self.resize(1000, 600)
        self.centralWidget = QLabel("PyNFL for XOR NFL Challenge")
        self.centralWidget.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        self.setCentralWidget(self.centralWidget)
        self._createActions()
        self._createMenuBar()        
        #self._createToolBars()

    def _createMenuBar(self):

        layout = QHBoxLayout()
        menuBar = self.menuBar()

        menuBar.setNativeMenuBar(False)
        self.setMenuBar(menuBar)

#########################################################
        # Team Menu Options
        # Creating menus using a title
        # Menu: League 
        leagueMenu = menuBar.addMenu("League")

        # Menu:  League -> Teams
        teamsubMenu = leagueMenu.addMenu("Teams")

        # Menu: League -> Teams -> Load Team
        ldteamAct = QAction("Load Team", self)
        teamsubMenu.addAction(ldteamAct)
        ldteamAct.triggered.connect(self.load_team)

        # Menu: League -> Teams -> Write Team
        wrteamAct = QAction("Write Team", self)
        teamsubMenu.addAction(wrteamAct)
        wrteamAct.triggered.connect(self.write_team)
#################################################################		
        
        # Menu: Roster 
        rosterMenu = menuBar.addMenu("Roster")

        # Menu: Roster -> View Rosters
        vwrosAct = QAction("View Rosters",self)
        rosterMenu.addAction(vwrosAct)
        vwrosAct.triggered.connect(self.view_roster)


#################################################################
        # Menu: Conferences
        leagueMenu.addAction("Conferences")
        divsubMenu = leagueMenu.addMenu("Divisions")
       
        divsubMenu.addAction("Add Division")

        divsubMenu.addAction("Edit Division")
        divsubMenu.addAction("Delete Division")
 #################################################################
        # Menu:  GM/Owner       
        gmoMenu = menuBar.addMenu("GM/Owner")

        # Menu: GM/Owner -> Player
        playerSubMenu = gmoMenu.addMenu("Player")
        
        # Menu: GM/Owner -> Player - Cut Player
        cutplayerAct = QAction("Cut Player", self)
        playerSubMenu.addAction(cutplayerAct)
        cutplayerAct.triggered.connect(self.cut_player)

        # Menu: GM/Owner -> Player -> Sign Player
        playerSubMenu.addAction("Sign Player")

        # Menu: GM/Owner -> Player -> Coach
        coachSubMenu = gmoMenu.addMenu("Coach")

        # Menu: GM/Owner -> Coach -> Fire Coach
        coachSubMenu.addAction("Fire Coach")

        # Menu: GM/Owner -> Coach -> Hire Coach
        coachSubMenu.addAction("Hire Coach")
 #################################################################
        # Menu: Schedule
        schedMenu = menuBar.addMenu("Schedule")

        # Menu: Schedule -> View
        schedMenu.addAction("View")

        # Menu: Schedule -> Playoffs
        playoffSubMenu = schedMenu.addMenu("Playoffs")

        # Menu: Schedule -> Playoffs -> Create Playoff Schedule
        playoffSubMenu.addAction("Create Playoff Schedule")

        # Menu: Schedule -> Playoffs -> View Playoff Schedule
        playoffSubMenu.addAction("View Playoff Schedule")
      
 #################################################################
        # Menu: Commissioner
        commMenu = menuBar.addMenu("Commissioner")
        # Menu: Commissioner -> Alter League
        commsubMenu = menuBar.addMenu("Alter League")
 
        # Menu: Commissioner -> Teams
        comteamsubMenu = commMenu.addMenu("Team")

        # Menu: Commissioner -> Team -> Add Team
        addteamAct = QAction("Add Team",self)
        comteamsubMenu.addAction(addteamAct)
        #addteamAct.triggered.connect(self.add_team)

        # Menu: Commissioner -> Team -> Modify Team
        edteamAct = QAction("Edit Team", self)
        comteamsubMenu.addAction(edteamAct)
        edteamAct.triggered.connect(self.edit_team)

        # Menu: Commissioner -> Team -> Delete Team
        delteamAct = QAction("Delete Team", self)
        comteamsubMenu.addAction(delteamAct)
        delteamAct.triggered.connect(self.delete_team)

        # Menu: Commissioner -> Modify Season
        commMenu.addAction("Modify Season")

        # Menu: Commissioner -> Modify Schedule
        commMenu.addAction("Modify Schedule")
 #################################################################
        # Menu: Off Season
        offMenu = menuBar.addMenu("&Off Season")

        # Menu: Off Season -> Draft
        draftsubMenu = offMenu.addMenu("Draft")

        # Menu: Off Season -> Draft -> Create Draft Players
        draftsubMenu.addAction("Create Draft Players")

        # Menu: Off Season -> Draft -> View Draft Players
        draftsubMenu.addAction("View Draft Players")

        # Menu: Off Season -> Draft -> Edit Draft Players
        draftsubMenu.addAction("Edit Draft Players")

        # Menu: Off Season -> Retire Players
        offMenu.addAction("Retire")

        # Menu: Off Season -> Training Camp
        offMenu.addAction("Training Camp")

        # Menu: Off Season -> Generate New Schedule
        offMenu.addAction("Generate New Schedule")
  #################################################################   
        # Menu:  Setup/Config
        setupMenu = menuBar.addMenu("&Setup/Config")

        # Menu:  Setup/Config -> Database
        dbsubMenu = setupMenu.addMenu("&Database")
        
        #Menu: Setup/Config -> Database -> DB Connection
        dbconnAct = QAction("DB Connection", self)
        dbsubMenu.addAction(dbconnAct)
        dbconnAct.triggered.connect(self.db_connection)
  
        # Menu: Setup/Config -> Database -> Create DB Objects
        dbsubMenu.addAction("Create DB Objects")

        # Menu: Setup/Config -> Database -> Initialize Tables
        dbsubMenu.addAction("Initialize Tables")

 #################################################################        
        # Menu: Coaches
        setcoachsubMenu = setupMenu.addMenu("&Coaches")

        # Menu: Coaches -> Create Coach
        setcoachsubMenu.addAction("Create Coach")

        # Menu: Coaches -> Edit Coach
        setcoachsubMenu.addAction("Edit Coach")

        # Menu: Coaches -> Delete Coach
        setcoachsubMenu.addAction("Delete Coach")
#################################################################
#################################################################

        helpMenu = menuBar.addMenu("&Help")
   

    def processtrigger(self,q):
        print (q.text()+" is triggered")



    def edit_team(self):
        w = QDialog(self)
        config = get_db_config()
        conn = connect_to_mysql(config, attempts=3)
        
        #conv = MySQLConverter()
        w.resize(640,480)
        w.setWindowTitle("Edit Team")  
        widget = QComboBox()
        conn.close()
        w.exec_()


    def load_team(self):
        w = QDialog(self)
        super(Window,self).__init__()
        loadUi("loadteam.ui",self)
        self.SelectBtn = self.findChild(QPushButton,"BtnSelectTeam")
        self.lable_Team.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        self.label = self.findChild(QLabel,"lable_Team")
        self.LoadBtn = self.findChild(QPushButton,"BtnLoadTeam")
        self.SelectBtn.clicked.connect(self.select_the_team)
        #self.LoadBtn.clicked.connect(lambdaLoadTeam)
        self.show()


    def select_the_team(self): 
        fname = QFileDialog.getOpenFileName(self,"Choose Team", " ","Roster Files (*.nfl)") 
        if fname:
            self.lable_Team.setText(fname[0])
            self.LoadBtn.clicked.connect(lambda: LoadTeam(fname[0]))
           


    def write_team(self):
        w = QDialog(self)
        w.resize(640,480)
        w.setWindowTitle("Write Team")  
        w.exec_()

    def delete_team(self):
        w = QDialog(self)
        w.resize(640,480)
        w.setWindowTitle("Delete Team")  
        w.exec_()


    def view_roster(self):
        self.window = QtWidgets.QMainWindow()
        self.ui = Ui_view_roster()
        self.ui.setupUi(self.window)
        self.window.show()


    def conference(self):
        w = QDialog(self)
        w.resize(640,480)
        w.setWindowTitle("Conference")  
        w.exec_()

    def add_division(self):
        w = QDialog(self)
        w.resize(640,480)
        w.setWindowTitle("Add Division")  
        w.exec_()

    def edit_division(self):
        w = QDialog(self)
        w.resize(640,480)
        w.setWindowTitle("Edit Division")  
        w.exec_()

    def delete_division(self):
        w = QDialog(self)
        w.resize(640,480)
        w.setWindowTitle("Delete Division")  
        w.exec_()

    def cut_player(self):
        w = QDialog(self)
        w.resize(640,480)
        w.setWindowTitle("Cut Player")  
        w.exec_()
    
    def sign_player(self):
        w = QDialog(self)
        w.resize(640,480)
        w.setWindowTitle("Sign Player")  
        w.exec_()

    def fire_coach(self):
        w = QDialog(self)
        w.resize(640,480)
        w.setWindowTitle("Fire Coach")  
        w.exec_()

    def hire_coach(self):
        w = QDialog(self)
        w.resize(640,480)
        w.setWindowTitle("Hire Coach")  
        w.exec_()

    def create_playoff_schedule(self):
        w = QDialog(self)
        w.resize(640,480)
        w.setWindowTitle("Create Playoff Schedule")  
        w.exec_()

    def view_schedule(self):
        w = QDialog(self)
        w.resize(640,480)
        w.setWindowTitle("View Schedule")  
        w.exec_()

    def view_playoff_schedule(self):
        w = QDialog(self)
        w.resize(640,480)
        w.setWindowTitle("View Playoff Schedule")  
        w.exec_()

    def alter_league(self):
        w = QDialog(self)
        w.resize(640,480)
        w.setWindowTitle("Alter League")  
        w.exec_()

    def modify_season(self):
        w = QDialog(self)
        w.resize(640,480)
        w.setWindowTitle("Modify Season")  
        w.exec_()

    def modify_schedule(self):
        w = QDialog(self)
        w.resize(640,480)
        w.setWindowTitle("Modify Schedule")  
        w.exec_()

    def db_connection(self):
        self.window = QtWidgets.QMainWindow()
        self.ui = Ui_DbConfig()
        self.ui.setupUi(self.window)
        self.window.show()
        

    def _createActions(self):
        # Creating action using the first constructor
        self.newAction = QAction(self)
        self.newAction.setText("&New")
        # Creating actions using the second constructor
        self.openAction = QAction("&Open...", self)
        self.addAction = QAction("&Add", self)
        self.saveAction = QAction("&Save", self)
        self.exitAction = QAction("&Exit", self)
        self.copyAction = QAction("&Copy", self)
        self.pasteAction = QAction("&Paste", self)
        self.cutAction = QAction("C&ut", self)
        self.helpContentAction = QAction("&Help Content", self)
        self.aboutAction = QAction("&About", self)

    def _createToolBars(self):
        # Using a title

        #teamToolBar = self.addToolBar("Team")
        #teamToolBar = addAction(self.newAction)
        # Using a QToolBar object
        #editToolBar = QToolBar("Edit", self)
        #self.addToolBar(editToolBar)
        # Using a QToolBar object and a toolbar area
        helpToolBar = QToolBar("Help", self)
        #self.addToolBar(Qt.LeftToolBarArea, helpToolBar)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = Window()
    win.show()
    sys.exit(app.exec_())
