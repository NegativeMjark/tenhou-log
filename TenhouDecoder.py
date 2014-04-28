#! /usr/bin/python3

import xml.etree.ElementTree as etree
import urllib.parse

class Data:
    @property
    def data(self):
        def convert(obj, convert):
            if isinstance(obj, Data):
                return obj.data
            elif isinstance(obj, str):
                return obj
            else:
                try:
                    return list(convert(child, convert) for child in obj)
                except:
                    return obj
        return dict((k, convert(v, convert)) for (k, v) in self.__dict__.items())

    def __repr__(self):
        return self.data.__repr__()

class Player(Data):
    pass    

class Round(Data):
    pass

class Meld(Data):
    @classmethod
    def decode(Meld, data):
        meld = Meld()
        meld.fromPlayer = data & 0x3
        if data & 0x4:
            meld.decodeChi(data)
        elif data & 0x18:
            meld.decodePon(data)
        elif data & 0x20:
            meld.decodeNuki(data)
        else:
            meld.decodeKan(data)
        return meld

    def decodeChi(self, data):
        self.type = "chi"
        t0, t1, t2 = (data >> 3) & 0x3, (data >> 5) & 0x3, (data >> 7) & 0x3
        baseAndCalled = data >> 10
        self.called = baseAndCalled % 3
        base = baseAndCalled // 3
        base = (base // 7) * 9 + base % 7
        self.tiles = t0 + 4 * (base + 0), t1 + 4 * (base + 1), t2 + 4 * (base + 2)
    
    def decodePon(self, data):
        t4 = (data >> 5) & 0x3
        t0, t1, t2 = ((1,2,3),(0,2,3),(0,1,3),(0,1,2))[t4]
        baseAndCalled = data >> 9
        self.called = baseAndCalled % 3
        base = baseAndCalled // 3
        if data & 0x8:
            self.type = "pon"
            self.tiles = t0 + 4 * base, t1 + 4 * base, t2 + 4 * base
        else:
            self.type = "chakan"
            self.tiles = t0 + 4 * base, t1 + 4 * base, t2 + 4 * base, t4 + 4 * base
    
    def decodeKan(self, data):
        baseAndCalled = data >> 8
        if self.fromPlayer:
            self.called = baseAndCalled % 4
        else:
            del self.fromPlayer
        base = baseAndCalled // 4
        self.type = "kan"
        self.tiles =  4 * base, 1 + 4 * base, 2 + 4 * base, 3 + 4 * base

class Event(Data):
    def __init__(self, events):
        events.append(self)
        self.type = type(self).__name__

class Dora(Event):
    pass

class Draw(Event):
    pass

class Discard(Event):
    pass

class Call(Event):
    pass

class Tsumo(Event):
    pass

class RiichiCalled(Event):
    pass

class RiichiStick(Event):
    pass

class Game(Data):
    RANKS = "新人,9級,8級,7級,6級,5級,4級,3級,2級,1級,初段,二段,三段,四段,五段,六段,七段,八段,九段,十段".split(",")
    NAMES = "n0,n1,n2,n3".split(",")
    HANDS = "hai0,hai1,hai2,hai3".split(",")
    ROUND_NAMES = "東1,東2,東3,東4,南1,南2,南3,南4,西1,西2,西3,西4,北1,北2,北3,北4".split(",")
    TAGS = {}
    
    def tagGO(self, tag, data):
        self.gameType = data["type"]
        self.lobby = data["lobby"]

    def tagUN(self, tag, data):
        if "dan" in data:
            for name in self.NAMES:
                if name in data:
                    player = Player()
                    player.name = urllib.parse.unquote(data[name])
                    self.players.append(player)
            ranks = self.decodeList(data["dan"])
            sexes = self.decodeList(data["sx"], dtype = str)
            rates = self.decodeList(data["rate"], dtype = float)
            for (player, rank, sex, rate) in zip(self.players, ranks, sexes, rates):
                player.rank = self.RANKS[rank]
                player.sex = sex
                player.rate = rate
                player.connected = True
        else:
            for (player, name) in zip(self.players, self.NAMES):
                if name in data:
                    player.connected = True
    
    def tagBYE(self, tag, data):
        self.players[int(data["who"])].connected = False

    def tagINIT(self, tag, data):
        self.round = Round()
        self.rounds.append(self.round)
        name, combo, riichi, d0, d1, dora = self.decodeList(data["seed"])
        self.round.round = self.ROUND_NAMES[name], combo, riichi
        self.round.hands = tuple(self.decodeList(data[hand]) for hand in self.HANDS if hand in data)
        self.round.dealer = int(data["oya"])
        self.round.events = []
        Dora(self.round.events).tile = dora

    def tagN(self, tag, data):
        call = Call(self.round.events)
        call.meld = Meld.decode(int(data["m"]))
        call.player = int(data["who"])

    def tagTAIKYOKU(self, tag, data):
        pass

    def tagDORA(self, tag, data):
         Dora(self.round.events).tile = int(data["hai"])

    @staticmethod
    def default(self, tag, data):
        if tag[0] in "DEFG":
            discard = Discard(self.round.events)
            discard.tile = int(tag[1:])
            discard.player = ord(tag[0]) - ord("D")
        elif tag[0] in "TUVW":
            draw = Draw(self.round.events)
            draw.tile = int(tag[1:])
            draw.player = ord(tag[0]) - ord("T")
        else:
            pass

    @staticmethod
    def decodeList(list, dtype = int):
        return tuple(dtype(i) for i in list.split(","))

    def decode(self, log):
        events = etree.parse(log).getroot()
        self.rounds = []
        self.players = []
        for event in events:
            self.TAGS.get(event.tag, self.default)(self, event.tag, event.attrib)
        del self.round

for key in Game.__dict__:
    if key.startswith('tag'):
        Game.TAGS[key[3:]] = getattr(Game, key)

if __name__=='__main__':
    import yaml
    import sys
    game = Game()
    game.decode(sys.stdin)
    yaml.dump(game.data, sys.stdout, default_flow_style=False, allow_unicode=True)
