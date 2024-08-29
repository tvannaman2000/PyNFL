import sys
import sqlite3
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QFontMetrics
from PyQt5.QtWidgets import (QApplication, 
                             QMainWindow, 
                             QPushButton, 
                             QVBoxLayout, 
                             QMessageBox,
                             QHBoxLayout, 
                             QWidget, 
                             QTableView,
                             )
from PyQt5.QtSql import QSqlDatabase, QSqlTableModel, QSqlQuery

class Write_Teams(QMainWindow):
    def __init__(self):
        super().__init__()

    def Write_Team(self):
       Team = 'fred' 




class Write_Games(QMainWindow):
    def __init__(self):
        super().__init__()
     
        #QMainWindow().__init__(self,parent)
        #self.parent = parent
        self.setWindowTitle("pyNFL Write season.nfl file")
        self.setFont(QFont('Arial',16))
        self.resize(382, 350)


        # Create database connection
        conn = sqlite3.connect("pyNFL.db")
        cursor = conn.cursor()
        cursor.execute("""select season, week, state from nfl_status order by dt desc;""")
        row = cursor.fetchone()
        yr,wk,state = row
        
        if state != 'write':
            wk += 1

        cursor.execute(f"select count(*) from schedule where season = {yr} and week = {wk};")
        row = cursor.fetchone()
        gms = row[0]
        f = open("/Users/timvannaman/dosgames/nfl/SEASON2.NFL","w")
        f.write(f"{gms}\n")
        cursor.execute(f"select home_team, away_team from schedule where season = {yr} and week = {wk};")
        row = cursor.fetchall()
        for Home, Away in row:
            f.write(f"{Home} {Away}\n") 
        f.close()
        msg = QMessageBox()
        msg.setWindowTitle("Write Games")
        msg.setText(f"Schedule for week #{wk} written")
        msg.setIcon(QMessageBox.Information)
        msg.exec_()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("fusion")
    window = Write_Games()
    window.show()
    sys.exit(app.exec_())

