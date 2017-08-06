import math
import numpy as np
import requests
from pandas import DataFrame
import os
#from argparse import ArgumentParser

class Player:
    def __init__(self, name, rating):
        self.name = name
        self.rating = float(rating)
        self.wins = 0
        self.losses = 0
        self.versus = {}
        self.history = []

    def defeats(self, other, k=75):
        # look at wiki page for elo ratings for references
        expected = 1.0 / (1.0 + math.pow(10.0, (other.rating - self.rating) / 400.0))
        otherExpected = 1.0 / (1.0 + math.pow(10.0, (self.rating - other.rating) / 400.0))

        self.rating += float(k * (1 - expected))
        self.history.append(int(round(self.rating)))
        other.rating -= float(k * otherExpected)
        other.history.append(int(round(other.rating)))
        self.wins += 1
        other.losses += 1

        self.versus[other.name] = (self.versus.get(other.name, (0, 0))[0] + 1, self.versus.get(other.name, (0, 0))[1])
        other.versus[self.name] = (other.versus.get(self.name, (0, 0))[0], other.versus.get(self.name, (0, 0))[1] + 1)

        if fileImport == "":
            log = open("gamelogs/old_gamelog.txt", mode="a")
            log.write(self.name + " defeats " + other.name + "\n")
            log.close()

    #this only works for 2v2
    def teamWin(self, teammate, loser1, loser2, k=75):
        otherRating = self.oppTeamRating(teammate,loser1,loser2)
        expected = 1.0 / (1.0 + math.pow(10.0, (otherRating - self.rating) / 400.0))
        self.rating += float(k * (1 - expected))
        self.history.append(int(round(self.rating)))
        self.wins += 1

    def teamLoss(self,teammate,winner1,winner2, k=75):
        otherRating = self.oppTeamRating(teammate,winner1,winner2)
        expected = 1.0 / (1.0 + math.pow(10.0, (otherRating - self.rating) / 400.0))
        self.rating += float(k * (0 - expected))
        self.history.append(int(round(self.rating)))
        self.losses += 1

    def oppTeamRating(self, teammate, opp1, opp2):
        return (opp1.rating + opp2.rating) - teammate.rating

    def whatif(self, other, k=75):
        expected = 1.0 / (1.0 + math.pow(10, (other.rating - self.rating) / 400.0))
        otherExpected = 1.0 / (1.0 + math.pow(10, (self.rating - other.rating) / 400.0))

        hypothetialRating = self.rating + k * (1-expected)
        hypothetialOther = other.rating + k * (0-otherExpected)

        return (hypothetialRating, hypothetialOther)

    def chance(self, other):
        expected = float(1.0 / (1.0 + math.pow(10, (other.rating - self.rating) / 400.0)))
        otherExpected = float(1.0 / (1.0 + math.pow(10, (self.rating - other.rating) / 400.0)))
        return (expected, otherExpected)

    def __str__(self):
        return self.name + " (" + str(self.wins) + ", " + str(self.losses) + ") - " + str(int(round(self.rating, 0)))

    def __lt__(self, other):
        return self.rating - other.rating > 0


def calculateOutliers():
    global players
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
        string = "There are no outliers."
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
    global K

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
            words = lines[i].strip().split(" ")
            if words[0] == "Team":
                wName1, wName2, x, lName1, lName2 = words[1:]

                winner1 = [p for p in players if p.name == wName1][0]
                winner2 = [p for p in players if p.name == wName2][0]
                loser1 = [p for p in players if p.name == lName1][0]
                loser2 = [p for p in players if p.name == lName2][0]

                winner1.teamWin(winner2,loser1,loser2,K)
                winner2.teamWin(winner1,loser1,loser2,K)

                loser1.teamLoss(loser1,winner1,winner2,K)
                loser2.teamLoss(loser1,winner1,winner2,K)
            else:
                wName, x, lName = words

                # if winner or loser are not in players add them to the list
                if not playerExists(wName):
                    players.append(Player(wName, startRating))
                if not playerExists(lName):
                    players.append(Player(lName, startRating))

                # get the actual player objects
                winner = [p for p in players if p.name == wName][0]
                loser = [p for p in players if p.name == lName][0]
                # input match results into model
                winner.defeats(loser, K)
            i += 1
    except IOError:
        print "---" + fileImport + " is not a valid file."


def playerExists(name):
    global players
    player = [p for p in players if p.name == name]
    return len(player) > 0


def processTeamFromStrings(winner1, winner2, loser1, loser2):
    ifAdd = os.environ.get("ADD_NEW_PLAYER") == "True"
    # see if players exist and add them to list if ifAdd
    if not playerExists(winner1):
        if ifAdd:
            players.append(Player(winner1, startRating))
        else:
            raise AttributeError(winner1 + " is not a current player")
    if not playerExists(winner2):
        if ifAdd:
            players.append(Player(winner2, startRating))
        else:
            raise AttributeError(winner2 + " is not a current player")

    if not playerExists(loser1):
        if ifAdd:
            players.append(Player(loser1, startRating))
        else:
            raise AttributeError(loser1 + " is not a current player")
    if not playerExists(loser2):
        if ifAdd:
            players.append(Player(loser2, startRating))
        else:
            raise AttributeError(loser2 + " is not a current player")

    wName1 = winner1
    wName2 = winner2
    lName1 = loser1
    lName2 = loser2

    winner1 = [p for p in players if p.name == wName1][0]
    winner2 = [p for p in players if p.name == wName2][0]
    loser1 = [p for p in players if p.name == lName1][0]
    loser2 = [p for p in players if p.name == lName2][0]

    wName1 = winner1
    wName2 = winner2
    lName1 = loser1
    lName2 = loser2

    winner1.teamWin(wName2, lName1, lName2, K)
    winner2.teamWin(winner1, lName1, lName2, K)

    loser1.teamLoss(lName2, winner1, wName2, K)
    loser2.teamLoss(lName1, winner1, wName2, K)

    # keep data already in file
    readFile = open(fileImport)
    lines = readFile.readlines()
    readFile.close()

    # remove 0 at end of file and add new result
    w = open(fileImport, 'w')
    w.writelines([item for item in lines[:-1]])
    w.write("Team " +wName1.name+" "+wName2.name+ " defeats " + lName1.name + " " + lName2.name)
    w.write("\n0")
    w.close()


def processMatchFromStrings(winner, loser):
    global players

    ifAdd = os.environ.get("ADD_NEW_PLAYER") == "True"
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
    global K

    botID = os.environ.get("BOT_TOKEN")
    groupID = os.environ.get("GROUP_APPT")
    limit = "1"
    get = requests.get("https://api.groupme.com/v3/groups/" + groupID + "/messages?token=" + botID + "&limit=" + limit)
    string = get.json()[u'response'][u'messages'][0]
    senderName = str(string[u'name'])
    string = string[u'text'].split(" ")
    string = [str(u) for u in string]

    # string is now a list of the words in the most recent message
    # test for command before doing anything
    if string[0][0] == "$":

        if string[0] == "$match":
            try:
                processMatchFromStrings(string[1], string[3])
                winner = [p for p in players if p.name == string[1]][0]
                loser = [p for p in players if p.name == string[3]][0]
                sendMessage(winner.name + "->" + str(int(round(winner.rating))) + "\n" + loser.name + "->" + str(
                    int(round(loser.rating))))
            except IndexError:
                sendMessage("Your command is in the wrong format.\nTry \n\"$match [winner] defeats [loser]\".")
            except AttributeError as error:
                sendMessage(error.message)

        elif string[0].lower() == "$teammatch":
            try:
                processTeamFromStrings(string[1],string[2],string[4],string[5])
                players.sort()
                d = [[p.name, "(" + str(p.wins) + ", " + str(p.losses) + ")", int(round(p.rating))] for p in players]
                df = DataFrame(data=d, columns=["Name", "Record", "Rating"],
                               index=["#" + str(i + 1) + ". " for i in range(len(players))])

                message = "" + df.to_string(header=False) + "\n\n"
                # print message
                sendMessage(message)
            except IndexError:
                sendMessage("Your command i in the wrong format.\nTry\n %TeamMatch [winner1] [winner2] defeats [loser1] [loser2]")
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

        elif string[0] == "$whatIf" or string[0] == "$whatif":
            try:
                if playerExists(string[1]) and playerExists(string[3]):
                    winner = [p for p in players if p.name == string[1]][0]
                    loser = [p for p in players if p.name == string[3]][0]
                    whatif = winner.whatif(loser)
                    sendMessage(winner.name + " -> " + str(int(round(whatif[0]))) + "\n" + loser.name + " -> " + str(int(round(whatif[1]))))
            except IndexError:
                sendMessage("Your command is in the wrong format. \nTry \n$whatIf [winner] defeats [loser]")

        elif string[0] == "$playerHistory":
            try:
                if playerExists(string[1]):
                    player = [p for p in players if p.name == string[1]][0]
                    string = player.name + ":\n"
                    for s in [str(h) for h in player.history]:
                        string += s + "\n"
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

        elif string[0] == "$versus":
            try:
                if playerExists(string[1]) and playerExists(string[2]):
                    playerA = [p for p in players if p.name == string[1]][0]
                    playerB = [p for p in players if p.name == string[2]][0]
                    record = playerA.versus.get(playerB)
                    sendMessage(playerA.name + " has a " + str(record) + " against " + playerB.name)
            except IndexError:
                sendMessage("Your command is in the wrong format. \nTry \n$versus [winner] [loser]")

        elif string[0] == "$outliers":
            out = calculateOutliers()
            sendMessage(out)

        elif string[0] == "$chance":
            try:
                if playerExists(string[1]) and playerExists(string[3]):
                    winner = [p for p in players if p.name == string[1]][0]
                    loser = [p for p in players if p.name == string[3]][0]
                    winnerChance, loserChance = winner.chance(loser)
                    sendMessage("Probability " + winner.name + " wins: " + str(round(winnerChance,1)*100) +
                                "%\nProbability " + loser.name + " wins: " + str(round(loserChance,1)*100) + "%")
            except IndexError:
                sendMessage("Your command is in the wrong format. \nTry \n$chance [winner] defeats [loser]")

        elif string[0] == "$Kscore":
            if len(string)>1 and string[1].isdigit():
                K = int(string[1])
                readMatchesFromFile()
                players.sort()
                d = [[p.name, "(" + str(p.wins) + ", " + str(p.losses) + ")", int(round(p.rating))] for p in players]
                df = DataFrame(data=d, columns=["Name", "Record", "Rating"],
                               index=["#" + str(i + 1) + ". " for i in range(len(players))])

                message = "" + df.to_string(header=False) + "\n\n"
                # print message
                sendMessage(message)
            else:
                senderName("Plese enter a number")

        elif string[0] == "$commands" or string[0] == "$help":
            sendMessage(">$match [winner] defeats [loser]\n"
                        "$teamMatch [winner1] [winner2] def [loser1] [loser2]\n"
                        "$score\n"
                        "$playerHistory [player]\n"
                        "$matchHistory\n"
                        "$whatif [winner] defeats [loser]\n"
                        "$outliers\n"
                        "$chance [winner] defeats [loser]\n"
                        "$versus [player1] [player2]"
                        "$Kscore [number]\n"
                        "$commands")

        elif string[0].lower() == "$fuckme":
            sendMessage("No.")

        else:
            # message starts with $ but there is not recognized command
            if senderName == "Brian Acosta":
                sendMessage("Not valid command")
                #sendMessage("Stop fucking with me Brian")
                #brian = [p for p in players if p.name == "Brian"][0]
                #sendMessage("Brian: " + str(brian.rating) + " -> 0")
            else:
                sendMessage("Not valid command")


def renderHTML():
    d = [[p.name, "(" + str(p.wins) + ", " + str(p.losses) + ")", int(round(p.rating))] for p in players]
    df = DataFrame(data=d, columns=["Name", "Record", "Rating"],
                   index=["#" + str(i + 1) + ". " for i in range(len(players))])

    f = open("score.html", mode='w')
    f.write(df.style.render())
    f.close()


def main(FI):
    global K
    global startRating
    global matchResult
    global fileImport
    global players

    #setupParser()
    K = int(os.environ.get("K_VALUE"))
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



