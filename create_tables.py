import sys, codecs, io, os.path
import xml.etree.ElementTree as ET
import pandas as pd
import csv
from io import StringIO
import sqlite3


class CreateTables(): 
    def create_all():
        CreateTables.create_status()
        CreateTables.create_conference()
        CreateTables.create_divisions()
        CreateTables.create_coaching_styles()
        CreateTables.create_teams()
        CreateTables.create_active_players()
        CreateTables.create_coaches()
        CreateTables.create_draft_players()
        CreateTables.create_fa_players()
        CreateTables.create_stg_firstnames()
        CreateTables.create_firstname()
        CreateTables.create_interceptions()
        CreateTables.create_surnames()
        CreateTables.create_nfl()
        CreateTables.create_passing()
        CreateTables.create_player_history()
        CreateTables.create_playoffs()
        CreateTables.create_punt_returns()
        CreateTables.create_rankings()
        CreateTables.create_receiving()
        CreateTables.create_game_results()
        CreateTables.create_results_history()
        CreateTables.create_ranking_formulas()
        CreateTables.create_rushing()
        CreateTables.create_sacks()
        CreateTables.create_standings()
        CreateTables.create_sched_template()
        CreateTables.create_standings_history()
        CreateTables.create_starters()
        CreateTables.create_team_stats()
        CreateTables.create_roster_specs()
        CreateTables.create_team_analyzed()
        CreateTables.create_tmp_standings()
        CreateTables.create_combine_data()

    def create_active_players():
        qry = """create table if not exists active_players (
                         player_id integer NOT NULL primary key autoincrement,
                         jersey_no integer NOT NULL,
                         name varchar(40) NOT NULL,
                         posi varchar(2) ,
                         ht integer NOT NULL,
                         wt integer NOT NULL,
                         yrs integer NOT NULL,
                         spd numeric(3,1) ,
                         rush integer NOT NULL,
                         rcv integer NOT NULL,
                         pass integer NOT NULL,
                         kick integer NOT NULL,
                         starter varchar(4) ,
                         team_id integer NOT NULL,
                         team varchar(20) ,
                         blk integer NOT NULL,
                         kr char(1) ,
                         pr char(1) ,
                         active char(1) DEFAULT 'Y',
                         FOREIGN KEY (team_id)
                             REFERENCES teams (team_id) 
                             ON UPDATE NO ACTION
                             ON DELETE NO ACTION
                      );"""
        CreateTables.execute_qry(qry)

    def create_status():
        qry = """create table if not exists nfl_status (
                            season integer,
                            week integer,
                            state varchar(15),
                            dt timestamp default current_timestamp not null);"""
        CreateTables.execute_qry(qry)
        qry = """insert into nfl_status(season,week,state) values (0,0,'Initialize')"""
        CreateTables.execute_qry(qry)


    def create_conference():
        qry = """create table if not exists conference (
                            conf_code varchar(5) NOT NULL primary key,
                            conf_name varchar(50),
                            conf_abbr varchar(5));"""
        CreateTables.execute_qry(qry)
        qry = "insert into conference values ('AFC','American Football Conference','afc')"
        CreateTables.execute_qry(qry)
        qry = "insert into conference values ('NFC','National Football Conference','nfc')"
        CreateTables.execute_qry(qry)

    def create_divisions():
        qry = """create table if not exists divisions (
                            div_code varchar(5) NOT NULL primary key,
                            div_name varchar(25),
                            conf_code varchar(5),
                            foreign key (conf_code)
                               references conference(conf_code)
                                  on delete cascade
                                  on update cascade);"""
        CreateTables.execute_qry(qry)
        qry = "insert into divisions values ('ae','AFC East','afc')"
        CreateTables.execute_qry(qry)
        qry = "insert into divisions values ('ac','AFC Central','afc')"
        CreateTables.execute_qry(qry)
        qry = "insert into divisions values ('aw','AFC West','afc')"
        CreateTables.execute_qry(qry)
        qry = "insert into divisions values ('ne','NFC East','nfc')"
        CreateTables.execute_qry(qry)
        qry = "insert into divisions values ('nc','NFC Central','nfc')"
        CreateTables.execute_qry(qry)
        qry = "insert into divisions values ('nw','NFC West','nfc')"
        CreateTables.execute_qry(qry)


    def create_coaching_styles():
        qry = """create table if not exists coaching_style (
                       coaching_style varchar(15) not null primary key);"""
        CreateTables.execute_qry(qry)
        qry = "insert into coaching_style values ('Aggressive')"
        CreateTables.execute_qry(qry)
        qry = "insert into coaching_style values ('Balanced')"
        CreateTables.execute_qry(qry)
        qry = "insert into coaching_style values ('Conservative')"
        CreateTables.execute_qry(qry)

    def create_coaches():
        qry = """create table if not exists coaches (
                        coach_id integer primary key autoincrement,
                        name varchar(30) NOT NULL,
                        isactive char(1) DEFAULT 'Y',
                        team varchar(35) DEFAULT NULL,
                        wins integer DEFAULT 0,
                        losses integer DEFAULT 0,
                        winpct numeric(5,1) DEFAULT 0.0,
                        offense varchar(15) DEFAULT NULL,
                        defense varchar(15) DEFAULT NULL,
                        age integer,
                        foreign key (offense)
                            references coaching_style(coaching_style)
                               on delete set null
                               on update cascade,
                        foreign key (defense)
                            references coaching_style(coaching_style)
                               on delete set null
                               on update cascade
                               );"""
        CreateTables.execute_qry(qry)

        CreateTables.execute_qry(qry)

    def create_draft_players():
        qry = """create table if not exists draft_players (
                           player_id integer primary key autoincrement,
                           name varchar(40) NOT NULL,
                           posi varchar(2) NOT NULL,
                           ht varchar(6) NOT NULL,
                           wt integer NOT NULL,
                           yrs integer NOT NULL,
                           spd numeric(3,1),
                           rush integer NOT NULL,
                           rcv integer NOT NULL,
                           pass integer NOT NULL,
                           kick integer NOT NULL,
                           blk integer NOT NULL);"""
        CreateTables.execute_qry(qry)
                          

    def create_fa_players():
        qry = """create table if not exists free_agents (
                           player_id integer primary key autoincrement,
                           name varchar(40) NOT NULL,
                           posi varchar(2) NOT NULL,
                           ht varchar(6) NOT NULL,
                           wt integer NOT NULL,
                           yrs integer NOT NULL,
                           spd numeric(3,1) not null,
                           rush integer NOT NULL,
                           rcv integer NOT NULL,
                           pass integer NOT NULL,
                           kick integer NOT NULL,
                           blk integer NOT NULL);"""
        CreateTables.execute_qry(qry)

    def create_firstname():
        qry = """create table if not exists firstname (
                      firstname varchar(50) NOT NULL primary key ,
                      rank integer NOT NULL);"""
        CreateTables.execute_qry(qry)
        qry = """insert into firstname SELECT firstname, RANK() OVER (ORDER BY SUM(occurances) DESC) AS rank 
FROM stg_firstnames GROUP BY firstname;"""
        CreateTables.execute_qry(qry)

    def create_stg_firstnames():
        qry = """create table if not exists stg_firstnames (
                      firstname varchar(50) NOT NULL ,
                      occurances integer NOT NULL);"""
        CreateTables.execute_qry(qry)
        conn = sqlite3.connect("pyNFL.db")
        cursor = conn.cursor()
        with open('firstnames.csv') as csvfile:
          csvFile = csv.reader(csvfile)
          for lines in csvFile:
            cursor.execute(f"insert into stg_firstnames values ('{lines[0]}',{lines[1]});")
        cursor.close()
        conn.commit()



    def create_interceptions():
        qry = """create table if not exists interceptions (
                    season integer NOT NULL,
                    week integer NOT NULL,
                    player_id integer NOT NULL,
                    team_id integer NOT NULL,
                    cnt integer,
                    yards integer,
                    tds integer,
                    longest integer,
                    average numeric(4,1) ,
                    opp_team_id integer NOT NULL,
                    foreign key (player_id)
                       references active_players(player_team_id)
                       on delete cascade
                       on update cascade,
                    foreign key (team_id)
                       references teams(team_id)
                       on delete cascade
                       on update cascade,
                    foreign key (opp_team_id)
                       references teams(team_id)
                       on delete cascade
                       on update cascade
                    primary key (season,week,player_id));"""
        CreateTables.execute_qry(qry)

    def create_standings():
        qry = """create table if not exists standings (
                                team_id integer NOT NULL primary key,
                                name varchar(20) ,
                                division varchar(25),
                                wins integer not null default (0) ,
                                losses integer not null default (0) ,
                                div_wins integer not null default (0) ,
                                div_losses integer not null default (0) ,
                                conf_wins integer not null default (0) ,
                                conf_losses integer not null default (0) ,
                                rnk integer not null default (0) 
                            );"""
        CreateTables.execute_qry(qry)
        qry = """ insert into standings(team_id, name, division) select a.team_id, a.name, b.div_name 
                  from teams a, divisions b where a.div_code = b.div_code;"""
        CreateTables.execute_qry(qry)

    def create_surnames():
        qry = """create table if not exists surnames (
                      lastname varchar(75) NOT NULL primary key,
                      rank integer NOT NULL);"""
        CreateTables.execute_qry(qry)
          ###  Load surname metadata into the table.  
        conn = sqlite3.connect("pyNFL.db")
        cursor = conn.cursor()
        with open('surnames.csv') as csvfile:
          csvFile = csv.reader(csvfile)
          for lines in csvFile:
            cursor.execute(f"insert into surnames values ('{lines[0]}',{lines[1]});")
        cursor.close()
        conn.commit()
        conn.close()




    def create_nfl():
        qry = """create table if not exists nfl (
                      season integer NOT NULL primary key,
                      sched_type integer not null,
                      complete char(1),
                      teams integer not null,
                      weeks integer not null);"""
        CreateTables.execute_qry(qry)

       

    def create_passing():
        qry = """create table if not exists passing (
                         season integer NOT NULL,
                         week integer,
                         player_id integer NOT NULL,
                         team_id integer NOT NULL,
                         attempts integer,
                         complete integer,
                         yards integer,
                         tds integer,
                         intercepts integer,
                         lg integer,
                         opp_team_id integer,
                         foreign key (team_id)
                            references teams(team_id)
                            on delete cascade
                            on update cascade,
                         foreign key (player_id)
                            references active_players(player_id)
                            on delete cascade
                            on update cascade,
                         PRIMARY KEY (player_id, team_id));"""
        CreateTables.execute_qry(qry)

    def create_player_history():
        qry = """create table if not exists player_history (
                     player_id integer NOT NULL,
                     jersey_no integer NOT NULL,
                     name varchar(75) NOT NULL,
                     posi varchar(2) ,
                     ht integer NOT NULL,
                     wt integer NOT NULL,
                     yrs integer NOT NULL,
                     spd numeric(3,1),
                     rush integer NOT NULL,
                     rcv integer NOT NULL,
                     pass integer NOT NULL,
                     kick integer NOT NULL,
                     kr char(1) ,
                     pr char(1),
                     starter varchar(4),
                     team_id integer NOT NULL,
                     team varchar(20),
                     blk integer NOT NULL,
                     active char(1) DEFAULT 'Y',
                     year integer,
                     primary key (player_id, team_id));"""
        CreateTables.execute_qry(qry)


    def create_playoffs():
        qry = """create table if not exists playoffs (
                     div_name varchar(15) NOT NULL,
                     team varchar(20) NOT NULL,
                     wins integer NOT NULL,
                     div_wins integer NOT NULL,
                     conf_wins integer NOT NULL,
                     div_winner char(1) ,
                     bye char(1) ,
                     seed integer,
                     week integer,
                     season integer); """
        CreateTables.execute_qry(qry)


    def create_punt_returns():
        qry = """create table if not exists punt_returns (
                         season integer NOT NULL,
                         week integer NOT NULL,
                         player_id integer NOT NULL,
                         team_id integer NOT NULL,
                         cnt integer,
                         yards integer,
                         avg numeric(5,1),
                         lg integer,
                         tds integer,
                         opp_team_id integer,
                         foreign key (team_id)
                            references teams(team_id)
                            on delete cascade
                            on update cascade,
                         foreign key (player_id)
                            references active_players(player_id)
                            on delete cascade
                            on update cascade);"""
        CreateTables.execute_qry(qry)


    def create_rankings():
        qry = """create table if not exists rankings (
                      year integer NOT NULL,
                 team varchar(45) NOT NULL,
                 category varchar(45) NOT NULL,
                 value integer NOT NULL,
                 rnk integer NOT NULL); """
        CreateTables.execute_qry(qry)


    def create_ranking_formulas():
        qry = """create table if not exists ranking_formulas (
                      posi char(2) NOT NULL primary key,
                        ht numeric(4,3) NOT NULL,
                        wt numeric(4,3) NOT NULL,
                       spd numeric(4,3) not null,
                      rush numeric(4,3) NOT NULL,
                       rcv numeric(4,3) NOT NULL,
                      blk numeric(4,3) NOT NULL,
                      pass numeric(4,3) NOT NULL,
                       kick numeric(4,3) NOT NULL); """
        CreateTables.execute_qry(qry)
        qry = """insert into ranking_formulas values ('QB',0.1,0.05,0.05,0.3,0.01,0.001,0.65,0.001)"""
        CreateTables.execute_qry(qry)
        qry = """insert into ranking_formulas values ('K',0.1,0.05,0.05,0.5,0.01,0.001,0.1,0.9)"""
        CreateTables.execute_qry(qry)
        qry = """insert into ranking_formulas values ('P',0.1,0.05,0.05,0.5,0.01,0.001,0.1,0.9)"""
        CreateTables.execute_qry(qry)
        qry = """insert into ranking_formulas values ('RB',0.1,0.1,0.5,0.75,0.55,0.5,0,0)"""
        CreateTables.execute_qry(qry)
        qry = """insert into ranking_formulas values ('TE',0.3,0.3,0.5,0.55,0.75,0.6,0,0)"""
        CreateTables.execute_qry(qry)
        qry = """insert into ranking_formulas values ('WR',0.3,0.1,0.5,0.55,0.75,0.45,0,0)"""
        CreateTables.execute_qry(qry)
        qry = """insert into ranking_formulas values ('C',0.3,0.1,0.5,0.55,0.75,0.45,0,0)"""
        CreateTables.execute_qry(qry)
        qry = """insert into ranking_formulas values ('OL',0.3,0.1,0.5,0.55,0.75,0.45,0,0)"""
        CreateTables.execute_qry(qry)
        qry = """insert into ranking_formulas values ('DL',0.3,0.1,0.5,0.00,0.00,0.70 ,0  ,0)"""
        CreateTables.execute_qry(qry)
        qry = """insert into ranking_formulas values ('LB',0.3,0.2,0.5,0.60,0.50,0.50 ,0  ,0)"""
        CreateTables.execute_qry(qry)
        qry = """insert into ranking_formulas values ('DB',0.3,0.2,0.5,0.60,0.50,0.50 ,0  ,0)"""
        CreateTables.execute_qry(qry)

    def create_receiving():
        qry = """create table if not exists receiving (
                       season integer NOT NULL,
                       week integer NOT NULL,
                       player_id integer NOT NULL,
                       team_id integer NOT NULL,
                       cnt integer,
                       yards integer,
                       average numeric(5,1) ,
                       lg integer,
                       tds integer,
                       opp_team_id integer,
                         foreign key (team_id)
                            references teams(team_id)
                            on delete cascade
                            on update cascade,
                         foreign key (player_id)
                            references active_players(player_id)
                            on delete cascade
                            on update cascade);"""
        CreateTables.execute_qry(qry)

    def create_game_results():
        qry = """create table if not exists game_results (
                          season integer NOT NULL,
                          week integer NOT NULL,
                          home_team integer NOT NULL,
                          away_team integer NOT NULL,
                          home_score integer NOT NULL,
                          away_score integer NOT NULL,
                          winner integer NOT NULL,
                          loser integer NOT NULL,
                          foreign key (away_team)
                             references teams(team_id)
                                  on delete cascade
                                  on update cascade,
                          FOREIGN KEY (home_team)
                              REFERENCES teams (team_id)
                                  ON UPDATE NO ACTION
                                  ON DELETE NO ACTION,
                          FOREIGN KEY (season)
                              REFERENCES nfl (season) 
                              ON UPDATE NO ACTION
                              ON DELETE NO ACTION);"""

        CreateTables.execute_qry(qry)


    def create_results_history():
        qry = """create table if not exists results_history (
                     season integer NOT NULL,
                     week integer NOT NULL,
                     home_team integer NOT NULL,
                     away_team integer NOT NULL,
                     home_score integer NOT NULL,
                     away_score integer NOT NULL,
                     winner integer NOT NULL,
                     loser integer NOT NULL); """
        CreateTables.execute_qry(qry)


    def create_rushing():
        qry = """create table if not exists rushing (
                      season integer NOT NULL,
                      week integer NOT NULL,
                      player_id integer NOT NULL,
                      team_id integer NOT NULL,
                      att integer,
                      yds integer,
                      avg numeric(4,1),
                      lg integer,
                      td integer,
                      opp_team_id integer,
                      foreign key (team_id)
                         references teams(team_id)
                         on delete cascade
                         on update cascade,
                      foreign key (player_id)
                            references active_players(player_id)
                            on delete cascade
                            on update cascade);"""
        CreateTables.execute_qry(qry)


    def create_sacks():
        qry = """create table if not exists sacks (
                         season integer NOT NULL,
                         week integer NOT NULL,
                         player_id integer NOT NULL,
                         team_id integer NOT NULL,
                         cnt integer,
                         opp_team_id integer,
                         foreign key (team_id)
                             references teams(team_id)
                             on delete cascade
                             on update cascade,
                      foreign key (player_id)
                            references active_players(player_id)
                            on delete cascade
                            on update cascade);"""
        CreateTables.execute_qry(qry)


    def create_sched_template():
        qry = """create table if not exists sched_template (
                        sched_type integer NOT NULL,
                        v_division varchar(3) NOT NULL,
                        v_finish integer NOT NULL,
                        h_division varchar(3) NOT NULL,
                        h_finish integer NOT NULL,
                        week integer NOT NULL,
                        no_teams integer,
                        no_divisions integer,
                        no_games integer); """
        CreateTables.execute_qry(qry)

    def create_schedule():
        qry = """create table if not exists schedule (
                      season integer NOT NULL,
                      week integer NOT NULL,
                      home_team varchar(40) NOT NULL,
                      away_team varchar(40) NOT NULL,
                      PRIMARY KEY (season, week, home_team)); """
        CreateTables.execute_qry(qry)


    def create_standings_history():
        qry = """create table if not exists standings_history (
                         team_id integer NOT NULL,
                         name varchar(20) ,
                         division varchar(30) ,
                         wins integer,
                         losses integer,
                         div_wins integer,
                         div_losses integer,
                         conf_wins integer,
                         conf_losses integer,
                         season integer); """
        CreateTables.execute_qry(qry)


    def create_starters():
        qry = """create table if not exists starters (
                        player_id integer NOT NULL,
                        team_id integer NOT NULL,
                        player_num integer NOT NULL,
                        starts varchar(4) NOT NULL,
                        PRIMARY KEY (player_id, team_id, starts, player_num),
                        foreign key (team_id)
                           references teams(team_id)
                                on delete cascade
                                on update cascade,
                      foreign key (player_id)
                            references active_players(player_id)
                            on delete cascade
                            on update cascade
                           );"""
        CreateTables.execute_qry(qry)


    def create_team_stats():
        qry = """create table if not exists team_stats (
                       season integer NOT NULL,
                       week integer NOT NULL,
                       team_id integer NOT NULL,
                       opp_id integer NOT NULL,
                       points integer NOT NULL,
                       pts_q1 integer NOT NULL,
                       pts_q2 integer NOT NULL,
                       pts_q3 integer NOT NULL,
                       pts_q4 integer NOT NULL,
                       fdowns integer,
                       frushes integer,
                       fpass integer,
                       fpen integer,
                       thirdmade integer,
                       thirdtried integer,
                       tot_yards integer,
                       tot_plays integer,
                       net_rush integer,
                       rush_plays integer,
                       net_pass integer,
                       pass_atts integer,
                       completes integer,
                       intercepts integer,
                       sacks integer,
                       sack_yds integer,
                       punts integer,
                       punt_avg numeric(5,1) ,
                       return_yds integer,
                       penalties integer,
                       pen_yds integer,
                       fumbles integer,
                       fumlost integer,
                       top_mins integer,
                       top_secs integer,
                       foreign key (team_id)
                         references teams(team_id)
                               on delete cascade
                               on update cascade
                        );"""
        CreateTables.execute_qry(qry)


    def create_teams():
        qry = """create table if not exists teams (
                     team_id integer NOT NULL primary key autoincrement,
                     name varchar(20) ,
                     city varchar(20) ,
                     offense varchar(15) ,
                     defense varchar(15) ,
                     last_finish integer not null default 0,
                     div_code varchar(2) ,
                     conf varchar(3) ,
                     coach_id integer default null,
                     FOREIGN KEY (defense)
                         REFERENCES coaching_styles (coaching_style) 
                         ON UPDATE NO ACTION
                         ON DELETE NO ACTION,
                     FOREIGN KEY (div_code)
                         REFERENCES divisions (div_code)
                         ON UPDATE CASCADE
                         ON DELETE NO ACTION,
                     FOREIGN KEY (conf)
                         REFERENCES conference (conf_code)
                         ON UPDATE CASCADE
                         ON DELETE NO ACTION,
                     FOREIGN KEY (coach_id)
                         REFERENCES coaches (coach_id)
                         ON UPDATE CASCADE
                         ON DELETE NO ACTION,
                     FOREIGN KEY (offense)
                         REFERENCES coaching_styles (coaching_style) 
                         ON UPDATE NO ACTION
                         ON DELETE NO ACTION); """
        CreateTables.execute_qry(qry)
        qry = "insert into teams(name,city,div_code,conf) values ('Cowboys','Dallas','ne','nfc')"
        CreateTables.execute_qry(qry)
        qry = "insert into teams(name,city,div_code,conf) values ('Giants','New York','ne','nfc')"
        CreateTables.execute_qry(qry)
        qry = "insert into teams(name,city,div_code,conf) values ('Redskins','Washington','ne','nfc')"
        CreateTables.execute_qry(qry)
        qry = "insert into teams(name,city,div_code,conf) values ('Eagles','Philadelphia','ne','nfc')"
        CreateTables.execute_qry(qry)
        qry = "insert into teams(name,city,div_code,conf) values ('Cards','St. Louis','ne','nfc')"
        CreateTables.execute_qry(qry)
        qry = "insert into teams(name,city,div_code,conf) values ('Saints','New Orleans','nw','nfc')"
        CreateTables.execute_qry(qry)
        qry = "insert into teams(name,city,div_code,conf) values ('Falcons','Atlanta','nw','nfc')"
        CreateTables.execute_qry(qry)
        qry = "insert into teams(name,city,div_code,conf) values ('49ers','San Francisco','nw','nfc')"
        CreateTables.execute_qry(qry)
        qry = "insert into teams(name,city,div_code,conf) values ('Rams','Los Angeles','nw','nfc')"
        CreateTables.execute_qry(qry)
        qry = "insert into teams(name,city,div_code,conf) values ('Bucs','Tampa Bay','nc','nfc')"
        CreateTables.execute_qry(qry)
        qry = "insert into teams(name,city,div_code,conf) values ('Bears','Chicago','nc','nfc')"
        CreateTables.execute_qry(qry)
        qry = "insert into teams(name,city,div_code,conf) values ('Packers','Green Bay','nc','nfc')"
        CreateTables.execute_qry(qry)
        qry = "insert into teams(name,city,div_code,conf) values ('Lions','Detroit','nc','nfc')"
        CreateTables.execute_qry(qry)
        qry = "insert into teams(name,city,div_code,conf) values ('Vikings','Minnesota','nc','nfc')"
        CreateTables.execute_qry(qry)
        qry = "insert into teams(name,city,div_code,conf) values ('Patriots','New England','ae','afc')"
        CreateTables.execute_qry(qry)
        qry = "insert into teams(name,city,div_code,conf) values ('Dolphins','Miami','ae','afc')"
        CreateTables.execute_qry(qry)
        qry = "insert into teams(name,city,div_code,conf) values ('Jets','New York','ae','afc')"
        CreateTables.execute_qry(qry)
        qry = "insert into teams(name,city,div_code,conf) values ('Bills','Buffalo','ae','afc')"
        CreateTables.execute_qry(qry)
        qry = "insert into teams(name,city,div_code,conf) values ('Colts','Indianapolis','ae','afc')"
        CreateTables.execute_qry(qry)
        qry = "insert into teams(name,city,div_code,conf) values ('Chiefs','Kansas City','aw','afc')"
        CreateTables.execute_qry(qry)
        qry = "insert into teams(name,city,div_code,conf) values ('Broncos','Denver','aw','afc')"
        CreateTables.execute_qry(qry)
        qry = "insert into teams(name,city,div_code,conf) values ('Raiders','Oakland','aw','afc')"
        CreateTables.execute_qry(qry)
        qry = "insert into teams(name,city,div_code,conf) values ('Seahawks','Seattle','aw','afc')"
        CreateTables.execute_qry(qry)
        qry = "insert into teams(name,city,div_code,conf) values ('Chargers','San Diego','aw','afc')"
        CreateTables.execute_qry(qry)
        qry = "insert into teams(name,city,div_code,conf) values ('Oilers','Houston','ac','afc')"
        CreateTables.execute_qry(qry)
        qry = "insert into teams(name,city,div_code,conf) values ('Bengals','Cincinnati','ac','afc')"
        CreateTables.execute_qry(qry)
        qry = "insert into teams(name,city,div_code,conf) values ('Steelers','Pittsburgh','ac','afc')"
        CreateTables.execute_qry(qry)
        qry = "insert into teams(name,city,div_code,conf) values ('Browns','Cleveland','ac','afc')"
        CreateTables.execute_qry(qry)

    def create_tmp_standings():
        qry = """create table if not exists tmp_standings (
                        name varchar(20),
                        wins integer,
                        losses integer,
                        div_wins integer,
                        conf_wins integer,
                        team_id integer); """
        CreateTables.execute_qry(qry)

    def create_team_analyzed():
        qry = """CREATE TABLE team_analyzed (
                        team      varchar(20),
                        posi      varchar(2),
                        BlkAvg    INTEGER,
                        RunAvg    INTEGER,
                        RcvAvg    INTEGER,
                        PassAvg   INTEGER,
                        KickAvg   INTEGER,
                        AvgPlayer INTEGER,
                        rank      INTEGER,
                        needrnk   integer); """
        CreateTables.execute_qry(qry)


    def create_roster_specs():
        qry = """CREATE TABLE roster_specs (
                                   posi    VARCHAR (2) NOT NULL PRIMARY KEY,
                                   min_cnt INTEGER     NOT NULL,
                                   max_cnt INTEGER     NOT NULL,
                                   avg_cnt integer not null);"""
        CreateTables.execute_qry(qry)

    def create_combine_data():
        qry = """CREATE TABLE IF NOT EXISTS meta.combine_data (
                         name varchar(150) NOT NULL,
                         posi varchar (4),
                         ht smallint,
                         wt smallint,
                         forty numeric(3,2),
                         vertical numeric(4,2),
                         benchreps numeric(4,2),
                         broadjump numeric(5,2),
                         cone numeric(4,2),
                         shuttle numeric(4,2),
                         year smallint,
                         pfr_id varchar(50) 
                         av numeric(4,2),
                         team varchar(75),
                         rnd smallint,
                         pick smallint);"""
        CreateTables.execute_qry(qry)
        conn = sqlite3.connect("pyNFL.db")
        cursor = conn.cursor()
        with open('combine_data.csv') as csvfile:
          csvFile = csv.reader(csvfile)
          for lines in csvFile:
            cursor.execute(f"""insert into combine_data values ('{lines[0]}',{lines[1]},{lines[2]},{lines[3]},
                             {lines[4]},{lines[5]},{lines[6]},{lines[7]},{lines[8]},{lines[9]}, {lines[10]},
                             '{lines[11]}',{lines[12]},'{lines[13]}',{lines[14]},{lines[15]},{lines[16]});""")
        cursor.close()
        conn.commit()
        conn.close()


    def execute_qry(qry):
        conn = sqlite3.connect("pyNFL.db")
        cursor = conn.cursor()
        cursor.execute(qry)
        cursor.close()
        conn.commit()
        conn.close()
