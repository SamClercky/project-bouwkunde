import re
import matplotlib.pyplot as plt
import numpy as np

from typing import List


reN = re.compile(r'\nN:\W*(\d+)')
reh1 = re.compile(r'\nh1:\W*(\d+\.?\d+)')
reh2 = re.compile(r'\nh2:\W*(\d+\.?\d+)')
red1a = re.compile(r'\nd1a:\W*(\d+\.?\d+)')
red1b = re.compile(r'\nd1b:\W*(\d+\.?\d+)')
red2a = re.compile(r'\nd2a:\W*(\d+\.?\d+)')
red2b = re.compile(r'\nd2b:\W*(\d+\.?\d+)')

reN1 = re.compile(r'\tN1: (\d+\.?\d+)')
reN2 = re.compile(r'\tN2: (\d+\.?\d+)')
reDoorbuiging = re.compile(r'\nMaximale doorbuiging:\n\t(\d+\.\d+)')

reI1a = re.compile(r'\tI1a: (\d+\.?\d+..\d+)')
reI1b = re.compile(r'\tI1b: (\d+\.?\d+..\d+)')
reI2a = re.compile(r'\tI2a: (\d+\.?\d+..\d+)')
reI2b = re.compile(r'\tI2b: (\d+\.?\d+..\d+)')

reScore = re.compile(r'\nScore brug: (\d+\.?\d+e?.\d?\d?)')


def read_from_file(file: str):
    contents = []
    with open(file, 'r') as io:
        for line in io:
            if line.strip() == "[*] Start brug berekenen":
                contents.append("")
            else:
                if len(contents) > 0:
                    contents[-1] += line
    return contents


def to_brug(data: str):
    try:
        N = int(reN.search(data).group(1))
        h1 = float(reh1.search(data).group(1))
        h2 = float(reh2.search(data).group(1))
        d1a = float(red1a.search(data).group(1))
        d1b = float(red1b.search(data).group(1))
        d2a = float(red2a.search(data).group(1))
        d2b = float(red2b.search(data).group(1))
        
        return h1, h2, d1a, d2a, d1b, d2b, N
    except AttributeError:
        return None, None, None, None, None, None, None


def get_max_kracht_doorbuiging(data: str):
    try:
        N1 = float(reN1.search(data).group(1))
        N2 = float(reN2.search(data).group(1))
        doorbuiging = float(reDoorbuiging.search(data).group(1))

        return N1, N2, doorbuiging
    except AttributeError:
        return None, None, None


def get_I(data: str):
    try:
        I1a = float(reI1a.search(data).group(1))
        I1b = float(reI1b.search(data).group(1))
        I2a = float(reI2a.search(data).group(1))
        I2b = float(reI2b.search(data).group(1))
        
        return I1a, I1b, I2a, I2b
    except AttributeError:
        return None, None, None, None


def get_score(data: str):
    score = reScore.search(data)
    if score is None:
        return None
    return float(score.group(1))


def create_rapport(bruggen: List[str]):
    h1, h2, N = list(zip(*[( \
        to_brug(brug)[0], \
        to_brug(brug)[1], \
        to_brug(brug)[6]) for brug in bruggen]))
    h1, h2, N = np.array(h1), np.array(h2), np.array(N)

    plt.figure()
    plt.scatter(h1[h1!=None], h2[h2!=None])
    plt.title("Hoogtes pilaren")
    plt.xlabel("Hoogte pilaar 1")
    plt.ylabel("Hoogte pilaar 2")

    N1, N2, DSNEDE = list(zip(*[
        get_max_kracht_doorbuiging(brug)
        for brug in bruggen]))
    N1, N2, DSNEDE = np.array(N1), np.array(N2), np.array(DSNEDE)

    plt.figure()
    plt.hist(N1[N1!=None], density=True)
    plt.title("Maximale kracht in pilaar 1")
    plt.xlabel("Kracht (N)")
    plt.ylabel("Frequentie (%)")

    plt.figure()
    plt.hist(N2[N2!=None], density=True)
    plt.title("Maximale kracht in pilaar 2")
    plt.xlabel("Kracht (N)")
    plt.ylabel("Frequentie (%)")

    plt.figure()
    plt.hist(DSNEDE[DSNEDE!=None]*1000, density=True)
    plt.title("Maximale doorbuiging")
    plt.xlabel("Doorbuiging (mm)")
    plt.ylabel("Frequentie (%)")

    plt.figure()
    plt.hist(N[N!=None], density=True)
    plt.title("Aantal tuien")
    plt.xlabel("# tuien")
    plt.ylabel("Frequentie (%)")

    I1a, I1b, I2a, I2b = list(zip(*[get_I(brug) for brug in bruggen]))
    I1a, I1b, I2a, I2b = np.array(I1a), \
        np.array(I1b), \
        np.array(I2a), \
        np.array(I2b)

    plt.figure()
    plt.scatter(I1a[I1a!=None], I1b[I1b!=None])
    plt.title("Verspreiding maximale I in pilaar 1")
    plt.xlabel("I richting tuien")
    plt.ylabel("I loodrecht op tuien")

    plt.figure()
    plt.scatter(I2a[I1a!=None], I2b[I1b!=None])
    plt.title("Verspreiding maximale I in pilaar 2")
    plt.xlabel("I richting tuien")
    plt.ylabel("I loodrecht op tuien")

    score = np.array([get_score(brug) for brug in bruggen])

    plt.figure()
    plt.plot(score[score!=None])
    plt.title("Verschillende scores van bruggen")
    plt.xlabel("Score")
    plt.ylabel("Frequentie (%)")
