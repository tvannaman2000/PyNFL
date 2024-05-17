import os, sys, io, codecs, random
import sqlite3
import numpy as np
from statistics import stdev, mean, pstdev
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import (QApplication,
                              QMessageBox,
                              QDialog,
                              )


class Draft():
     def Get_Stats(Pos,Col):
         data = Draft.run_all_sql(f"select {Col} from active_players where posi = '{Pos}'")
         flat_list = [item[0] for item in data if item[0] is not None]
         std_dev = stdev(flat_list)
         ht_avg = mean(flat_list)
         return(round(ht_avg,2),round(std_dev,2))

     def Get_Stats3(Pos,Col):
         data = Draft.run_all_sql(f"select {Col} from active_players where posi = '{Pos}'")
         flat_list = [float(item[0]) for item in data if item[0] is not None]
         std_dev = stdev(flat_list) 
         ht_avg = mean(flat_list) 
         return(round(ht_avg,2),round(std_dev,2))
    
     def Get_Pos_Stdd(Pos):
         data = Draft.run_all_sql(f"""select a.poscnt from (select year, posi, count(*) as poscnt 
                              from combine_data group by 1,2) a where a.posi = '{Pos}';""")
         flat_list = [int(item[0]) for item in data if item[0] is not None]
         std_dev = stdev(flat_list) 
         return(round(std_dev,2))

     def run_sql(qry):
         conn = sqlite3.connect("pyNFL.db")
         cursor = conn.cursor()
         cursor.execute(qry)
         data = cursor.fetchone()
         cursor.close()
         conn.commit()
         conn.close()
         return(data)


     def run_all_sql(qry):
         conn = sqlite3.connect("pyNFL.db")
         cursor = conn.cursor()
         cursor.execute(qry)
         data = cursor.fetchall()
         cursor.close()
         conn.commit()
         conn.close()
         return(data)


     def get_name(MaxFRnk, MaxLRnk):
        skew_factor = 0.5
        rank = 5
        #Rnk = random.randint(1,MaxFrnk)
        Rnk = round((random.triangular(1, MaxFRnk, rank) ** skew_factor) * (rank - 1) + 1)
        fname = Draft.run_sql(f"""SELECT a.firstname FROM firstname a where a.rank = (select min(b.rank) from firstname b
                              where b.rank >= {Rnk}) ORDER BY rank limit 1;""")[0]
        #Rnk = random.randint(1,MaxLrnk)
        Rnk = round((random.triangular(1, MaxLRnk, rank) ** skew_factor) * (rank - 1) + 1)
        lname = Draft.run_sql(f"""SELECT a.lastname FROM surnames a where a.rank = (select min(b.rank) from surnames b
                              where b.rank >= {Rnk}) ORDER BY rank limit 1;""")[0]
        return(fname.title(),lname.title())



     def New_Num(pos,Avg,Std,Skill):
          probability = 0.04   # 1% of time
          NewNum = np.random.normal(Avg,Std,1).astype(int)[0]
          rnd_num = random.random()
          if rnd_num <= probability and Avg != 50:
              NewNum += 10
          if NewNum > 99:
              NewNum = 99
          return(NewNum)


     def Create_Player_by_Pos(self):
           MaxLRnk = Draft.run_sql("select max(rank) from surnames")[0]
           MaxFRnk = Draft.run_sql("select max(rank) from firstname")[0]
           Draft.run_sql("delete from draft_players")
           Player_List = []
           positions = Draft.run_all_sql("select distinct posi from active_players order by posi;")
           for pos in positions:
               pos = pos[0]
               AvgWt, StdWt = Draft.Get_Stats(pos,'wt')
               AvgHt, StdHt = Draft.Get_Stats(pos,'ht')
               AvgSpd, StdSpd = Draft.Get_Stats3(pos,'spd')
               AvgRush, StdRush = Draft.Get_Stats(pos,'rush')
               AvgBlk, StdBlk = Draft.Get_Stats(pos,'blk')
               AvgRcv, StdRcv = Draft.Get_Stats(pos,'rcv')
               AvgPass, StdPass = Draft.Get_Stats(pos,'pass')
               AvgKick, StdKick = Draft.Get_Stats(pos,'kick')
               #print(f"Pos: {pos}  Run: {AvgRush} - {StdRush}")
               
               StdPos = Draft.Get_Pos_Stdd(pos) 
               qry = f"""select avg(a.poscnt) from (select year, posi, count(*) as poscnt  
                       from combine_data group by 1,2) a where a.posi = '{pos}';"""
               AvgPos = round(Draft.run_sql(qry)[0],0)
               #print(f"Cnt: {AvgPos}   Std: {StdPos}")
               PosNo = np.random.normal(AvgPos,StdPos,1).astype(int)[0]
               print(f"Pos: {pos}: {PosNo}")
               #NewWt = np.random.normal(AvgWt,StdWt,1).astype(int)[0]
               if PosNo == 0:
                   PosNo = 1
               for i in range(0,PosNo):
                  fname, lname = Draft.get_name(MaxFRnk, MaxLRnk)
                  Name = fname + ' ' + lname
                  NewWt = np.random.normal(AvgWt,StdWt,1).astype(int)[0]
                  NewHt = np.random.normal(AvgHt,StdHt,1).astype(int)[0]
                  NewSpd = round(np.random.normal(AvgSpd,StdSpd,1).astype(float)[0]-0.05,2) 
                  NewBlk = Draft.New_Num(pos,AvgBlk,StdBlk,'Blk')
                  NewRush = Draft.New_Num(pos,AvgRush,StdRush,'Rush')
                  NewKick = Draft.New_Num(pos,AvgKick,StdKick,'Kick')
                  NewPass = Draft.New_Num(pos,AvgPass,StdPass,'Pass')
                  NewRcv = Draft.New_Num(pos,AvgRcv,StdRcv,'Rcv')
                  print(f"{pos} - {Name} Ht: {NewHt}  Wt: {NewWt}  Spd: {NewSpd}  Blk: {NewBlk}  Rn: {NewRush}  P: {NewPass}  Rc: {NewRcv}  K: {NewKick}")
                  qry = f"""insert into draft_players(name,posi,ht,wt,yrs,spd,rush,rcv,pass,kick,blk) values
                         ('{Name}','{pos}',{NewHt},{NewWt},0,{NewSpd},{NewRush},{NewRcv},{NewPass},{NewKick},{NewBlk})"""
                  Draft.run_sql(qry)
               print()
           msg = QMessageBox()
           msg.setWindowTitle("PyNFL XOR Challenge")
           msg.setText("Draft players created & loaded!")
           msg.setIcon(QMessageBox.Information)
           x = msg.exec_()




if __name__ == '__main__':
      Draft.Create_Player_by_Pos()
