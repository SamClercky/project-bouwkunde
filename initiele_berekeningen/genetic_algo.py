import numpy as np

# Maxwaarden
h1_max = 0.70 # 60cm
h2_max = 0.70 # 60cm
h1_min = 0.10 # 20cm
h2_min = 0.10 # 20cm

d1_max = 1 # 2m
d2_max = 1 # 2m
d1_min = 0.05 # 5cm
d2_min = 0.05 # 5cm

d1a_max = 1 # 2m
d2a_max = 1 # 2m
d1a_min = 0.05 # 5cm
d2a_min = 0.05 # 5cm

d1b_max = 2 # 2m
d2b_max = 2 # 2m
d1b_min = 0.05 # 5cm
d2b_min = 0.05 # 5cm

N_max = 6
N_min = 6

def find_best(population):
    scores = [[brug.calc_fitness(), brug] for brug in population]
    scores = sorted(scores, key=lambda score: score[0])
    return scores[0]

def print_brug(brug):
    import matplotlib.pyplot as plt

    x = np.arange(0, max([brug.h1, brug.h2, 2]), 0.001)
    N1, _, _ = list(zip(*[brug.calc_intern_balk(xi, True) for xi in x]))
    N2, _, _ = list(zip(*[brug.calc_intern_balk(xi, False) for xi in x]))
    _, D, _ = list(zip(*[brug.calc_intern_wegdek(xi) for xi in x]))
    I1a, I1b = list(zip(*[brug.calc_piloon_I(x, True) for x in np.arange(0, brug.h1, 0.01)]))
    I2a, I2b = list(zip(*[brug.calc_piloon_I(x, False) for x in np.arange(0, brug.h2, 0.01)]))
    doorbuiging = [brug.calc_doorbuiging_wegdek(x) for x in np.arange(0, 2.0, 0.01)]

    fig = plt.figure()
    ax1 = plt.subplot(3, 1, 1)
    ax1.plot(x, N1)
    ax1.set_ylabel("N1")
    ax2 = plt.subplot(3, 1, 2)
    ax2.plot(x, N2)
    ax2.set_ylabel("N2")
    ax3 = plt.subplot(3, 1, 3)
    ax3.plot(x, D)
    ax3.set_ylabel("D")
    
    print("======= Info Brug ========")
    print(f"h1:\t{brug.h1}")
    print(f"h2:\t{brug.h2}")
    print(f"d1a:\t{brug.d1a}")
    print(f"d2a:\t{brug.d2a}")
    print(f"d1b:\t{brug.d1b}")
    print(f"d2b:\t{brug.d2b}")
    print(f"N:\t{brug.N}")

    print("Krachten in touwen A")
    for F in brug.FiA:
        print(f"\t{F}")
    print("Krachten in touwen B")
    for F in brug.FiB:
        print(f"\t{F}")
    print("Krachten in touwen C")
    for F in brug.FiC:
        print(f"\t{F}")
    print("Krachten in touwen D")
    for F in brug.FiD:
        print(f"\t{F}")
    print("Maximale kracht trek/druk:")
    print(f"\tN1: {np.max(np.abs(N1))}")
    print(f"\tN2: {np.max(np.abs(N2))}")
    print(f"\tD: {np.max(np.abs(D))}")

    print("Maximale I:")
    print(f"\tI1a: {np.max(np.abs(I1a))}")
    print(f"\tI1b: {np.max(np.abs(I1b))}")
    print(f"\tI2a: {np.max(np.abs(I2a))}")
    print(f"\tI2b: {np.max(np.abs(I2b))}")

    print("Maximale doorbuiging:")
    print(f"\t{np.max(np.abs(doorbuiging))}")

    return fig

def kill_population(population):
    scores = [[brug.calc_fitness(), brug] for brug in population]
    scores = sorted(scores, key=lambda score: score[0])
    # delete half the population #Thanos-feeling
    scores = scores[:len(scores)//2]
    return list(zip(*scores))[1]

def regen_population(population, genRandomBrugFunc, genFromParentsFunc):
    new_p = [genFromParentsFunc(population[i], population[i+1]) for i in range(0, len(population), 2)]
    return [*population,
            *new_p,
            *[genRandomBrugFunc() for _ in range(len(population)//2)]]

def clamp(x, mini, maxi):
    return min(maxi, max(mini, x))

def _genRandomBrugVars():
    from random import random, randint
    h1 = h1_min + random()*(h1_max - h1_min)
    #h2 = h2_min + random()*(h2_max - h2_min)
    h2 = h1/2
    d1a = d1a_min + random()*(d1a_max - d1a_min)
    d2a = d2a_min + random()*(d2a_max - d2a_min)
    d1b = d1b_min + random()*(d1b_max - d1b_min)
    d2b = d2b_min + random()*(d2b_max - d2b_min)
    N = randint(N_min, N_max)

    return (h1, h2, max(d1a, d1b+0.1), max(d2a, d2b+0.1), d1b, d2b, N)

def genRandomBrugA():
    from berekeningen_andreas import Brug

    return Brug(*_genRandomBrugVars())

def genRandomBrugB():
    from berekeningen_ramses import Brug

    return Brug(*_genRandomBrugVars())


def genRandomBrugVlot():
    from berekeningen_1piloon import Brug
    from random import random, randint

    h = h1_min + random()*(h1_max - h1_min)
    da = d1a_min + random()*(d1a_max - d1a_min)
    db = d1b_min + random()*(d1b_max - d1b_min)
    N = randint(N_min, N_max)

    return Brug(
        h,
        max(da, db+0.1),
        db,
        np.random.uniform(0, 2, N),
    )


def _genParentVars(p1, p2):
    import random
    h1  = clamp((p1.h1 if random.choice([True, False]) else p2.h1) + random.gauss(0,1), h1_min, h1_max)
    #h2  = clamp((p1.h2 if random.choice([True, False]) else p2.h2) + random.gauss(0,1), h2_min, h2_max)
    h2 = h1/2
    d1a = clamp((p1.d1a if random.choice([True, False]) else p2.d1a) + random.gauss(0,1), d1a_min, d1a_max)
    d2a = clamp((p1.d2a if random.choice([True, False]) else p2.d2a) + random.gauss(0,1), d2a_min, d2a_max)
    d1b = clamp((p1.d1b if random.choice([True, False]) else p2.d1b) + random.gauss(0,1), d1b_min, d1b_max)
    d2b = clamp((p1.d2b if random.choice([True, False]) else p2.d2b) + random.gauss(0,1), d2b_min, d2b_max)
    N   = clamp((p1.N if random.choice([True, False]) else p2.N) + int(random.gauss(0,N_max/2)), N_min, N_max)

    return (h1, h2, max(d1a, d1b+0.1), max(d2a, d2b+0.1), d1b, d2b, N)

def genFromParentsA(p1, p2):
    from berekeningen_andreas import Brug

    return Brug(*_genParentVars(p1, p2))


def genFromParentsB(p1, p2):
    from berekeningen_ramses import Brug

    return Brug(*_genParentVars(p1, p2))


def genFromParentsVlot(p1, p2):
    from berekeningen_1piloon import Brug
    import random

    h  = clamp((p1.h if random.choice([True, False]) else p2.h) + random.gauss(0,1), h1_min, h1_max)
    da = clamp((p1.da if random.choice([True, False]) else p2.da) + random.gauss(0,1), d1a_min, d1a_max)
    db = clamp((p1.db if random.choice([True, False]) else p2.db) + random.gauss(0,1), d1b_min, d1b_max)
    N = [*p1.N, *p2.N]
    np.random.shuffle(N)
    N = np.clip(N + np.random.normal(size=len(N)), N_min, N_max)
    N = np.sort(N[:int((len(p1.N)+len(p2.N))//2)])

    return Brug(
        h,
        max(da, db+0.1),
        db,
        N,
    )
