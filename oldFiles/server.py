import EloRatings
from flask import Flask
import os
import psycopg2
import urlparse

#server
app = Flask(__name__)

@app.route('/', methods=['POST', 'GET'])
def index():
    EloRatings.main(os.environ.get("GAMELOG_FILE"))
    s = ""
    html = open("score.html","r")
    for line in html.readlines():
        s += line
    s+="\n"+EloRatings.calculateOutliers()
    return s

if __name__ == '__main__':
    #app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
    urlparse.uses_netloc.append("postgres")
    url = urlparse.urlparse("postgres://bajqyybwqouyvr:96c187860b5bec3e831f0ed8da07c67bf70c0039e3994b43505001855709943f@ec2-50-19-95-47.compute-1.amazonaws.com:5432/ddqtbots988fqk")

    conn = psycopg2.connect(
        database=url.path[1:],
        user=url.username,
        password=url.password,
        host=url.hostname,
        port=url.port
    )

    cur = conn.cursor()
    #cur.execute("CREATE TABLE test (id serial PRIMARY KEY, num integer, data varchar);")

    #cur.execute("INSERT INTO test (num, data) VALUES (%s, %s)", (100, "abc'def"))

    # Query the database and obtain data as Python objects
    cur.execute("SELECT * FROM test;")
    print cur.fetchone()


    # Make the changes to the database persistent
    conn.commit()

    cur.close()
    conn.close()