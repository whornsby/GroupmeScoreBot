import  math
import config


class Player:
    def __init__(self, name, rating=1000.0,wins=0,loses=0):
        self.name = name
        self.rating = float(rating)
        self.wins = wins
        self.losses = wins


def match(winner, loser):
    k = config.getKValue()
    # look at wiki page for elo ratings for references
    winnerExp = 1.0 / (1.0 + math.pow(10.0, (loser.rating - winner.rating) / 400.0))
    loserExp = 1.0 / (1.0 + math.pow(10.0, (winner.rating - loser.rating) / 400.0))

    winner.rating += float(k * (1 - winnerExp))
    loser.rating -= float(k * loserExp)
    self.wins += 1
    other.losses += 1

