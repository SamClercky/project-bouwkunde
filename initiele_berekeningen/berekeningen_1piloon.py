import math
import numpy as np

from brug import BrugInterface
import constanten as C


class Brug(BrugInterface):

    def __init__(self, h, da, db, N):
        """
        !OPGELET!: N is hier een lijst
        """
        self.h = h
        self.da = da
        self.db = db
        self.N = np.array(N)
        
        assert(np.min(N)>=0)

        self.update_data()

    def update_data(self):
        """
        Bereken automatisch alpha en beta in de constructie
        """

        breette = self.N + self.db
        hoogte = self.h
        hypoth = np.sqrt(breette**2 + hoogte**2)

        self.cosa = breette/hypoth
        self.sina = hoogte/hypoth

        self.P = np.array([0, *self.N, 2])
        self.deeltje = [self.P[i] - self.P[i-1] for i in range(1, len(self.P))]

    def calc_reactie_krachten(self):
        V = []
        for i in range(len(self.deeltje)):
            Va = (C.VERDEELDE_BELASTING+C.EIG_GEWICHT_BRUG)*self.deeltje[i]/2
            Vb = (C.VERDEELDE_BELASTING+C.EIG_GEWICHT_BRUG)*self.deeltje[i]/2

            if i < len(self.N)-2 and self.P[i] <= 2/3 and 2/3 < self.P[i+1]:
                Va += C.PUNT_BELASTING*(self.P[i+1] - 2/3)/self.deeltje[i]
                Vb += C.PUNT_BELASTING*(2/3 - self.P[i])/self.deeltje[i]
            V.append(Va)
            V.append(Vb)

        V = np.array([V[0], *[V[i] + V[i+1] for i in range(1, len(V)-1, 2)], V[-1]])
        self.Vi = V
        return V

    def calc_touw_kracht(self):
        self.FiA = self.Vi[1:-1] / self.sina
        self.FiB = self.FiA * self.cosa

        return self.FiA, self.FiB

    def calc_kant(self):
        breette = self.da - self.db
        hoogte = self.h
        hypoth = math.sqrt(breette**2 + hoogte**2)
        self.cosgam = breette/hypoth
        self.singam = hoogte/hypoth

        # Deel C
        self.FiC = np.sum(self.FiA*self.cosa)/self.cosgam
        self.Vc = -self.FiC*self.cosgam
        self.Hc = -self.FiC*self.singam

        # Deel D
        self.FiD = []
        self.Vd = 0
        self.Hd = -np.sum(self.FiB)

        return self.Vc, self.Hc, self.FiC, self.Vd, self.Hd, self.FiD

    def calc_intern_wegdek(self, x):
        i = min(np.where(self.P >= x)[0][0] - 1, len(self.Vi)-1)
        N = 0
        D = np.sum(self.Vi[:i+1]) \
            - (C.VERDEELDE_BELASTING+C.EIG_GEWICHT_BRUG)*x \
            - (C.PUNT_BELASTING if x >= 2/3 else 0)
        M = np.sum(self.Vi[:i+1]*(x-self.P[:i+1])) \
            - (C.VERDEELDE_BELASTING+C.EIG_GEWICHT_BRUG)*x**2/2 \
            - (C.PUNT_BELASTING*(x-2/3) if x >= 2/3 else 0)

        return N, D, M

    def calc_intern_balk(self, x):
        N = -np.sum(self.FiA*self.sina) - self.FiC*self.singam + self.Vi[0]
        D = np.sum(self.FiA*self.cosa) - self.FiC*self.cosgam
        M = np.sum(self.FiA*self.cosa)*self.h - self.FiC*self.cosgam*self.h

        return N, D, M

    def calc_doorbuiging_wegdek(self, x):
        i = min(np.where(self.P >= x)[0][0] - 1, len(self.deeltje)-1)

        Q = C.VERDEELDE_BELASTING/2+C.EIG_GEWICHT_BRUG
        P = C.PUNT_BELASTING/2 \
            if i < len(self.P)-2 and self.P[i] < 2/3 and 2/3 < self.P[i+1] \
            else 0
        E = C.E_MODULUS
        I = C.I_WEGDEK

        return (5*Q*self.deeltje[i]**4)/(384*E*I) \
            + (5*P*self.deeltje[i]**3)/(48*E*I)

    def calc_piloon_I(self, x: float, balk1: bool = False):
        """
        Berekenen van 2 verschillende Is: 
        1) op basis van richting tuien
        2) op basis van richting loodrecht op tuien
        @returns I1, I2
        """
        N, _, _ = self.calc_intern_balk(x)
        Cte1 = 2
        Cte2 = 1/4
        E = C.E_MODULUS
        L = self.h

        I1 = abs(N)*L**2/(Cte1*math.pi**2*E)
        I2 = abs(N)*L**2/(Cte2*math.pi**2*E)

        return I1, I2

    def calc_fitness(self):
        """
        Optimaliseren voor zo min mogelijk krachten in pilonen en wegdek (duur tov van kabels)
        Functie roept zelf benodigde methoden aan
        """
        self.update_data()
        self.calc_reactie_krachten()
        FiA, FiB = self.calc_touw_kracht()
        Vc, Hc, FiC, _, Hd, _ = self.calc_kant()

        doorbuiging = [self.calc_doorbuiging_wegdek(x) for x in np.arange(0, 2.0, 0.01)]
        I1a, I1b = list(zip(*[self.calc_piloon_I(x) for x in np.arange(0, self.h, 0.01)]))
        I_max = np.max(np.array([*I1a, *I1b]))

        touw_max = np.max(np.array([*FiA, *FiB, FiC]))
        touw_max = touw_max if touw_max < 600 else touw_max**10  # punish for impossible constructions

        max_doorbuiging = np.max(doorbuiging)
        max_doorbuiging = max_doorbuiging if max_doorbuiging < 0.02 \
        else max_doorbuiging*10**20  # punish for impossible construction

        return max_doorbuiging*10**5 + self.h**6 + I_max*100 + \
            touw_max*0.1 + len(self.N)*10000


def print_brug(brug: Brug):
    import matplotlib.pyplot as plt

    x = np.arange(0, max([brug.h, 2]), 0.001)
    N1, _, _ = list(zip(*[brug.calc_intern_balk(xi) for xi in x]))
    N2 = -1
    _, D, _ = list(zip(*[brug.calc_intern_wegdek(xi) for xi in x]))
    I1a, I1b = list(zip(*[brug.calc_piloon_I(x) for x in np.arange(0, brug.h, 0.01)]))
    I2a, I2b = -1, -1
    doorbuiging = [brug.calc_doorbuiging_wegdek(x) for x in np.arange(0, 2.0, 0.01)]

    fig = plt.figure()
    ax1 = plt.subplot(2, 1, 1)
    ax1.plot(x, N1)
    ax1.set_ylabel("N1")
    ax2 = plt.subplot(2, 1, 2)
    ax2.plot(x, D)
    ax2.set_ylabel("D")

    print("======= Info Brug ========")
    print(f"h1:\t{brug.h}")
    print(f"h2:\t{-1}")
    print(f"d1a:\t{brug.da}")
    print(f"d2a:\t{-1}")
    print(f"d1b:\t{brug.db}")
    print(f"d2b:\t{-1}")
    print(f"N:\t{brug.N}")

    print("Krachten in touwen A")
    for F in brug.FiA:
        print(f"\t{F}")
    print("Krachten in touwen B")
    for F in brug.FiB:
        print(f"\t{F}")
    print("Krachten in touwen C")
    for F in [ brug.FiC ]:
        print(f"\t{F}")
    print("Krachten in touwen D")
    for F in [-1]*len(brug.N):
        print(f"\t{F}")
    print("Maximale kracht trek/druk:")
    print(f"\tN1: {np.max(np.abs(N1))}")
    print(f"\tN2: {-1}")
    print(f"\tD: {np.max(np.abs(D))}")

    print("Maximale I:")
    print(f"\tI1a: {np.max(np.abs(I1a))}")
    print(f"\tI1b: {np.max(np.abs(I1b))}")
    print(f"\tI2a: {-1}")
    print(f"\tI2b: {-1}")

    print("Maximale doorbuiging:")
    print(f"\t{np.max(np.abs(doorbuiging))}")

    return fig

