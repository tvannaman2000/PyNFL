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
                              QAction, 
                              QDialog, 
                              QListWidget, 
                              QListWidgetItem, 
                              QTextEdit, 
                              QWidget, 
                              QFileDialog, 
                              QLabel, 
                              QGroupBox,
                              )

class Teams():

    def LoadTeam(self):
       options = QFileDialog.Options()
       options |= QFileDialog.DontUseNativeDialog 
       fname, _ = QFileDialog.getOpenFileName(self,"Open Roster File","",
            "Roster Files (*.nfl)",options=options)
       if fname:
           Team = os.path.basename(fname)
           print(f"File: {fname} Team: {Team}") 
           qry = f"select team_id from teams where upper(name) = '{Team}';"
           connection = sqlite3.connect("pyNFL.db")
           cursor = connection.cursor()
           cursor.execute("""select count(*) from sqlite_master where type = 'table'
                          and name = 'nfl_status';""")
           Team_ID = cursor.fetchone()[0]

           ###  Now it's time to open the file and loop through it
           ####   "\x9b" is the hex code for cent sign in DOS

           fil = codecs.open(File_Team,"r",encoding="iso-8859-1")
           # skip first 3 lines
           inline = fil.readline()
           inline = fil.readline()
           inline = fil.readline()



