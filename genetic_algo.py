import numpy as np

# Maxwaarden
h1_max = 2 # 2m
h2_max = 2 # 2m
h1_min = 0.06 # 6cm
h2_min = 0.06 # 6cm
d1_max = 2 # 2m
d2_max = 2 # 2m
d1_min = 0.1 # 10cm
d2_min = 0.1 # 10cm
N_max = 10
N_min = 1

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
    print(f"d1:\t{brug.d1}")
    print(f"d2:\t{brug.d2}")
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
    return (
        h1_min + random()*(h1_max - h1_min),
        h2_min + random()*(h2_max - h2_min),
        d1_min + random()*(d1_max - d1_min),
        d2_min + random()*(d2_max - d2_min),
        randint(N_min, N_max),
    )

def genRandomBrugA():
    from berekeningen_andreas import Brug

    return Brug(*_genRandomBrugVars())

def _genParentVars(p1, p2):
    import random
    h1 = (p1.h1 if random.choice([True, False]) else p2.h1) + random.gauss(0,1)
    h2 = (p1.h2 if random.choice([True, False]) else p2.h2) + random.gauss(0,1)
    d1 = (p1.d1 if random.choice([True, False]) else p2.d1) + random.gauss(0,1)
    d2 = (p1.d2 if random.choice([True, False]) else p2.d2) + random.gauss(0,1)
    N = (p1.N if random.choice([True, False]) else p2.N) + int(random.gauss(0,N_max/2))

    return (
        clamp(h1, h1_min, h1_max),
        clamp(h2, h2_min, h2_max),
        clamp(d1, d1_min, d1_max),
        clamp(d2, d2_min, d2_max),
        clamp(N, N_min, N_max)
    )

def genFromParentsA(p1, p2):
    from berekeningen_andreas import Brug

    return Brug(*_genParentVars(p1, p2))

    