import EloRatings
from flask import Flask
import os

#server
app = Flask(__name__)

@app.route('/', methods=['POST', 'GET'])
def index():
    EloRatings.main(os.environ.get("GAMELOG_FILE"))
    s = ""
    html = open("score.html","r")
    for line in html.readlines():
        s += line
    return s

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
