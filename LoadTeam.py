import os,codecs,sys,io
import xml.etree.ElementTree as ET
from mysql.connector.conversion import MySQLConverter
from myconn import connect_to_mysql
from PyQt5.QtWidgets import QMessageBox


cfg_file = "dbconfig.xml"


#####################
#####  Start here
#####################

def LoadTeam(Team_File):

   print(Team_File)
   Team = os.path.basename(Team_File)
   
   msg = QMessageBox()
   File_Team = Team
   Team = Team.removesuffix(".nfl")
   Player_id = 0

   ##  Load code to read XML file containing credentials
   tree = ET.parse(cfg_file)
   root = tree.getroot()
   for x in root[0]:
       if x.tag == "hostname":
              hostname = x.text
       if x.tag == "password":
              password = x.text
       if x.tag == "username":
              username = x.text
       if x.tag == "dbname":
              dbname = x.text
   config = { "host": hostname, "user": username, "password": password, "database": dbname, }
   conn = connect_to_mysql(config, attempts=3)
   conv = MySQLConverter()
   Team_id = i = 0
   sql_stmt = "select team_id from teams where name = '" + Team + "';"
   if conn and conn.is_connected(): 
       with conn.cursor() as cursor:
           cursor.execute(sql_stmt,(Team_id))
           rows = cursor.fetchall()
           for rows in rows:
              Team_id = rows[0]
              #print("Team ID: ", Team_id)
   else:
       msg.setText("Could not connect to MySQL")
       #print("Could not connect to MySQL")
   cursor.close()

   ###  Now it's time to open the file and loop through it
   ####   "\x9b" is the hex code for cent sign in DOS

   fil = codecs.open(File_Team,"r",encoding="iso-8859-1")
   # skip first 3 lines
   inline = fil.readline()
   inline = fil.readline()
   inline = fil.readline()
   
   # Loop thru 49 players
   for i in range(49):
      inline = fil.readline()
      inline = inline.replace('\n', '')
      nbr = inline[3:5]
      posi = inline[7:9]
      height = inline[12:17]
      height = conv.escape(height)
      weight = inline[19:22]
      years = inline[24:26]
      speed = inline[28:31]
      run = inline[33:35]
      rcv = inline[38:40]
      blk = inline[43:45]
      pas = inline[48:50]
      kick = inline[53:55]
      name = inline[58:len(inline)-1]
      name = conv.escape(name)    # Some names have ' in them
      #print ("Num: [%s] Pos: [%s] Wgt: [%s] Spd: [%s] " % (nbr,posi,weight,speed), run, rcv, blk, pas,name)
      sql_stmt = f"insert into active_players2 (yrs,team_Id,jersey_no,name,posi,ht,wt,spd,rush,rcv,blk,pass,kick,team) values ({years},{Team_id},{nbr},'{name}','{posi}','{height}',{weight},{speed},{run},{rcv},{blk},{pas},{kick},'{Team}');"
      #print(sql_stmt)
      mycur = conn.cursor()
      mycur.execute(sql_stmt)
      conn.commit()
      if mycur.rowcount != 1:
        msg.setText("Error inserting into nfl.active_players")
        #print("Error inserting into active_players")
      mycur.close()

   ###   Read 2 more lines to get to starters
   inline = fil.readline()
   inline = fil.readline()
   for i in range(32):
      inline = fil.readline()
      inline = inline.replace('\n', '')
      Pos_Start = inline[0:4].replace(' ','')
      St_Num = inline[6:8]
      
      mycur = conn.cursor()
      Player_id = 0
      sql_stmt = f"select player_id from active_players2 where jersey_no = {St_Num} and team_id ={Team_id};"
      mycur.execute(sql_stmt,(Player_id))
      rows = mycur.fetchall()
      for row in rows:
         Player_id = row[0]
         #print("ID: ", Player_id, "Start: ", Pos_Start, "Num: ",St_Num)
      mycur.close()

      upcur = conn.cursor()
      upcur.execute("set names utf8mb4;")
      upcur.execute("set character set utf8mb4;")
      upcur.execute("set character_set_connection=utf8mb4;")
      sql_stmt = f"insert into starters2 values({Player_id},{Team_id},{St_Num},'{Pos_Start}');"
      #print(sql_stmt)
      upcur.execute(sql_stmt)
      if upcur.rowcount != 1:
        msg.setText("Error inserting into nfl.starters")
        #print("Error inserting into starters")
      upcur.close()
   conn.commit()

   fil.close()
   conn.close()
   msg.setText("Team Loaded")

