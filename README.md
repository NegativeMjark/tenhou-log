tenhou-log
==========

Scripts for downloading logs from tenhou.net

tenhou-download-game-xml.py
---------------------------

Scans flash local storage for tenhou log file names and then downloads the game xml from tenhou.net.

Log Format
==========

```
<SHUFFLE>
 - seed         Seed for RNG for generating walls and dice rolls.
 - ref          ?
<GO>            Start of game
 - type             Lobby type.
 - lobby            Lobby number.
<UN>            User list or user reconnect
 - n[0-3]           Names for each player as URLEncoded UTF-8.
 - dan              List of ranks for each player.
 - rate             List of rates for each player.
 - sx               List of sex ("M" or "F") for each player.
<BYE>           User disconnect
 - who              Player who disconnected.
<TAIKYOKU>      Start of round
 - oya              Dealer
<INIT>          Start of hand
 - seed             Six element list:
                        Round number,
                        Number of combo sticks,
                        Number of riichi sticks,
                        First dice minus one,
                        Second dice minus one,
                        Dora indicator.
 - ten              List of scores for each player     
 - oya              Dealer
 - hai[0-3]         Starting hands as a list of tiles for each player.
<[T-W][0-9]*>   Player draws a tile.
<[D-G][0-9]*>   Player discards a tile.
<N>             Player calls a tile.
 - who              The player who called the tile.
 - m                The meld.
<REACH>         Player declares riichi.
 - who              The player who declared riichi
 - step             Where the player is in declaring riichi:
                        1 -> Called "riichi"
                        2 -> Placed point stick on table after discarding.
 - ten              List of current scores for each player.
<DORA>          New dora indicator.
 - hai              The new dora indicator tile.
<AGARI>         A player won the hand
 - who              The player who won.
 - fromwho          Who the winner won from: themselves for tsumo, someone else for ron.
 - hai              The closed hand of the winner as a list of tiles.
 - m                The open melds of the winner as a list of melds.
 - machi            The waits of the winner as a list of tiles.
 - doraHai          The dora as a list of tiles.
 - dorahaiUra       The ura dora as a list of tiles.
 - yaku             List of yaku and their han values.
                            0 -> tsumo
                            1 -> riichi
                            2 -> ippatsu
                            3 -> chankan
                            4 -> rinshan
                            5 -> haitei
                            6 -> houtei
                            7 -> pinfu
                            8 -> tanyao
                            9 -> ippeiko
                        10-17 -> fanpai
                        18-20 -> yakuhai
                           21 -> daburi
                           22 -> chiitoi
                           23 -> chanta
                           24 -> itsuu
                           25 -> sanshokudoujin
                           26 -> sanshokudou
                           27 -> sankantsu
                           28 -> toitoi
                           29 -> sanankou
                           30 -> shousangen
                           31 -> honrouto
                           32 -> ryanpeikou
                           33 -> junchan
                           34 -> honitsu
                           35 -> chinitsu
                           52 -> dora
                           53 -> uradora
                           54 -> akadora
 - yakuman          List of yakuman.
                           36 -> renhou
                           37 -> tenhou
                           38 -> chihou
                           39 -> daisangen
                        40,41 -> suuankou
                           42 -> tsuiisou
                           43 -> ryuuiisou
                           44 -> chinrouto
                        45,46 -> chuurenpooto
                        47,48 -> kokushi
                           49 -> daisuushi
                           50 -> shousuushi
                           51 -> suukantsu
 - ten              Three element list:
                        The fu points in the hand,
                        The point value of the hand,
                        The limit value of the hand:
                            0 -> No limit
                            1 -> Mangan
                            2 -> Haneman
                            3 -> Baiman
                            4 -> Sanbaiman
                            5 -> Yakuman
 - ba               Two element list of stick counts:
                        The number of combo sticks,
                        The number of riichi sticks.
 - sc               List of scores and the changes for each player.
 - owari            Final scores including uma at the end of the game.
<RYUUKYOKU>     The hand ended with a draw
 - type             The type of draw: 
                        "yao9"   -> 9 ends
                        "reach4" -> Four riichi calls
                        "ron3"   -> Triple ron
                        "kan4"   -> Four kans
                        "kaze4"  -> Same wind discard on first round
                        "nm"     -> Nagashi mangan.
 - hai[0-3]         The hands revealed by players as a list of tiles.
 - ba               Two element list of stick counts:
                        The number of combo sticks,
                        The number of riichi sticks.
 - sc               List of scores and the changes for each player.
 - owari            Final scores including uma at the end of the game.
```

Meld Format
-----------

```
    CHI

     0                   1
     0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5
    +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
    | Base Tile | |   |   |   | |   |
    |    and    |0| T2| T1| T0|1|Who|   
    |Called Tile| |   |   |   | |   |
    +-----------+-+---+---+---+-+---+

        Base Tile and Called Tile:
            ((Base / 9) * 7 + Base % 9) * 3 + Chi
        T[0-2]:
            Tile[i] - 4 * i - Base * 4
        Who:
            Offset of player the tile was called from.
        Tile[0-2]:
            The tiles in the chi.
        Base:
            The lowest tile in the chi / 4.
        Called:
            Which tile out of the three was called.

    PON or CHAKAN

     0                   1
     0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5
    +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
    |  Base Tile  |   |   |K|P| |   |
    |     and     | 0 | T4|A|O|0|Who|
    | Called Tile |   |   |N|N| |   |
    +---------------+-+---+-+-+-+---+

        Base Tile and Called Tile:
            Base * 3 + Called
        T4:
            Tile4 - Base * 4
        PON:
            Set iff the meld is a pon.
        KAN:
            Set iff the meld is a pon upgraded to a kan.
        Who:
            Offset of player the tile was called from.
        Tile4:
            The tile which is not part of the pon.
        Base:
            A tile in the pon / 4.
        Called:
            Which tile out of the three was called.

    KAN

     0                   1
     0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5
    +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
    |   Base Tile   |           |   |
    |      and      |     0     |Who|
    |   Called Tile |           |   |
    +---------------+-+---+-+-+-+---+

        Base Tile and Called Tile:
            Base * 4 + Called
        Who:
            Offset of player the tile was called from or 0 for a closed kan.
        Base:
            A tile in the kan / 4. 
        Called:
            Which tile out of the four was called.

``` 
