import config
import LeagueManager
import psycopg2

def getPlayer(name):
    conn = config.getConnection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM players where player_name = %s;", (name, ))
    name,rating,wins,loses = cur.fetchone()
    cur.close()
    conn.close()
    return LeagueManager.Player(name=name, rating=rating, wins=wins, loses=loses)

def addWin(name):
    conn = config.getConnection()
    cur = conn.cursor()
    cur.execute("update players set wins=wins+1 where player_name == %s;", (name,))
    cur.close()
    conn.close()

def addLoss(name):
    conn = config.getConnection()
    cur = conn.cursor()
    cur.execute("update players set loses=loses+1 where player_name == %s;", (name,))
    cur.close()
    conn.close()

def updateRating(name,rating):
    conn = config.getConnection()
    cur = conn.cursor()
    cur.execute("update players set rating=%s where player_name == %s;", (rating,name))
    cur.close()
    conn.close()