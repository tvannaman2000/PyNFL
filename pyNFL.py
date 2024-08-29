import sys,os
import sqlite3
import time
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import (QApplication, 
                              QMainWindow, 
                              QVBoxLayout, 
                              QHBoxLayout, 
                              QMessageBox, 
                              QPushButton, 
                              QFrame, 
                              QAction, 
                              QDialog, QListWidget, 
                              QListWidgetItem, 
                              QTextEdit, 
                              QWidget, 
                              QLabel, 
                              QGroupBox,
                              )

from create_tables import CreateTables
from Teams import Teams
from Create_Draft_Players import Draft
from Create_FA_Players import FreeAgent
from Show_Edit_Draft import View_Draft
from Conferences import View_Conferences
from Divisions import View_Divisions
from Team_Mgmt import Manage_Teams
from Write_Games import Write_Games



class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        connection = sqlite3.connect("pyNFL.db")
        cursor = connection.cursor()
        self.setWindowTitle('PyNFL for XOR NFL Challenge')
        self.setFont(QFont('Arial',10))
        #self.setGeometry(100, 100, 400, 300)
        self.resize(1000,600)
        self.font = QFont()
        self.font.setPointSize(15)
        self.font.setFamily("Arial")

        # Create a central widget and layout
        self.central_widget = QWidget()
        self.main_layout = QHBoxLayout()
        self.central_widget.setLayout(self.main_layout)
        self.setCentralWidget(self.central_widget)

         # Create group boxes
        self.team_list_groupbox = QGroupBox("PyNFL Standings")
        self.league_groupbox = QGroupBox("PyNFL")
        self.sched_groupbox = QGroupBox("PyNFL Schedule")
        self.news_groupbox = QGroupBox("PyNFL News")

        # Create buttons for the group boxes
        self.team_list = QListWidget()
        self.team_list.itemClicked.connect(self.update_sched_list)
        self.sched_list = QListWidget()
        self.news_list = QListWidget()
        self.league_list = QListWidget()

        #######  Extract Season status
        cursor.execute("""select season, week  from nfl_status order by dt desc;""")
        row = cursor.fetchone()
        yr,wk = row
        if yr == 0: 
          SeasonValue = "Season: N/A"
          WeekValue = "Week: N/A"
        else:
          WeekValue = f"Week: {wk}"
          SeasonValue = f"Season: {yr}"
        self.season = QLabel(SeasonValue)
        self.week = QLabel(WeekValue)


        # Add buttons to the group boxes
        self.left_layout = QVBoxLayout()
        self.left_layout.addWidget(self.team_list)
        self.team_list_groupbox.setLayout(self.left_layout)

        self.right_layout1 = QVBoxLayout()
        self.right_layout1.addWidget(self.sched_list)
        self.sched_groupbox.setLayout(self.right_layout1)

        self.right_layout2 = QVBoxLayout()
        self.right_layout2.addWidget(self.news_list)
        self.news_groupbox.setLayout(self.right_layout2)

        self.league_layout = QHBoxLayout()
        #self.league_layout.addWidget(self.league_list)
        self.league_layout.addWidget(self.season)
        self.league_layout.addWidget(self.week)
        self.league_groupbox.setLayout(self.league_layout)

        # Create layout for right group boxes
        right_groupboxes_layout = QVBoxLayout()
        right_groupboxes_layout.addWidget(self.league_groupbox)
        right_groupboxes_layout.addWidget(self.sched_groupbox)
        right_groupboxes_layout.addWidget(self.news_groupbox)

        # Add group boxes to the main layout
        self.main_layout.addWidget(self.team_list_groupbox)
        self.main_layout.addLayout(right_groupboxes_layout)


        # Group box with title for team list
        self.font.setBold(True)
        self.team_list_groupbox.setFont(self.font)
        self.news_groupbox.setFont(self.font)
        self.sched_groupbox.setFont(self.font)
        self.league_groupbox.setFont(self.font)

        self.font.setBold(False)
        self.font.setFamily("Arial")
        self.exitBtn = QPushButton("Exit",self)
        self.left_layout.addWidget(self.exitBtn)


        # List of teams
        self.team_list.setFont(self.font)
        self.news_list.setFont(self.font)
        self.exitBtn.clicked.connect(self.close)
        self._createActions()
        self._createMenuBar()


     #####################################################################################
     ### We are done doing the housework, now it's time to do some App specific stuffs
     #####################################################################################

     ### Connect to the db to see if it's there.  Will be created if not there.
        #connection = sqlite3.connect("pyNFL.db")
        #cursor = connection.cursor()
        cursor.execute("""select count(*) from sqlite_master where type = 'table'
                          and name = 'nfl_status';""")
        result = cursor.fetchone()[0]
        if result == 0:    # table does not exist, so this is a new installation
            msg = QMessageBox()
            msg.setWindowTitle("pyNFL XOR Challenge")
            msg.setText("New Installation detected!")
            msg.setIcon(QMessageBox.Information)
            x = msg.exec_()
            CreateTables.create_all()
            msg = QMessageBox()
            msg.setWindowTitle("PyNFL XOR Challenge")
            msg.setText("Database initialized, make sure to customize the league!")
            msg.setIcon(QMessageBox.Information)
            x = msg.exec_()

   ###     Let's see what the status of the league is
        cursor.execute("""select state from nfl_status order by dt desc;""")
        result = cursor.fetchone()[0]
        if result == 'Initialize':
           self.news_list.addItem(QListWidgetItem("""Db Initialized, please customize teams."""))
           show_standings(self)
           #self.widget_two.titleList.addItem(QListWidgetItem('No League configured, please configure'))
        else:
           self.news_list.addItem(QListWidgetItem(result))
        cursor.close()


    def _createActions(self):
        # Creating action using the first constructor
        self.addAction = QAction(self)
        #self.addAction.setText("&New")
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



###  This looks up a schedule for team when clicked.
    def update_sched_list(self,item):
        selected_team = item.text()
        try:
           team = selected_team.split()[0].strip()
        except:
           team = None
        if team in ["NFC","AFC"]:
            team = None
        if team != None:   # Now we process and populate
          con = sqlite3.connect("pyNFL.db")
          cursor = con.cursor()
          self.sched_list.clear()
          cursor.execute(f"select team_id from teams where name = '{team}';")
          teamID = cursor.fetchone()[0]
          qry = f"""select week, home_team, away_team from schedule
                             where home_id = {teamID} or away_id = {teamID}
                             order by week;"""
          cursor.execute(qry)
          print(qry)
          sched = cursor.fetchall()
          for week in sched:
              wk,hteam,ateam = week
              if hteam == team:
                  sch = f"Week {wk}: {ateam}"
              else:
                  sch = f"Week {wk}: @ {hteam}"
                   
              self.sched_list.addItem(QListWidgetItem(sch))
          con.close()




    def _createMenuBar(self):
        self.layout = QHBoxLayout()
        menuBar = self.menuBar()
        menuBar.setNativeMenuBar(False)
        self.setMenuBar(menuBar)
        menuBar.setFont(self.font)
        
        #########################################################
        # Team Menu Options
        # Creating menus using a title
        # Menu: Games
        self.font.setPointSize(18)
        gamesMenu = menuBar.addMenu("Games")
        gamesMenu.setFont(self.font)

        # Menu: League ->  Write Team
        wrteamAct = QAction("Write Team", self)
        gamesMenu.addAction(wrteamAct)
        wrteamAct.triggered.connect(self.write_team)

        # Menu: League -> Write NFL Challenge games file
        wrmatchAct = QAction("Write NFL Challenge Weekly Schedule", self)
        gamesMenu.addAction(wrmatchAct)
        wrmatchAct.triggered.connect(self.write_match)

        # Menu: League -> Load Results
        wrsubldRes = QAction("Load Results", self)
        gamesMenu.addAction(wrsubldRes)
        wrsubldRes.triggered.connect(self.load_results)



     #################################################################

        # Menu: Roster
        rosterMenu = menuBar.addMenu("Roster")
        rosterMenu.setFont(self.font)

        # Menu: Roster -> View Rosters
        vwrosAct = QAction("View Rosters",self)
        rosterMenu.addAction(vwrosAct)
        vwrosAct.triggered.connect(self.view_roster)


#################################################################
        # Menu: Conferences
        #leagueMenu.addAction("Conferences")


        #divsubMenu = leagueMenu.addMenu("Divisions")
        #divsubMenu.setFont(self.font)

        #divsubMenu.addAction("Add Division")

        #divsubMenu.addAction("Edit Division")
        #divsubMenu.addAction("Delete Division")

 #################################################################
     # Menu:  GM/Owner
        gmoMenu = menuBar.addMenu("GM/Owner")
        gmoMenu.setFont(self.font)

        # Menu: GM/Owner -> Player
        playerSubMenu = gmoMenu.addMenu("Player")
        playerSubMenu.setFont(self.font)

        # Menu: GM/Owner -> Player - Cut Player
        cutplayerAct = QAction("Cut Player", self)
        playerSubMenu.addAction(cutplayerAct)
        cutplayerAct.triggered.connect(self.cut_player)

        # Menu: GM/Owner -> Player -> Sign Player
        playerSubMenu.addAction("Sign Player")

        # Menu: GM/Owner -> Player -> Coach
        coachSubMenu = gmoMenu.addMenu("Coach")
        coachSubMenu.setFont(self.font)

        # Menu: GM/Owner -> Coach -> Fire Coach
        coachSubMenu.addAction("Fire Coach")

        # Menu: GM/Owner -> Coach -> Hire Coach
        coachSubMenu.addAction("Hire Coach")

 #################################################################
        # Menu: Schedule
        schedMenu = menuBar.addMenu("Schedule")
        schedMenu.setFont(self.font)

        # Menu: Schedule -> View
        schedMenu.addAction("View")

        # Menu: Schedule -> Playoffs
        playoffSubMenu = schedMenu.addMenu("Playoffs")
        playoffSubMenu.setFont(self.font)

        # Menu: Schedule -> Playoffs -> Create Playoff Schedule
        playoffSubMenu.addAction("Create Playoff Schedule")

        # Menu: Schedule -> Playoffs -> View Playoff Schedule
        playoffSubMenu.addAction("View Playoff Schedule")

 #################################################################
        # Menu: Commissioner
        commMenu = menuBar.addMenu("Commissioner")
        commMenu.setFont(self.font)

        ##########################################################
        # Menu: Commissioner -> Alter League
        ##########################################################
        commAltersubMenu = commMenu.addMenu("Alter League")
        commAltersubMenu.setFont(self.font)

        # Menu: Commissioner -> Alter League -> Modify Conferences
        alterconfAct = QAction("Modify Conferences",self)
        commAltersubMenu.addAction(alterconfAct)
        alterconfAct.triggered.connect(self.view_conferences)
    
        # Menu: Commissioner -> Alter League -> Modify Divisions
        alterdivAct = QAction("Modify Divisions",self)
        commAltersubMenu.addAction(alterdivAct)
        alterdivAct.triggered.connect(self.view_divisions)

        # Menu: Commissioner -> Load Team
        ldteamAct = QAction("Load Team", self)
        commAltersubMenu.addAction(ldteamAct)
        ldteamAct.triggered.connect(self.load_team)
    
    
        # Menu: Commissioner -> Alter League -> Modify Teams
        alterTeamAct = QAction("Modify Teams",self)
        commAltersubMenu.addAction(alterTeamAct)
        alterTeamAct.triggered.connect(self.manage_teams)
        ##########################################################

        # Menu: Commissioner -> Modify Season
        commMenu.addAction("Modify Season")

        # Menu: Commissioner -> Modify Schedule
        commMenu.addAction("Modify Schedule")

 #################################################################
        # Menu: Off Season
        offMenu = menuBar.addMenu("&Off Season")
        offMenu.setFont(self.font)
   # Menu: Off Season -> Draft
        draftsubMenu = offMenu.addMenu("Draft")
        draftsubMenu.setFont(self.font)

        # Menu: Off Season -> Analyze Teams
        AnalyzeTeamAct = QAction("Analyze Teams", self)
        offMenu.addAction(AnalyzeTeamAct)
        AnalyzeTeamAct.triggered.connect(self.analyze_team)

        # Menu: Off Season -> Draft -> Create Draft Players
        CreateDraftAct = QAction("Create Draft Players", self)
        draftsubMenu.addAction(CreateDraftAct)
        CreateDraftAct.triggered.connect(self.create_draft)

        # Menu: Off Season -> Draft -> View Draft Players
        ViewDraftAct = QAction("View Draft Players", self)
        draftsubMenu.addAction(ViewDraftAct)
        ViewDraftAct.triggered.connect(self.view_draft)

        # Menu: Off Season -> Draft -> Edit Draft Players
        draftsubMenu.addAction("Edit Draft Players")

        # Menu: Off Season -> Retire Players
        RetirePlayersAct = QAction("Retire Players", self)
        offMenu.addAction(RetirePlayersAct)
        #RetirePlayersAct.triggered.connect(self.retire_players)

        # Menu: Off Season -> Training Camp
        TrainingCampAct = QAction("Training Camp", self)
        offMenu.addAction(TrainingCampAct)
        #TrainingCampAct.triggered.connect(self.training_camp)

        # Menu: Off Season -> Generate New Schedule
        CreateSchedAct = QAction("Create New Schedule", self)
        offMenu.addAction(CreateSchedAct)
        #CreateSchedAct.triggered.connect(self.create_sched)

  #################################################################
        # Menu:  Setup/Config
        setupMenu = menuBar.addMenu("&Setup/Config")
        setupMenu.setFont(self.font)

        # Menu:  Setup/Config -> Database
        CreateFAAct = QAction("Create Free Agents", self)
        setupMenu.addAction(CreateFAAct)
        CreateFAAct.triggered.connect(self.create_fa)

        #dbconnAct = QAction("DB Connection", self)
        #dbsubMenu.addAction(dbconnAct)
        #dbconnAct.triggered.connect(self.db_connection)

        # Menu: Setup/Config -> Database -> Create DB Objects
        CreateDbObjAct = QAction("Create DB Objects", self)
        setupMenu.addAction(CreateDbObjAct)
        #CreateDbObjAct.triggered.connect(self.create_db_obj)

        # Menu: Setup/Config -> Database -> Initialize Tables
        InitTblAct = QAction("Initialize DB Objects", self)
        setupMenu.addAction(InitTblAct)
        #InitTblAct.triggered.connect(self.init_tbls)

 #################################################################
        # Menu: Coaches
        setcoachsubMenu = setupMenu.addMenu("&Coaches")
        setcoachsubMenu.setFont(self.font)

        # Menu: Coaches -> Create Coach
        #setcoachsubMenu.addAction("Create Coach")
        crCoachAct = QAction("Create Coach", self)
        setcoachsubMenu.addAction(crCoachAct)
        crCoachAct.triggered.connect(self.create_coaches)
        # Menu: Coaches -> Edit Coach
        setcoachsubMenu.addAction("Edit Coach")

        # Menu: Coaches -> Delete Coach
        setcoachsubMenu.addAction("Delete Coach")
#################################################################
#################################################################

        helpMenu = menuBar.addMenu("&Help")
        helpMenu.setFont(self.font)
        ########  Check to see if nfl_status table exists, if it doesn't, this is a new installat


#########################################################################
    def processtrigger(self,q):
        print (q.text()+" is triggered")


    def edit_team(self):
        w = QDialog(self)
        config = get_db_config()
        conn = connect_to_postgres(config, attempts=3)

        #conv = MySQLConverter()
        w.resize(640,480)
        w.setWindowTitle("Edit Team")
        widget = QComboBox()
        conn.close()
        w.exec_()


    def write_team(self):
        w = QDialog(self)
        w.resize(640,480)
        w.setWindowTitle("Write Team")
        w.exec_()


    def write_match(self):
        #w = QDialog(self)
        #w.resize(640,480)
        #w.setWindowTitle("Write NFL Challenge Matchups")
        Write_Games()
        #w.exec_()

    def load_results(self):
        w = QDialog(self)
        w.resize(640,480)
        w.setWindowTitle("Load NFL Challenge Results")
        w.exec_()


    def load_team(self):
        Teams.Load_Team(self)

    def analyze_team(self):
        Teams.Analyze_Teams(self)

    def create_fa(self):
        FreeAgent.Create_Player_by_Pos(self)

    def create_draft(self):
        Draft.Create_Player_by_Pos(self)

    def view_draft(self):
        self.view_win = View_Draft()
        self.view_win.show()

    def view_conferences(self):
        self.view_win = View_Conferences()
        self.view_win.show()

    def view_divisions(self):
        self.view_win = View_Divisions()
        self.view_win.show()

    def manage_teams(self):
        self.view_win = Manage_Teams()
        self.view_win.show()

    def select_the_team(self):
        fname = QFileDialog.getOpenFileName(self,"Choose Team", " ","Roster Files (*.nfl)")
        if fname:
            self.lable_Team.setText(fname[0])
            self.LoadBtn.clicked.connect(lambda: Teams.LoadTeam(fname[0]))

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


 #   def conference(self):
 #       w = QDialog(self)
 #       w.resize(640,480)
 #       w.setWindowTitle("Conference")
 #       w.exec_()

 #   def add_division(self):
 #       w = QDialog(self)
 #       w.resize(640,480)
 #       w.setWindowTitle("Add Division")
 #       w.exec_()
#
#    def edit_division(self):
#        w = QDialog(self)
#        w.resize(640,480)
#        w.setWindowTitle("Edit Division")
#        w.exec_()
#
#    def delete_division(self):
#        w = QDialog(self)
#        w.resize(640,480)
#        w.setWindowTitle("Delete Division")
#        w.exec_()

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

    def create_coaches(self):
        self.window = QtWidgets.QMainWindow()
        self.ui = Ui_DbConfig()
        self.ui.setupUi(self.window)
        self.window.show()





def show_standings(self):
    #self.team_list.addItem(QListWidgetItem("""This is a team."""))
    self.team_list.clear()
    self.font = QFont()
    self.font.setPointSize(15)
    self.font.setFamily("Courier New")
    self.team_list.setFont(self.font)
    connection = sqlite3.connect("pyNFL.db")
    cursor = connection.cursor()
    cursor.execute("""select distinct division from standings""")
    result = cursor.fetchall()
    for Div in result:
       self.team_list.addItem(QListWidgetItem(Div[0]))
       cur2 = connection.cursor()
       cur2.execute(f"""select name,wins,losses from standings where division = '{Div[0]}'
                        order by rnk""")
       res2 = cur2.fetchall()
       for Team in res2:
          Tm = Team[0]
          Tm = Tm.rjust(15)
          Res = f"{Team[1]:>2} - {Team[2]:>2}"
          msg = f"{Tm:>15}  {Res}"
          self.team_list.addItem(QListWidgetItem(msg))
       self.team_list.addItem(QListWidgetItem(""))

       cur2.close()
    cursor.close()




if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyle("fusion")
    main = MainWindow()
    main.show()
    sys.exit(app.exec_())

