import math
import numpy as np
import requests
from pandas import DataFrame
import os
#from argparse import ArgumentParser

class Player:
    def __init__(self, name, rating):
        self.name = name
        self.rating = rating
        self.wins = 0
        self.losses = 0
        self.versus = {}
        self.history = []

    def defeats(self, other, k=75):
        # look at wiki page for elo ratings for references
        expected = 1 / (1 + math.pow(10, (other.rating - self.rating) / 400))
        otherExpected = 1 / (1 + math.pow(10, (self.rating - other.rating) / 400))

        self.rating += k * (1 - expected)
        self.history.append(int(round(self.rating)))
        other.rating -= k * otherExpected
        other.history.append(int(round(other.rating)))
        self.wins += 1
        other.losses += 1

        self.versus[other.name] = (self.versus.get(other.name, (0, 0))[0] + 1, self.versus.get(other.name, (0, 0))[1])
        other.versus[self.name] = (other.versus.get(self.name, (0, 0))[0], other.versus.get(self.name, (0, 0))[1] + 1)

        if fileImport == "":
            log = open("gamelogs/old_gamelog.txt", mode="a")
            log.write(self.name + " defeats " + other.name + "\n")
            log.close()

    def whatif(self, other, k=75):
        expected = 1 / (1 + math.pow(10, (other.rating - self.rating) / 400))
        otherExpected = 1 / (1 + math.pow(10, (self.rating - other.rating) / 400))

        hypothetialRating = self.rating + k * (1-expected)
        hypothetialOther = other.rating + k * (0-otherExpected)

        return (hypothetialRating, hypothetialOther)

    def __str__(self):
        return self.name + " (" + str(self.wins) + ", " + str(self.losses) + ") - " + str(int(round(self.rating, 0)))

    def __lt__(self, other):
        return self.rating - other.rating > 0


def calculateOutliers(players):
    npp = np.array([p.rating for p in players])
    q1 = np.percentile(npp, 25)
    q3 = np.percentile(npp, 75)
    iqr = q3 - q1
    string = ""
    for i in range(len(players)):
        if npp[i] < q1 - 1.5 * iqr:
            bad = players[i]
            string += str(bad) + " is statistically really bad!\n"
        if npp[i] > q3 + 1.5 * iqr:
            good = players[i]
            string += str(good) + " is statistically really good!\n"
    if string == "":
        string = "There are on outliers."
    return string


def clearLog():
    log = open("gamelogs/old_gamelog.txt", mode="w")
    log.close()


# def setupParser():
#     global K
#     global fileImport
#     global startRating
#     global matchResult
#     global toSend
#     global toGet
#
#     parser = ArgumentParser()
#     parser.add_argument("-k", "--k_value", default=75, type=int, dest="K",
#                         help="K value that determines rating changes")
#     parser.add_argument("-f", "--file_import", default="", dest="fileImport",
#                         help="What file to to read competition data from file present in /gamelogs")
#     parser.add_argument("-r", "--start_rating", default=1000, type=int, dest="startRating",
#                         help="Starting rating for all players")
#     parser.add_argument("-m", "--match_results", default=None, dest="result",
#                         help="Results of a match. Formatted as \"[winner] defeats [loser]\".")
#     parser.add_argument("-s", "--send", default=False, dest="send", action="store_true",
#                         help="Whether to send the results to the GroupMe API")
#     parser.add_argument("-g", "--get", default=False, dest="get", action="store_true",
#                         help="Whether to get last message from GroupMe to add new match")
#
#
#     args = parser.parse_args()
#     K = args.K
#     fileImport = "gamelogs/" + args.fileImport
#     startRating = args.startRating
#     matchResult = args.result
#     toSend = args.send
#     toGet = args.get


# this isn't for modularity, its only purpose is to make the main cleaner

def enterMatchesFromCode():
    global K
    global startRating
    backupGamelog = "gamelogs/old_gamelog.txt"

    william = Player("William", startRating)
    brian = Player("Brian", startRating)
    will = Player("Will", startRating)
    franklin = Player("Franklin", startRating)
    pop = Player("Pop", startRating)
    players = [william, brian, will, franklin, pop]

    clearLog()
    log = open(backupGamelog, mode="a")
    for p in players:
        log.write(p.name + " " + str(p.rating) + "\n")
    log.write("0\n")
    log.close()

    william.defeats(brian, K)
    brian.defeats(will, K)
    william.defeats(will, K)
    will.defeats(brian, K)
    franklin.defeats(will, K)
    franklin.defeats(pop, K)
    will.defeats(pop, K)
    franklin.defeats(will, K)
    will.defeats(franklin, K)
    will.defeats(pop, K)

    players = [william, brian, will, franklin, pop]

    log = open(backupGamelog, mode="a")
    log.write("0\n")
    log.close()

    return players


def readMatchesFromFile():
    global fileImport
    global players

    try:
        file = open(fileImport, "r")

        lines = file.readlines()
        i = 0
        players = []

        # add players
        while lines[i].strip() is not "0":
            name, start = lines[i].strip().split(" ")
            players.append(Player(name, int(start)))
            i += 1
        i += 1

        # start competition
        while lines[i].strip() is not "0":
            wName, x, lName = lines[i].strip().split(" ")

            # if winner or loser are not in players add them to the list
            if not playerExists(players, wName):
                players.append(Player(wName, startRating))
            if not playerExists(players, lName):
                players.append(Player(lName, startRating))

            # get the actual player objects
            winner = [p for p in players if p.name == wName][0]
            loser = [p for p in players if p.name == lName][0]
            # input match results into model
            winner.defeats(loser, K)
            i += 1
    except:
        print "---" + fileImport + " is not a valid file\n---Now exiting"



def playerExists(name):
    global players
    player = [p for p in players if p.name == name]
    return len(player) > 0


def processMatchFromStrings(winner, loser):
    global players

    ifAdd = False
    # see if players exist and add them to list if ifAdd
    if not playerExists(winner):
        if ifAdd:
            players.append(Player(winner, startRating))
        else:
            raise AttributeError(winner + " is not a current player")

    if not playerExists(loser):
        if ifAdd:
            players.append(Player(loser, startRating))
        else:
            raise AttributeError(loser+ " is not a current player")

    # get the actual player objects
    winner = [p for p in players if p.name == winner][0]
    loser = [p for p in players if p.name == loser][0]

    # input match results into model
    winner.defeats(loser, K)

    # keep data already in file
    readFile = open(fileImport)
    lines = readFile.readlines()
    readFile.close()

    # remove 0 at end of file and add new result
    w = open(fileImport, 'w')
    w.writelines([item for item in lines[:-1]])
    w.write(winner.name + " defeats " + loser.name)
    w.write("\n0")
    w.close()


def sendMessage(message, botID=os.environ.get("BOT_ID")):
    data = {"text": message, "bot_id": botID}
    send = requests.post("https://api.groupme.com/v3/bots/post", json=data)
    return send


def parseCommands():
    global players
    global fileImport

    botID = os.environ.get("BOT_TOKEN")
    groupID = os.environ.get("GROUP_DEBUG")
    limit = "1"
    get = requests.get("https://api.groupme.com/v3/groups/" + groupID + "/messages?token=" + botID + "&limit=" + limit)
    string = get.json()[u'response'][u'messages'][0][u'text'].split(" ")
    string = [str(u) for u in string]

    # string is now a list of the words in the most recent message
    # test for command before doing anything
    if string[0][0] == "$":

        if string[0] == "$match":
            print string
            try:
                players = processMatchFromStrings(string[1], string[3])
                winner = [p for p in players if p.name == string[1]][0]
                loser = [p for p in players if p.name == string[3]][0]
                sendMessage(winner.name + "->" + str(int(round(winner.rating))) + "\n" + loser.name + "->" + str(
                    int(round(loser.rating))))
            except IndexError:
                sendMessage("Your command is in the wrong format.\nTry \n\"$match [winner] defeats [loser]\".")
            except AttributeError as error:
                sendMessage(error.message)

        elif string[0] == "$score":
            players.sort()
            d = [[p.name, "(" + str(p.wins) + ", " + str(p.losses) + ")", int(round(p.rating))] for p in players]
            df = DataFrame(data=d, columns=["Name", "Record", "Rating"],
                           index=["#" + str(i + 1) + ". " for i in range(len(players))])

            message = "" + df.to_string(header=False) + "\n\n"
            # print message
            sendMessage(message)

        elif string[0] == "$whatIf":
            try:
                if playerExists(string[1]) and playerExists(string[3]):
                    winner = [p for p in players if p.name == string[1]][0]
                    loser = [p for p in players if p.name == string[3]][0]
                    whatif = winner.whatif(loser)
                    sendMessage(winner + " -> " + whatif[0] + "\n" + loser + " -> " + whatif[1])
            except IndexError:
                sendMessage("Your command is in the wrong format. \nTry \n$whatIf [winner] defeats [loser]")

        elif string[0] == "$playerHistory":
            try:
                if playerExists(string[1]):
                    winner = [p for p in players if p.name == string[1]][0]
                    string = ""
                    for s in [str(h) for h in winner.history]:
                        string += s
                    sendMessage(string)
            except IndexError:
                sendMessage("Your command is in the wrong format. \nTry \n$playerHistory [player]")

        elif string[0] == "$matchHistory":
            file = open(fileImport, "r")

            lines = file.readlines()
            i = 0

            # add players
            while lines[i].strip() is not "0":
                i += 1
            i += 1
            matches = ""
            while lines[i].strip() is not "0":
                matches += lines[i] + "\n"
                i+=1
            file.close()
            sendMessage(matches)

        elif string[0] == "$outliers":
            out = calculateOutliers(players)
            sendMessage(out)

        elif string[0] == "$commands":
            sendMessage(">$match [winner] defeats [loser]\n"
                        "$score\n"
                        "$playerHistory [player]\n"
                        "$matchHistory]\n"
                        "$whatif [winner] defeats [loser]\n"
                        "$outliers\n"
                        "$commands")
        else:
            # message starts with 0 but there is not recognized command
            pass
            # sendMessage("No valid command recognized")


def renderHTML():
    d = [[p.name, "(" + str(p.wins) + ", " + str(p.losses) + ")", int(round(p.rating))] for p in players]
    df = DataFrame(data=d, columns=["Name", "Record", "Rating"],
                   index=["#" + str(i + 1) + ". " for i in range(len(players))])

    f = open("score.html", mode='w')
    f.write(df.style.render())
    f.close()


def main(FI):
    global Kv
    global startRating
    global matchResult
    global fileImport
    global players

    #setupParser()
    K = 75
    startRating = 1000
    fileImport = "gamelogs/" + FI

    readMatchesFromFile()

    # if fileImport is not "":
    # else:
    #     players = enterMatchesFromCode()

    #where most of the work is done
    parseCommands()

    players.sort()

    renderHTML()



