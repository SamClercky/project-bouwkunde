import numpy as np
import constanten as C
import math

class BrugInterface:
    
    def __init__(
        self,
        h1, h2,
        d1, d2,
        N):
        self.h1 = h1
        self.h2 = h2
        self.d1 = d1
        self.d2 = d2
        self.N = N

    def update_data(self):
        raise Exception("Unimplemented")

    def calc_reactie_krachten(self):
        raise Exception("Unimplemented")

    def calc_touw_kracht(self):
        raise Exception("Unimplemented")

    def calc_kant(self):
        raise Exception("Unimplemented")

    def calc_intern_wegdek(self, x: float):
        raise Exception("Unimplemented")

    def calc_intern_balk(self, x: float, balk1: bool):
        raise Exception("Unimplemented")

    def calc_doorbuiging_wegdek(self, x):
        deeltje = 2/(self.N+1)
        i = int(x//deeltje)

        Q = C.VERDEELDE_BELASTING/2+C.EIG_GEWICHT_BRUG
        P = C.PUNT_BELASTING/2 if deeltje*i < 2/3 and 2/3 < deeltje*(i+1) else 0
        E = C.E_MODULUS
        I = C.I_WEGDEK

        return (5*Q*deeltje**4)/(384*E*I) + (5*P*deeltje**3)/(48*E*I)

    def calc_piloon_I(self, x: float, balk1: bool):
        """
        Berekenen van 2 verschillende Is: 
        1) op basis van richting tuien
        2) op basis van richting loodrecht op tuien
        @returns I1, I2
        """
        N, _, _ = self.calc_intern_balk(x, balk1)
        Cte = 1/4
        E = C.E_MODULUS
        h = self.h1 if balk1 else self.h2
        deeltje = h/self.N
        #L = deeltje*(x//deeltje + 1)
        L1 = deeltje
        L2 = deeltje*(x//deeltje + 1) # Hoogte van deel

        I1 = abs(N)*L1**2/(Cte*math.pi**2*E)
        I2 = abs(N)*L2**2/(Cte*math.pi**2*E)

        return I1, I2
    
    def calc_piloon_balk(self, x: float, balk1: bool):
        """
        Berekenen van balk met stukjes van 0.006m x 0.0318m
        """
        I1, I2 = self.calc_piloon_I(x, balk1)

        b = (I2**3/I1 * 11**2)**(1/8)
        h = (I1**3/I1 * 12**2)**(1/8)

        return h, b

    def calc_fitness(self):
        """
        Optimaliseren voor zo min mogelijk krachten in pilonen en wegdek (duur tov van kabels)
        Functie roept zelf benodigde methoden aan
        """
        self.update_data()
        self.calc_reactie_krachten()
        FiA, FiB = self.calc_touw_kracht()
        Vc, Hc, FiC, Vd, Hd, FiD = self.calc_kant()

        doorbuiging = [self.calc_doorbuiging_wegdek(x) for x in np.arange(0, 2.0, 0.01)]
        I1a, I1b = list(zip(*[self.calc_piloon_I(x, True) for x in np.arange(0, self.h1, 0.01)]))
        I2a, I2b = list(zip(*[self.calc_piloon_I(x, False) for x in np.arange(0, self.h2, 0.01)]))
        I_max = np.max(np.array([*I1a, *I1b, *I2a, *I2b]))

        touw_max = np.max(np.array([*FiA, *FiB, *FiC, *FiD]))
        touw_max = touw_max if touw_max < 460 else touw_max*10**9  # punish for impossible constructions

        max_doorbuiging = np.max(doorbuiging)
        max_doorbuiging = max_doorbuiging if max_doorbuiging < 0.02 \
            else max_doorbuiging*10**9  # punish for impossible construction

        h = self.h1 + self.h2*1.3  # We willen assymmetrie

        return (max_doorbuiging*10)**2 + (h*10)**4 + I_max*1000 + \
            touw_max*0.1 + self.N*100
