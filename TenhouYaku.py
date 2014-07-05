import TenhouDecoder
import collections
from Data import Data

YakuHanCounter = collections.namedtuple('YakuHanCounter', 'yaku han')

class YakuCounter(Data):
    def __init__(self):
        self.hands = collections.Counter()
        self.closed = YakuHanCounter(collections.Counter(), collections.Counter())
        self.opened = YakuHanCounter(collections.Counter(), collections.Counter())

    def addGame(self, game):
        for round in game.rounds:
            self.addRound(round)

    def addRound(self, round):
        for agari in round.agari:
            self.addAgari(agari)
    
    def addAgari(self, agari):
        counterYaku, counterHan = self.closed if agari.closed else self.opened
        self.hands["closed" if agari.closed else "opened"] += 1
        if hasattr(agari, 'yaku'):
            for yaku, han in agari.yaku.items():
                counterYaku[yaku] += 1
                counterHan[yaku] += han

if __name__ == '__main__':
    import sys
    import yaml
    counter = YakuCounter()
    for path in sys.argv[1:]:
        game = TenhouDecoder.Game()
        print(path)
        game.decode(open(path))
        counter.addGame(game)
    yaml.dump(counter.asdata(), sys.stdout, default_flow_style=False, allow_unicode=True)
        
