import sys,os,time
import pandas as pd
import numpy as np
import sqlite3
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

class Draft():

    def Get_Ht_Stats(Pos):
        data = run_all_sql(f"select round(avg(ht))::integer, round(stddev(ht))::integer from combine_data where position = '{Pos}'")
        for x in data:
           return(x[0],x[1])

    def Get_Wt_Stats(Pos):
        data = run_all_sql(f"select round(avg(wt))::integer, round(stddev(wt))::integer from combine_data where position = '{Pos}'")
        for x in data:
           return(x[0],x[1])

    def Get_40_Stats(Pos):
        data = run_all_sql(f"select avg(forty)::numeric(3,2), stddev(forty)::numeric(3,2) from combine_data where position = '{Pos}'")
        for x in data:
           return(x[0],x[1])



    def player_by_pos():
        Player_List = []
        positions = Draft.run_all_sql("select distinct posi from combine_data order by posi")
        for pos in positions:
            pos = pos[0]
            AvgWt, StdWt = Draft.Get_Wt_Stats(pos)
            AvgHt, StdHt = Draft.Get_Ht_Stats(pos)
            AvgSpd, StdSpd = Draft.Get_40_Stats(pos)
            #print(AvgSpd, StdSpd)
            qry = f"select avg(a.poscnt), stddev(a.poscnt) from (select year, position, count(*) as poscnt  \
                    from combine_data group by 1,2) a where a.position = '{pos}';"
            row = run_sql(qry)
            poscnt = row[0]
            posdev = row[1]






   def run_all_sql(qry):
      conn = sqlite3.connect("PyNFL.db")
      cur = conn.cursor()
      cur.execute(qry)
      row = cur.fetchall()
      cur.close()
      conn.close()
      return(row)

   def run_sql(qry):
      conn = sqlite3.connect("PyNFL.db")
      cur = conn.cursor()
      cur.execute(qry)
      row = cur.fetchone()
      cur.close()
      conn.close()
      return(row)

