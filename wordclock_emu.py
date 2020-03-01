import sys, time, random
mod = type(sys)("DUMMY")
for modname in "machine neopixel ntptime network urandom".split():
    sys.modules[modname] = mod
time.sleep_ms = lambda x: time.sleep(x / 1000.)
import neopixel
neopixel.NeoPixel = lambda *args: None
import machine
machine.Pin = lambda x: None
import urandom
urandom.getrandbits = random.getrandbits
import wordclock


class NeopixelEmu(list):
    def write(self):
        for row in range(wordclock.ROWS):
            for col in range(wordclock.COLS):
                print(self[wordclock.pos2idx(col, row)], end='')
            print()
        print()

wordclock.BLACK = "B"
wordclock.COL = "C"
wordclock.COL_FADED = "C"
wordclock.COL_FADED2 = "F"
np = wordclock.np = NeopixelEmu([wordclock.BLACK] * 110)

w2i = lambda *ws: sum((w.indices() for w in ws), [])

old = w2i(wordclock.es, wordclock.ist, wordclock.zehn, wordclock.uhr)
new = w2i(wordclock.es, wordclock.ist, wordclock.fuenfm, wordclock.nach, wordclock.sechs)
#new = w2i(wordclock.es, wordclock.ist)
for idx in old:
    np[idx] = wordclock.COL
np.write()
wordclock.fade_matrix(old, new)
