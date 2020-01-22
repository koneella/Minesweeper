"""
Samu Ahola
Janne Korhonen

"""

import random
import math
import time
import datetime
import haravasto

numerot = ["1", "2", "3", "4", "5", "6", "7", "8", "9"]

tila = {
    "kentta": [],
    "nakyvakentta": [],
    "gameRunning": True,
    "playerWon": False,
    "clickCount": 0,
    "start_time": 0,
    "end_time": 0,
    "korkeus": 0,
    "leveys": 0,
    "miinat": 0
}

mouse = {
    haravasto.HIIRI_VASEN: "vasen",
    haravasto.HIIRI_OIKEA: "oikea",
    haravasto.HIIRI_KESKI: "keski"
}


def kasittele_hiiri(x, y, hiiri, muokkaus):
    """
    Hiiren klikkauksien käsittelijä.
    """

    if haravasto.MOD_SHIFT & muokkaus:
        print("Shift oli pohjassa kun klikkasit!")

    x = math.ceil(x/40) - 1
    y = math.ceil(y/40) - 1

    tila["clickCount"] += 1

    if tila["clickCount"] == 1:
        tila["start_time"] = time.time()

    if tila["gameRunning"] == True:
        # Miina
        if tila["kentta"][y][x] == "x" and mouse.get(hiiri) == "vasen" \
            and not tila["nakyvakentta"][y][x] == "f":
            tila["nakyvakentta"] = tila["kentta"]
            tila["end_time"] = time.time()
            tila["gameRunning"] = False
        # Numero
        elif tila["kentta"][y][x] in numerot and mouse.get(hiiri) == "vasen":
            tila["nakyvakentta"][y][x] = tila["kentta"][y][x]
        # Tyhjä
        elif tila["kentta"][y][x] == "0" and mouse.get(hiiri) == "vasen":
            tulvataytto(tila["kentta"], x, y)
        # Lippu avaamattomaan
        elif tila["nakyvakentta"][y][x] == " " and mouse.get(hiiri) == "oikea":
            tila["nakyvakentta"][y][x] = "f"
        # Lippu pois
        elif tila["nakyvakentta"][y][x] == "f" and mouse.get(hiiri) == "oikea":
            tila["nakyvakentta"][y][x] = " "


def tulvataytto(kentta, aloitusX, aloitusY):
    """
    Täyttää tyhjät tilat ja reunimmaiset numerot.
    """

    tulvalista = [(aloitusX, aloitusY)]

    tarkastetut = []

    row_limit = len(kentta)
    column_limit = len(kentta[0])

    while tulvalista:
        x, y = tulvalista.pop(-1)
        if ((x, y)) not in tarkastetut and x >= 0 and y >= 0:
            for i in range(max(0, y-1), min(row_limit, y+2)):
                for j in range(max(0, x-1), min(column_limit, x+2)):
                    if (j, i) != (x, y) and kentta[i][j] == "0":
                        tulvalista.insert(0, (j, i))
                        tila["nakyvakentta"][y][x] = kentta[i][j]
                        paljasta_numerot(j, i, tila["kentta"])
        tarkastetut.append((x, y))


def piirra_kentta():
    """
    Käsittelijäfunktio, joka piirtää kaksiulotteisena listana kuvatun miinakentän
    ruudut näkyviin peli-ikkunaan. Funktiota kutsutaan aina kun pelimoottori pyytää
    ruudun näkymän päivitystä.

    tyhjaa_ikkuna (pyyhkii edellisen kierroksen grafiikat pois)
    piirra_tausta (asettaa ikkunan taustavärin)
    piirra_tekstia (kirjoittaa ruudulle tekstiä)
    aloita_ruutujen_piirto (kutsutaan ennen varsinaisen ruudukon piirtoa)
    lisaa_piirrettava_ruutu (lisää piirrettävän ruudun)
    piirra_ruudut (piirtää kaikki aloituksen jälkeen lisätyt ruudut)
    """

    haravasto.tyhjaa_ikkuna()
    haravasto.piirra_tausta()
    haravasto.aloita_ruutujen_piirto()

    for y, rivi in reversed(list(enumerate(tila["nakyvakentta"]))):
        for x, ruutu in enumerate(rivi):
            haravasto.lisaa_piirrettava_ruutu(ruutu, x * 40, y * 40)

    haravasto.piirra_ruudut()

    tyhjat = sum(x.count(' ') for x in tila["nakyvakentta"])
    liput = sum(x.count('f') for x in tila["nakyvakentta"])

    if tyhjat + liput == tila["miinat"]:
        tila["end_time"] = time.time()
        tila["playerWon"] = True
        tila["nakyvakentta"] = tila["kentta"]
        tila["gameRunning"] = False

    if tila["gameRunning"] == False and tila["playerWon"] == False:
        haravasto.piirra_tekstia(
            "Hävisit", 0, 0, (255, 0, 0, 255), "Comic Sans MS", 50)
    elif tila["gameRunning"] == False and tila["playerWon"] == True:
        haravasto.piirra_tekstia(
            "Voitit", 0, 60, (255, 0, 0, 255), "Comic Sans MS", 50)


def kirjoita_tulos(vuorot, lopputulos):
    aika = tila["end_time"] - tila["start_time"]
    file = open("tulokset.txt", "a")
    file.write("Pelikentta: {korkeus}x{leveys}, Miinoja: {miinat}, Pelin kesto: {kesto:.1f}s, \
         Vuorot: {vuorot}, Lopputulos: {lopputulos}, Paivamaara: {päivämäärä} {newline}"
        .format(korkeus=tila["korkeus"], leveys=tila["leveys"], miinat=tila["miinat"], \
                päivämäärä=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), kesto=aika, \
                vuorot=vuorot, lopputulos=lopputulos, newline="\n"))


def laske_miinat(x, y, pelikentta):
    miinat = 0
    koordinaatit = [x, y]

    if pelikentta[y][x] == 'x':
        return

    for loopX in range(-1, 2):
        for loopY in range(-1, 2):
            X = koordinaatit[0] + loopX
            Y = koordinaatit[1] + loopY
            if X >= 0 and Y >= 0:
                if X <= len(pelikentta[0]) - 1 and Y <= len(pelikentta) - 1:
                    if pelikentta[Y][X] == 'x':
                        miinat += 1

    tila["kentta"][y][x] = str(miinat)


def paljasta_numerot(x, y, pelikentta):

    koordinaatit = [x, y]

    for loopX in range(-1, 2):
        for loopY in range(-1, 2):
            X = koordinaatit[0] + loopX
            Y = koordinaatit[1] + loopY
            if X >= 0 and Y >= 0:
                if X <= len(pelikentta[0]) - 1 and Y <= len(pelikentta) - 1:
                    if pelikentta[Y][X] in numerot:
                        tila["nakyvakentta"][Y][X] = tila["kentta"][Y][X]


def miinoita(kentta, vapaat_ruudut, miinalkm):
    for _ in range(miinalkm):
        miinaloc = random.choice(vapaat_ruudut)
        vapaat_ruudut.remove(miinaloc)
        x, y = miinaloc
        kentta[y][x] = "x"


def main():
    """
    Lataa pelin grafiikat, luo peli-ikkunan ja asettaa siihen piirtokäsittelijän.
    """
    haravasto.lataa_kuvat("spritet")
    haravasto.luo_ikkuna(tila["leveys"]*40, tila["korkeus"]*40)
    haravasto.aseta_piirto_kasittelija(piirra_kentta)
    haravasto.aseta_hiiri_kasittelija(kasittele_hiiri)
    haravasto.aloita()

    piirra_kentta()

    if tila["gameRunning"] == False and tila["playerWon"] == True:
        kirjoita_tulos(tila["clickCount"], "Voitto")
    else:
        kirjoita_tulos(tila["clickCount"], "Havio")


def aloita():

    tila["gameRunning"] = True
    tila["playerWon"] = False
    tila["start_time"] = 0
    tila["end_time"] = 0
    tila["clickCount"] = 0

    while 1:
        print("Kentän minimikoko 3x3. Miinoja on oltava ainakin 1.")
        try:
            tila["korkeus"] = int(input("Korkeus: "))
            tila["leveys"] = int(input("Leveys: "))
            tila["miinat"] = int(input("Miinojen määrä: "))
            if tila["korkeus"] < 3 or tila["leveys"] < 3 or tila["miinat"] < 0:
                raise Exception("Liian pieni")
        except ValueError:
            print("Viallinen syöte")
        else:
            kentta = []
            nakyvakentta = []
            for _ in range(tila["korkeus"]):
                kentta.append([])
                nakyvakentta.append([])
                for _ in range(tila["leveys"]):
                    kentta[-1].append(" ")
                    nakyvakentta[-1].append(" ")

            tila["kentta"] = kentta
            tila["nakyvakentta"] = nakyvakentta

            jaljella = []
            for x in range(tila["leveys"]):
                for y in range(tila["korkeus"]):
                    jaljella.append((x, y))

            miinoita(kentta, jaljella, tila["miinat"])

            for x in range(tila["leveys"]):
                for y in range(tila["korkeus"]):
                    laske_miinat(x, y, kentta)

            main()
            return


def tulokset():
    file = open("tulokset.txt", "r")

    f1 = file.readlines()
    for tulos in f1:
        print(tulos)


def lopeta():
    print("Kiitos pelaamisesta")
    exit()


if __name__ == "__main__":
    while 1:
        try:
            valinta = int(
                input("1: Aloita peli\n2: Tulokset \n3: Lopeta \n> "))
        except ValueError:
            print("Vain numerot!")
        else:
            if valinta == 1:
                aloita()
            elif valinta == 2:
                tulokset()
            elif valinta == 3:
                lopeta()
            else:
                print("Vain valinnat 1, 2 tai 3")
