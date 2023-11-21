
CREATE TABLE teams (
  team_id serial NOT NULL ,
  name character varying(20) NOT NULL,
  city character varying(20) NOT NULL,
  offense character varying(15) DEFAULT NULL,
  defense character varying(15) DEFAULT NULL,
  division character varying(12) DEFAULT NULL,
  last_finish integer DEFAULT NULL,
  div_code character varying(2) DEFAULT NULL,
  conf character varying(3) DEFAULT NULL,
  PRIMARY KEY (team_id)
); 



CREATE TABLE active_players (
  player_id serial NOT NULL,
  jersey_no integer NOT NULL,
  name character varying(40) NOT NULL,
  posi character varying(2) DEFAULT NULL,
  ht character varying(6) NOT NULL,
  wt integer NOT NULL,
  yrs integer NOT NULL,
  spd decimal(3,1) DEFAULT NULL,
  rush integer NOT NULL,
  rcv integer NOT NULL,
  pass integer NOT NULL,
  kick integer NOT NULL,
  starter character varying(4) DEFAULT NULL,
  team_id integer NOT NULL,
  team character varying(20) DEFAULT NULL,
  blk integer NOT NULL,
  KR char(1) DEFAULT NULL,
  PR char(1) DEFAULT NULL,
  active char(1) DEFAULT 'Y',
  PRIMARY KEY (player_id),
  FOREIGN KEY (team_id) REFERENCES teams (team_id)
);

CREATE TABLE coaches (
  coach_id serial NOT NULL,
  name character varying(30) NOT NULL,
  isactive char(1) DEFAULT 'Y',
  team character varying(35) DEFAULT NULL,
  wins integer DEFAULT '0',
  losses integer DEFAULT '0',
  winpct decimal(5,1) DEFAULT '0.0',
  offense character varying(15) DEFAULT NULL,
  defense character varying(15) DEFAULT NULL,
  age integer DEFAULT NULL,
  PRIMARY KEY (coach_id)
) ;

CREATE TABLE divisions (
  div_code char(2) NOT NULL,
  div_name character varying(25) NOT NULL,
  PRIMARY KEY (div_code)
) ;


CREATE TABLE draft_players (
  player_id serial NOT NULL ,
  name character varying(40) NOT NULL,
  posi character varying(2) DEFAULT NULL,
  ht character varying(6) NOT NULL,
  wt integer NOT NULL,
  yrs integer NOT NULL,
  spd decimal(3,1) DEFAULT NULL,
  rush integer NOT NULL,
  rcv integer NOT NULL,
  pass integer NOT NULL,
  kick integer NOT NULL,
  blk integer NOT NULL,
  PRIMARY KEY (player_id)
) ;


CREATE TABLE firstnames (
  name character varying(20) NOT NULL,
  PRIMARY KEY (name)
);


CREATE TABLE interceptions (
  season integer NOT NULL,
  week integer NOT NULL,
  player_id integer NOT NULL,
  team_id integer NOT NULL,
  cnt integer DEFAULT NULL,
  yards integer DEFAULT NULL,
  tds integer DEFAULT NULL,
  longest integer DEFAULT NULL,
  average decimal(4,1) DEFAULT NULL,
  opp_team_id integer NOT NULL
) ;

CREATE TABLE kick_returns (
  season integer NOT NULL,
  week integer NOT NULL,
  player_id integer NOT NULL,
  team_id integer NOT NULL,
  cnt integer DEFAULT NULL,
  yards integer DEFAULT NULL,
  avg decimal(5,1) DEFAULT NULL,
  lg integer DEFAULT NULL,
  tds integer DEFAULT NULL,
  opp_team_id integer DEFAULT NULL
) ;

CREATE TABLE kickers (
  season integer NOT NULL,
  week integer NOT NULL,
  player_id integer NOT NULL,
  team_id integer NOT NULL,
  ep integer DEFAULT NULL,
  epatt integer DEFAULT NULL,
  fg integer DEFAULT NULL,
  fgatt integer DEFAULT NULL,
  lg integer DEFAULT NULL,
  opp_team_id integer DEFAULT NULL
); 


CREATE table passing (
  season integer not null,
  week integer default null,
  player_id integer default null,
  team_id integer default null,
  attempts integer default null,
  complete integer default null,
  yards integer default null,
  tds integer default null,
  intercepts integer default null,
  lg integer default null,
  opp_team_id integer default null,
  primary key (player_id, team_id)
  );






CREATE TABLE lastnames (
  surname character varying(60) NOT NULL,
  approx_cnt integer NOT NULL,
  freq decimal(6,3) NOT NULL,
  rank integer DEFAULT NULL,
  PRIMARY KEY (surname)
) ;

CREATE TABLE nfl (
  season integer NOT NULL,
  sched_type integer NOT NULL,
  complete char(1) DEFAULT NULL,
  teams integer DEFAULT NULL,
  weeks integer DEFAULT NULL,
  PRIMARY KEY (season)
); 


CREATE TABLE player_history (
  player_id integer NOT NULL DEFAULT '0',
  jersey_no integer NOT NULL,
  name character varying(40) NOT NULL,
  posi character varying(2) DEFAULT NULL,
  ht character varying(6) NOT NULL,
  wt integer NOT NULL,
  yrs integer NOT NULL,
  spd decimal(3,1) DEFAULT NULL,
  rush integer NOT NULL,
  rcv integer NOT NULL,
  pass integer NOT NULL,
  kick integer NOT NULL,
  starter character varying(4) DEFAULT NULL,
  team_id integer NOT NULL,
  team character varying(20) DEFAULT NULL,
  blk integer NOT NULL,
  KR char(1) DEFAULT NULL,
  PR char(1) DEFAULT NULL,
  active char(1) DEFAULT 'Y',
  year integer DEFAULT NULL
); 


CREATE TABLE playoffs (
  div_name character varying(15) NOT NULL,
  team character varying(20) NOT NULL,
  wins integer NOT NULL,
  div_wins integer NOT NULL,
  conf_wins integer NOT NULL,
  div_winner char(1) DEFAULT NULL,
  bye char(1) DEFAULT NULL,
  seed integer DEFAULT NULL,
  week integer DEFAULT NULL,
  season integer DEFAULT NULL
) ;

CREATE TABLE punt_returns (
  season integer NOT NULL,
  week integer NOT NULL,
  player_id integer NOT NULL,
  team_id integer NOT NULL,
  cnt integer DEFAULT NULL,
  yards integer DEFAULT NULL,
  avg decimal(5,1) DEFAULT NULL,
  lg integer DEFAULT NULL,
  tds integer DEFAULT NULL,
  opp_team_id integer DEFAULT NULL
) ;

CREATE TABLE rankings (
  year integer NOT NULL,
  team character varying(45) NOT NULL,
  category character varying(45) NOT NULL,
  value integer NOT NULL,
  rnk integer NOT NULL
) ;


CREATE TABLE rarelastnames (
  surname character varying(40) NOT NULL,
  rank integer NOT NULL,
  cnt integer NOT NULL,
  per_100k decimal(7,2) DEFAULT NULL,
  pct_white decimal(5,1) DEFAULT NULL,
  pct_black decimal(5,1) DEFAULT NULL,
  pct_api decimal(5,1) DEFAULT NULL,
  pct_aiam decimal(5,0) DEFAULT NULL,
  pct_multi decimal(5,1) DEFAULT NULL,
  pct_hispanic decimal(5,1) DEFAULT NULL,
  rank_in_2000 integer DEFAULT NULL,
  cnt_in_2000 integer DEFAULT NULL,
  chg_since_2000 integer DEFAULT NULL,
  pct_change decimal(5,1) DEFAULT NULL,
  rank_change integer DEFAULT NULL,
  PRIMARY KEY (surname)
); 


CREATE TABLE receiving (
  season integer NOT NULL,
  week integer NOT NULL,
  player_id integer NOT NULL,
  team_id integer NOT NULL,
  cnt integer DEFAULT NULL,
  yards integer DEFAULT NULL,
  average decimal(5,1) DEFAULT NULL,
  lg integer DEFAULT NULL,
  tds integer DEFAULT NULL,
  opp_team_id integer DEFAULT NULL
) ;


CREATE TABLE results (
  season integer NOT NULL,
  week integer NOT NULL,
  home_team integer NOT NULL,
  away_team integer NOT NULL,
  home_score integer NOT NULL,
  away_score integer NOT NULL,
  winner integer NOT NULL,
  loser integer NOT NULL,
  FOREIGN KEY (away_team) REFERENCES teams (team_id),
  FOREIGN KEY (home_team) REFERENCES teams (team_id),
  FOREIGN KEY (season) REFERENCES nfl (season)
) ;

CREATE TABLE results_history (
  season integer NOT NULL,
  week integer NOT NULL,
  home_team integer NOT NULL,
  away_team integer NOT NULL,
  home_score integer NOT NULL,
  away_score integer NOT NULL,
  winner integer NOT NULL,
  loser integer NOT NULL
) ;

CREATE TABLE rushing (
  season integer NOT NULL,
  week integer NOT NULL,
  player_id integer NOT NULL,
  team_id integer NOT NULL,
  att integer DEFAULT NULL,
  yds integer DEFAULT NULL,
  avg decimal(4,1) DEFAULT NULL,
  lg integer DEFAULT NULL,
  td integer DEFAULT NULL,
  opp_team_id integer DEFAULT NULL
) ;

CREATE TABLE sacks (
  season integer NOT NULL,
  week integer NOT NULL,
  player_id integer NOT NULL,
  team_id integer NOT NULL,
  cnt integer DEFAULT NULL,
  opp_team_id integer DEFAULT NULL
) ;


CREATE TABLE sched_template (
  sched_type integer NOT NULL,
  v_division character varying(3) NOT NULL,
  v_finish integer NOT NULL,
  h_division character varying(3) NOT NULL,
  h_finish integer NOT NULL,
  week integer NOT NULL,
  no_teams integer DEFAULT NULL,
  no_divisions integer DEFAULT NULL,
  no_games integer DEFAULT NULL
) ;

CREATE TABLE schedule (
  season integer NOT NULL,
  week integer NOT NULL,
  home_team character varying(40) NOT NULL,
  away_team character varying(40) NOT NULL,
  PRIMARY KEY (season,week,home_team)
) ;


CREATE TABLE standings (
  team_id integer NOT NULL,
  name character varying(20) DEFAULT NULL,
  division character varying(30) DEFAULT NULL,
  wins integer DEFAULT NULL,
  losses integer DEFAULT NULL,
  div_wins integer DEFAULT NULL,
  div_losses integer DEFAULT NULL,
  conf_wins integer DEFAULT NULL,
  conf_losses integer DEFAULT NULL,
  rnk integer DEFAULT NULL,
  PRIMARY KEY (team_id)
) ;

CREATE TABLE standings_history (
  team_id integer NOT NULL,
  name character varying(20) DEFAULT NULL,
  division character varying(30) DEFAULT NULL,
  wins integer DEFAULT NULL,
  losses integer DEFAULT NULL,
  div_wins integer DEFAULT NULL,
  div_losses integer DEFAULT NULL,
  conf_wins integer DEFAULT NULL,
  conf_losses integer DEFAULT NULL,
  season integer DEFAULT NULL
) ;


CREATE TABLE starters (
  player_id integer NOT NULL,
  team_id integer NOT NULL,
  player_num integer NOT NULL,
  starts character varying(4) NOT NULL,
  PRIMARY KEY (player_id,team_id,starts,player_num)
) ;



CREATE TABLE tmp_standings (
  name character varying(20) DEFAULT NULL,
  wins integer DEFAULT NULL,
  losses integer DEFAULT NULL,
  div_wins integer DEFAULT NULL,
  conf_wins integer DEFAULT NULL,
  team_id integer DEFAULT NULL
) ;

CREATE view losses as
   select results.loser as loser, count(*) as losses
from results group by results.loser;

CREATE view wins as
   select results.winner as winner, count(*) as wins
   from results
   group by results.winner;



CREATE or replace function func_upd_coach_pct()
   returns trigger as
$BODY$
  BEGIN
     if (new.wins > 0) then 
          new.winpct = (new.wins::decimal / (new.wins::decimal + new.losses::decimal)) * 100.0; 
     end if;  
     RETURN NEW;
  END;
$BODY$
LANGUAGE plpgsql volatile
;

CREATE trigger trig_upd_coach_pct
   BEFORE INSERT or update
   on coaches
   FOR EACH ROW
   EXECUTE PROCEDURE func_upd_coach_pct();

CREATE TABLE if not exists team_stats (
    season integer NOT NULL,
    week integer NOT NULL,  
    team_id integer NOT NULL,
    opp_id integer NOT NULL,
    points integer NOT NULL,
    pts_q1 integer NOT NULL,
    pts_q2 integer NOT NULL,
    pts_q3 integer NOT NULL,
    pts_q4 integer NOT NULL,
    fdowns integer DEFAULT NULL,
    frushes integer DEFAULT NULL,
    fpass integer DEFAULT NULL, 
    fpen integer DEFAULT NULL, 
    thirdmade integer DEFAULT NULL,
    thirdtried integer DEFAULT NULL,
    tot_yards integer DEFAULT NULL,
    tot_plays integer DEFAULT NULL,
    net_rush integer DEFAULT NULL, 
    rush_plays integer DEFAULT NULL,
    net_pass integer DEFAULT NULL,  
    pass_atts integer DEFAULT NULL,
    completes integer DEFAULT NULL,
    intercepts integer DEFAULT NULL,
    sacks integer DEFAULT NULL,    
    sack_yds integer DEFAULT NULL,
    punts integer DEFAULT NULL,  
    punt_avg decimal(5,1) DEFAULT NULL,
    return_yds integer DEFAULT NULL,   
    penalties integer DEFAULT NULL,   
    pen_yds integer DEFAULT NULL,     
    fumbles integer DEFAULT NULL,     
    fumlost integer DEFAULT NULL,     
    top_mins integer DEFAULT NULL,    
    top_secs integer DEFAULT NULL     
);


create table coaching_styles (
   coaching_style character varying(15) not null primary key
);

