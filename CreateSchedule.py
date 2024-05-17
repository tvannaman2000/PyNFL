import sys,os
import sqlite3
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




class Schedule:
    def __init__(self):
       pass

    def load_template(name):
         conn = sqlite3.connect("pyNFL.db")
         cursor = conn.cursor()
         cursor.execute(f"""select no_teams,no_divisions,no_games from sched_template where sched_name = '{name}'""")
         result = cursor.fetchall()
         for Data in result:
             noTeams, noDivs, noGames = Data
         return noTeams,noDivs,noGames
             
    def make_sched(name):
         conn = sqlite3.connect("pyNFL.db")
         cursor = conn.cursor()
         cursor.execute("delete from schedule")
         cursor.execute(f"""insert into schedule SELECT d.season,
                                   a.week,
                                   b.name,
                                   b.team_id,
                                   c.name,
                                   c.team_id
                              FROM sched_detail a,
                                   teams b,
                                   teams c,
                                   nfl d
                             WHERE a.sched_name = '{name}' AND 
                                   b.div_code = a.hdiv AND 
                                   c.div_code = a.vdiv AND 
                                   b.last_finish = a.hfin AND 
                                   c.last_finish = a.vfin AND
                                   d.season = (select max(season) from nfl)
                             ORDER BY a.week""")
        

       

     
   



#### Start here ######
######################
if __name__ == '__main__':    
#    app = QApplication(sys.argv)
#    app.setStyle("fusion")    
#    main = MainWindow()       
#    main.show()               
#    sys.exit(app.exec_())    
    noTeams, noDivs, noGames = Schedule.load_template('1980A')
    Schedule.make_sched('1980A')
