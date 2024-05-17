import os, sys, io, codecs
import sqlite3
from PyQt5.QtWidgets import QMessageBox, QFileDialog,QListWidgetItem, QListWidget



class Teams():

   ###  This loops thru the .nfl file and extracts the starters into a list
   def get_starters(fil):
      starters = []
      for inline in fil:
          inline = inline.strip()
          if inline == 'Offense:':
              break
          if inline != 'STARTERS':
             strtpos, strtno = inline.split()
             starters.append((strtpos,strtno))
      return(starters)


   ###  This converts the imperial 6'4" designation into inches
   def to_inches(ht):
      ht = ht.strip("\"")
      info = ht.split("\'")
      feet = int(info[0]) * 12
      inches = int(info[1])
      return(feet + inches)


   def read_player_info(fil):
       player_info = []

       #inline = fil.readline()
       for inline in fil:
          if not inline.strip():
             break
          info = inline.strip().split("  ")
          i = 0
          jersey = info[i]
          posi = info[i+1]
          posi = posi.strip(" ")
          if posi in ('K','P','C'):
            i += 1  
          ht = Teams.to_inches(info[i+2])
          wt = info[i+3]
          yrs = info[i+4]
          spd = info[i+5]
          run = info[i+6]
          rcv = info[i+7]
          blk = info[i+8]
          throw = info[i+9]
          kick = info[i+10]
          name = info[i+11]
          name = name.replace("'","''")
          player_info.append((name,jersey,posi,ht,wt,yrs,spd,run,rcv,blk,throw,kick))
       return player_info

     
   def Load_Team(self):
       options = QFileDialog.Options()
       options |= QFileDialog.DontUseNativeDialog
       fname, _ = QFileDialog.getOpenFileName(self,"Open Roster File","",
            "Roster Files (*.nfl)",options=options)
       if fname:
          Team = os.path.basename(fname)
          Team = Team.capitalize()
          Team = Team.removesuffix(".nfl")
          #print(f"File: {fname} Team: {Team}")
          conn = sqlite3.connect("pyNFL.db")
          cursor = conn.cursor()
          qry = f"select team_id from teams where name = '{Team}';"
          #print(qry)
          cursor.execute(qry)
          Team_ID = cursor.fetchone()[0]
   
          #print(f"Team: {Team}   ID: {Team_ID}")
   
          ###  Now it's time to open the file and loop through it
          ####   "\x9b" is the hex code for cent sign in DOS
   
          fil = codecs.open(fname,"r",encoding="iso-8859-1")
          # skip first 3 lines
          inline = fil.readline()
          inline = fil.readline()
          inline = fil.readline()
          cursor.execute("begin transaction")
   
          ### Read the roster and add to active_players table
          player_info = Teams.read_player_info(fil)
          for p in player_info:
              qry = f"""insert into active_players(name,jersey_no,posi,ht,wt,yrs,spd,rush,rcv,blk,pass,kick,team_id,team) 
                        values ('{p[0]}',{p[1]},'{p[2]}',{p[3]},{p[4]},{p[5]},{p[6]},{p[7]},{p[8]},{p[9]},
                                {p[10]},{p[11]},{Team_ID},'{Team}')"""
                             
              cursor.execute(qry)
              #print(f"Adding {p[0]}")
   
          ### Read the starters and insert into starters table
          starters = Teams.get_starters(fil)
          for starter in starters:
             startpos, startno = starter
             qry = f"select player_id from active_players where team_id = {Team_ID} and jersey_no = {startno}"
             cursor.execute(qry)
             Player_ID = cursor.fetchone()[0]
             qry = f"insert into starters values ({Player_ID},{Team_ID},{startno},'{startpos}');"
             cursor.execute(qry)
             #print(Player_ID,startpos, startno)
   
          ##  Time to extract the coaching profiles
      #    inline = fil.readline()  # This should be the "Offense:" line
          offense = fil.readline()  # This should be the offensive profile
          offense = offense.strip()
   
          #print(f"Offense: {offense}")
          inline = fil.readline()  # This should be the "Defense:" line
          defense = fil.readline()  # This should be the defensive profile
          defense = defense.strip()
          qry = f"update teams set offense = '{offense}', defense = '{defense}' where team_id = {Team_ID};"
          #print(qry)
          cursor.execute(qry)
          cursor.close()
          conn.commit()
          conn.close()
          msg = QMessageBox()
          msg.setWindowTitle("PyNFL XOR Challenge")
          msg.setText("Team Loaded!")
          msg.setIcon(QMessageBox.Information)
          x = msg.exec_()


#############################################################
##  This averages out all team skill levels and allows the AI to identify team strengths and weaknesses
#############################################################

   def Analyze_Teams(self):

          conn = sqlite3.connect("pyNFL.db")
          cursor = conn.cursor()
        #### basically truncate the table.
          qry = "delete from team_analyzed;"
          cursor.execute(qry)
        ###  Now it's time to insert the data
          qry = """insert into team_analyzed (team,posi,blkavg,runavg,rcvavg,passavg,kickavg,avgplayer)
                    select team, posi, 
                           round(avg(blk)), 
                           round(avg(rush)),
                           round(avg(rcv)), 
                           round(avg(pass)), 
                           round(avg(kick)) ,
                           round(avg(blk) + avg(rush) + avg(rcv) + avg(pass) + avg(kick)) as avg_player
                    from active_players 
                    group by team, posi; """
          cursor.execute(qry)
        ###  Now it's time to rank the teams
          qry = """WITH ranked_players AS (
                             SELECT
                                 team,
                                 posi,
                                 avgplayer,
                                 rank() OVER (PARTITION BY posi ORDER BY avgplayer DESC) AS rn
                             FROM
                                 team_analyzed
                         )
                         UPDATE team_analyzed
                         SET rank = (
                             SELECT rn
                             FROM ranked_players
                             WHERE ranked_players.team = team_analyzed.team
                               AND ranked_players.posi = team_analyzed.posi
                               AND ranked_players.avgplayer = team_analyzed.avgplayer);"""
          cursor.execute(qry)
       ####  Time to loop thru each team and update draft needs
          qry = "select distinct team from team_analyzed;"
          c2 = conn.cursor()
          cursor.execute(qry)
          Teams = cursor.fetchall()
          for Team in Teams:
             qry2 = f"""WITH ranked_teams AS (
                                SELECT
                                    team,
                                    posi,
                                    rank,
                                    RANK() OVER (ORDER BY rank DESC) AS NeedRnk
                                FROM
                                    team_analyzed
                                WHERE
                                    team = '{Team[0]}'  -- Specify the team for which you want to calculate the need rank
                            )
                            UPDATE
                                team_analyzed
                            SET
                                NeedRnk = (
                                    SELECT
                                        rt.NeedRnk
                                    FROM
                                        ranked_teams AS rt
                                    WHERE
                                        rt.team = team_analyzed.team
                                        AND rt.posi = team_analyzed.posi
                                        AND rt.rank = team_analyzed.rank
                                )
                            WHERE
                                team = '{Team[0]}';"""
             c2.execute(qry2)
          c2.close()
          self.news_list.clear()
          self.news_list.addItem(QListWidgetItem("""Top Draft Needs in the PyNFL"""))
          qry = """select team, posi from team_analyzed where needrnk = 1 order by team;"""
          cursor.execute(qry)
          Needs = cursor.fetchall()
          for i in Needs:
             Need = f"{i[0]}: {i[1]}"
             self.news_list.addItem(QListWidgetItem(Need))

         ####  Now its time to document roster configuration
          qry = "delete from roster_specs;"
          cursor.execute(qry)

          qry = """insert into roster_specs select posi, max(cnt), min(cnt), round(avg(cnt)) from 
                    (select posi, count(*) as cnt from active_players group by team, posi) a group by posi;"""
          cursor.execute(qry)

          cursor.close()
          conn.commit()
          conn.close()

          msg = QMessageBox()
          msg.setWindowTitle("PyNFL XOR Challenge")
          msg.setText("Analyze Teams Complete!")
          msg.setIcon(QMessageBox.Information)
          x = msg.exec_()


if __name__ == '__main__':
    Load_Team("Cowboys.nfl")
