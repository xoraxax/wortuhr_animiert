# -*- coding: utf-8
# Wortuhr-Programm in Micropython geschrieben
# (c) 2020 Alexander Schremmer <alex AT alexanderweb DOT de>
# License: AGPL v3
import machine, neopixel, time, ntptime, network, urandom

from wordclock_config import *


COL = (0x24, 0xa7, 0xd5)  # hellblau-türkis
COL = (0xfe, 0x9f, 0x46)  # orange
COL = (0x06, 0xdf, 0x00)  # hellgrün
BLACK = (0, 0, 0)

COEFFS = [0.0] + [1.3**(pct - 16) * .4 for pct in range(0, 16)]

ntptime.host = "de.pool.ntp.org"
SLEEP_TIME_S = 5

ROWS = 10
COLS = 11
TAIL = 5

np = neopixel.NeoPixel(machine.Pin(2), ROWS * COLS)


class Word:
    def __init__(self, from_, word):
        self.from_ = from_
        self.to_ = from_ + len(word) - 1

    def indices(self):
        return list(range(self.from_, self.to_ + 1))

    def turn_on(self):
        for i in self.indices():
            np[i] = COL_FADED

uhr = Word(8, "Uhr")
sechs = Word(1, "sechs")
zehn = Word(13, "zehn")
acht = Word(17, "acht")
elf = Word(22, "elf")
neun = Word(25, "neun")
vier = Word(29, "vier")
fuenf = Word(33, "funf")
drei = Word(39, "drei")
zwei = Word(44, "zwei")
ein = Word(46, "ein")
eins = Word(46, "eins")
sieben = Word(49, "sieben")
zwoelf = Word(56, "zwolf")
halb = Word(62, "halb")
nach = Word(68, "nach")
vor = Word(72, "vor")
viertel = Word(77, "viertel")
dreiviertel = Word(77, "dreiviertel")
zehnm = Word(88, "zehn")
zwanzigm = Word(92, "zwanzig")
fuenfm = Word(99, "funf")
ist = Word(104, "ist")
es = Word(108, "es")
none = Word(0, "")

hours = [eins, zwei, drei, vier, fuenf, sechs, sieben, acht, neun, zehn, elf, zwoelf]
min5 = [
  [ uhr ],
  [ fuenfm, nach ],
  [ zehnm, nach ],
  [ viertel, nach ],
  [ zwanzigm, nach ],
  [ fuenfm, vor, halb ],
  [ halb ],
  [ fuenfm, nach, halb ],
  [ zwanzigm, vor ],
  [ viertel, vor ],
  [ zehnm, vor ],
  [ fuenfm, vor ],
]


def do_connect():
    wlan = network.WLAN(network.AP_IF)
    wlan.active(False)
    wlan = network.WLAN(network.STA_IF)
    wlan.active(False)
    time.sleep(1)
    wlan.active(True)
    wlan.connect(WIFI_NET, WIFI_KEY)
    time.sleep(1)
    while not wlan.isconnected():
        time.sleep(1)
    print('network config:', wlan.ifconfig())
    ntp_load()

def ntp_load():
    for _ in range(3):
        try:
            ntptime.settime()
            return
        except OSError as e:
            print(e)
    machine.reset()


def cettime():
    year = time.localtime()[0]       #get current year
    HHMarch = time.mktime((year,3 ,(31-(int(5*year/4+4))%7),1,0,0,0,0,0)) #Time of March change to CEST
    HHOctober = time.mktime((year,10,(31-(int(5*year/4+1))%7),1,0,0,0,0,0)) #Time of October change to CET
    now = time.time()
    if now < HHMarch:               # we are before last sunday of march
        cet = time.localtime(now + 3600) # CET:  UTC+1H
    elif now < HHOctober:           # we are before last sunday of october
        cet = time.localtime(now + 7200) # CEST: UTC+2H
    else:                            # we are after last sunday of october
        cet = time.localtime(now + 3600) # CET:  UTC+1H
    return cet



def fade_col(col, q):
    return int(col[0] * q), int(col[1] * q), int(col[2] * q)
ALL_COLS = [fade_col(COL, coeff) for coeff in COEFFS]
COL_FADED = ALL_COLS[-1]


def randrange(start, stop=None):
    if stop is None:
        stop = start
        start = 0
    upper = stop - start
    bits = 0
    pwr2 = 1
    while upper > pwr2:
        pwr2 <<= 1
        bits += 1
    while True:
        r = urandom.getrandbits(bits)
        if r < upper:
            break
    return r + start

def shuffle(seq):
    l = len(seq)
    if l == 1:
        return
    for i in range(l):
        j = randrange(l)
        seq[i], seq[j] = seq[j], seq[i]


def choice(seq):
    return seq[randrange(len(seq)) - 1]


def fade_switch(old, new):
    for coeff_idx in range(len(COEFFS)):
        for idx in old:
            if idx in new:
                continue
            np[idx] = fade_col(COL, COEFFS[-coeff_idx - 1])
        for idx in new:
            if idx in old:
                continue
            np[idx] = fade_col(COL, COEFFS[coeff_idx])
        np.write()
        time.sleep_ms(50)


def pos2idx(col, row):
    idx = 0
    if row % 2:
        idx += col
    else:
        idx += COLS - col - 1
    return idx + COLS * (ROWS - 1 - row)


def idx2colrow(idx):
    row = ROWS - idx // COLS - 1
    col = idx % COLS
    if not (row % 2):
        col = COLS - col - 1
    return col, row


def fade_matrix(old, new):
    remove = []
    add = []
    steady = es.indices() + ist.indices()  # idx not removed by add trail
    steady_late = []  # idx not removed by removal trail
    for idx in old:
        if idx in new:
            steady.append(idx)
            continue
        remove.append(idx)
    for idx in new:
        if idx in old:
            continue
        add.append(idx)
    add_colrow = {}
    remove_colrow = {}
    for idx in add:
        col, row = idx2colrow(idx)
        add_colrow.setdefault(col, []).append(row)
    for idx in remove:
        col, row = idx2colrow(idx)
        remove_colrow.setdefault(col, []).append(row)
    add_colptr = {}
    add_coltail = {}
    remove_colptr = {}
    add_cols = list(add_colrow.keys())
    shuffle(add_cols)
    for i, col in enumerate(add_cols):
        if col in remove_colrow:
            steady_late.extend([pos2idx(col, row) for row in add_colrow[col]])
            del add_colrow[col]
        else:
            add_colptr[col] = -i
            add_coltail[col] = TAIL
    remove_cols = list(remove_colrow.keys())
    shuffle(remove_cols)
    for i, col in enumerate(remove_cols):
        remove_colptr[col] = -i
    while add_colrow or remove_colptr:
        for col, lvl_max in list(add_colptr.items()) + list(remove_colptr.items()):
            if col in add_colptr:
                for lvl in range(0, lvl_max + 1):
                    idx = pos2idx(col, lvl)
                    if lvl <= lvl_max - add_coltail[col]:
                        np[idx] = COL_FADED if idx in steady else BLACK
                    else:
                        np[idx] = choice(ALL_COLS) if lvl != lvl_max else COL
                if add_colptr[col] in add_colrow[col]:
                    if add_coltail.get(col):
                        add_coltail[col] -= 1
                    else:
                        row = add_colptr.pop(col)
                        add_colrow[col].remove(row)
                        idx = pos2idx(col, row)
                        steady.append(idx)
                        np[idx] = COL_FADED
                        rows = add_colrow[col]
                        if rows:
                            add_colptr[col] = 0
                            add_coltail[col] = TAIL
                        else:
                            del add_colrow[col]
                else:
                    add_colptr[col] += 1
            elif col in remove_colptr:
                for lvl in range(0, min(lvl_max + 1, ROWS)):
                    idx = pos2idx(col, lvl)
                    if lvl <= lvl_max - TAIL:
                        np[idx] = COL_FADED if idx in steady or idx in steady_late else BLACK
                    else:
                        np[idx] = choice(ALL_COLS) if lvl != lvl_max else COL
                if lvl_max - TAIL == ROWS:
                    del remove_colptr[col]
                else:
                    remove_colptr[col] += 1
        np.write()
        time.sleep_ms(250)


def fade_single(old, new):
    remove = []
    add = []
    for idx in old:
        if idx in new:
            continue
        remove.append(idx)
    for idx in new:
        if idx in old:
            continue
        add.append(idx)
    shuffle(add)
    shuffle(remove)
    fade_time = int(min(900 / max(len(add), len(remove), 1), 150))
    while remove or add:
        if add:
            np[add.pop()] = COL_FADED
        if remove:
            np[remove.pop()] = BLACK
        np.write()
        time.sleep_ms(fade_time)


def update_time(indices):
    t = cettime()
    hour, minute = t[3:5]
    #hour, minute = i // 60, i % 60  # for testing
    hour %= 12
    minute = (minute + 2) // 5
    ovf = minute >= 12
    minute %= 12

    words = []
    words.extend(min5[minute])
    hour_word = hours[hour if minute >= 5 or ovf else hour - 1]
    if not minute or ovf:
        if hour == 1 and not ovf or not hour and ovf:
            hour_word = ein
        words.append(uhr)
    words.append(hour_word)
    new_indices = sum([word.indices() for word in words], [])
    if indices != new_indices:
        method = fade_matrix
        method(indices, new_indices)
    return new_indices


def main():
    global i
    for i in range(0, 110):
        np[i] = BLACK
    np.write()

    es.turn_on()
    ist.turn_on()
    do_connect()

    i = 0
    indices = []
    while True:
        i += 1
        i %= 240 // SLEEP_TIME_S
        if not i:
            print("Setting Time via NTP")
            ntp_load()
        indices = update_time(indices)
        time.sleep(SLEEP_TIME_S)

main()
