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
        N, _, _ = self.calc_intern_balk(x, balk1)
        Cte = 1/4
        E = C.E_MODULUS
        h = self.h1 if balk1 else self.h2
        deeltje = h/self.N
        #L = deeltje*(x//deeltje + 1)
        L = deeltje

        I = abs(N)*L**2/(Cte*math.pi**2*E)

        return I
    
    def calc_piloon_balk(self, x: float, balk1: bool):
        """
        Berekenen van balk met stukjes van 0.006m x 0.0318m
        """
        h_step = 0.006
        b_step = 0.034
        h = h_step
        b = b_step

        I = lambda h, b: b*h**3/12
        Pr = self.calc_piloon_I(x, balk1)

        while I(h, b) < Pr:
            h += h_step
            b += b_step
        
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
        wdN, wdD, wdM = list(zip(*[self.calc_intern_wegdek(x) for x in np.arange(0, 2, 0.1)])) # wd = wegdek
        b1N, b1D, b1M = list(zip(*[self.calc_intern_balk(x, True) for x in np.arange(0, self.h1, 0.01)]))
        b2N, b2D, b2M = list(zip(*[self.calc_intern_balk(x, False) for x in np.arange(0, self.h2, 0.01)]))
        doorbuiging = [self.calc_doorbuiging_wegdek(x) for x in np.arange(0, 2.0, 0.01)]
        I1 = [self.calc_piloon_I(x, True) for x in np.arange(0, self.h1, 0.01)]
        I1 = [self.calc_piloon_I(x, False) for x in np.arange(0, self.h2, 0.01)]

        wdN, wdD, wdM = max(np.abs(wdN)), max(np.abs(wdD)), max(np.abs(wdM))
        b1N, b1D, b1M = max(np.abs(b1N)), max(np.abs(b1D)), max(np.abs(b1M))
        b2N, b2D, b2M = max(np.abs(b2N)), max(np.abs(b2D)), max(np.abs(b2M))

        return wdD*1 + b1N*2 + b2N*2
