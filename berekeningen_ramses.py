import math
import numpy as np

from brug import BrugInterface
import constanten as C

class Brug(BrugInterface):
    
    def __init__(self, h1, h2, d1a, d2a, d1b, d2b, N):
        self.h1 = h1
        self.h2 = h2
        self.d1a = d1a
        self.d2a = d2a
        self.d1b = d1b
        self.d2b = d2b
        self.N = N

        self.update_data()
    
    def update_data(self):
        """
        Bereken automatisch alpha en beta in de constructie
        """

        breette_a = 2.0/(self.N+1) + self.d1b
        hoogte_a = self.h1/self.N
        hypoth_a = math.sqrt(breette_a**2 + hoogte_a**2)

        breette_b = 2.0/(self.N+1) + self.d2b
        hoogte_b = self.h2/self.N
        hypoth_b = math.sqrt(breette_b**2 + hoogte_b**2)

        self.cosa = breette_a/hypoth_a
        self.sina = hoogte_a/hypoth_a
        self.cosb = breette_b/hypoth_b
        self.sinb = hoogte_b/hypoth_b

    def calc_reactie_krachten(self):
        deeltje = 2.0/(self.N + 1)

        V = []
        for i in range(self.N+1):
            Va = (C.VERDEELDE_BELASTING+C.EIG_GEWICHT_BRUG)*deeltje/2
            Vb = (C.VERDEELDE_BELASTING+C.EIG_GEWICHT_BRUG)*deeltje/2

            if deeltje*i < 2/3 and 2/3 < deeltje*(i+1):
                Va += C.PUNT_BELASTING*(deeltje*(i+1) - 2/3)/deeltje
                Vb += C.PUNT_BELASTING*(2/3 - deeltje*i)/deeltje
            V.append(Va)
            V.append(Vb)

        V = [V[0], *[V[i] + V[i+1] for i in range(1, len(V)-1, 2)], V[-1]]
        self.Vi = V
        return V

    def calc_touw_kracht(self):
        singam = math.sqrt(1-self.sina**2)
        sinphi = math.sqrt(1-self.sinb**2)
        sinab  = self.sina*self.cosb + self.cosa*self.sinb

        self.FiA = [self.Vi[i] * sinphi/sinab for i in range(1, len(self.Vi)-1)]
        self.FiB = [self.Vi[i] * singam/sinab for i in range(1, len(self.Vi)-1)]

        return self.FiA, self.FiB

    def calc_kant(self):
        def calc_i(i, h, d, FiA, cosa):
            cosgam = d/math.sqrt((h/self.N*i)**2 + d**2)
            singam = (h/self.N*i)/math.sqrt((h/self.N*i)**2 + d**2)

            FiC = FiA[i]*cosa/cosgam
            return FiC, cosgam, singam

        # Deel C
        FiC, cosgam, singam = list(zip(*[calc_i(
            i, self.h1, self.d1a-self.d1b, self.FiA, self.cosa) for i in range(len(self.FiA))]))
        self.FiC = FiC
        self.cosgam = cosgam
        self.singam = singam
        FiC = np.array(self.FiC)
        cosgam = np.array(cosgam)
        singam = np.array(singam)
        self.Vc = -np.sum(FiC*singam)
        self.Hc = -np.sum(FiC*cosgam)

        # Deel D
        FiD, cosxi, sinxi = list(zip(*[calc_i(
            i, self.h2, self.d2a-self.d2b, self.FiB, self.cosb) for i in range(len(self.FiA))]))
        self.FiD = FiD
        FiD = np.array(self.FiD)
        self.cosxi = cosxi
        self.sinxi = sinxi
        cosxi = np.array(cosxi)
        sinxi = np.array(sinxi)
        self.Vd = -np.sum(FiD*sinxi)
        self.Hd = -np.sum(FiD*cosxi)

        return self.Vc, self.Hc, self.FiC, self.Vd, self.Hd, self.FiD

    def calc_intern_wegdek(self, x):
        deeltje = 2/(self.N+1)
        i = min(int(x // deeltje), len(self.Vi)-1) # integer deling
        N = 0
        D = sum(self.Vi[0:i+1]) - (C.VERDEELDE_BELASTING+C.EIG_GEWICHT_BRUG)*x - (C.PUNT_BELASTING if x > 2/3 else 0)
        # M = self.Va*x + sum(self.Fi[ii]*(x-deeltje*ii) for ii in range(i)) - 800*x**2/2 - (400*(x-2/3) if x > 2/3 else 0)
        #M = self.Va*x + sum(self.Fi[ii]*(x-deeltje*ii) for ii in range(len(self.Fi))) - self.Vb*(2-x) - 400*(x-2/3) - 800*x**2/2
        # M = 0
        # for j in range(i):
        #     M += deeltje*self.Vi[j] - (C.VERDEELDE_BELASTING+C.EIG_GEWICHT_BRUG)*deeltje**2/2
        #     M += C.PUNT_BELASTING*(2/3 - deeltje*j) if deeltje*j < 2/3 and 2/3 < deeltje*(j+1) else 0
        # M += (x%deeltje)*self.Vi[i] - (C.VERDEELDE_BELASTING+C.EIG_GEWICHT_BRUG)*(x%deeltje)**2/2
        # M += C.PUNT_BELASTING*(2/3 - x) if deeltje*i < 2/3 and 2/3 < x else 0
        M = sum(self.Vi[ii]*(x-deeltje*(ii)) for ii in range(i+1)) - (C.VERDEELDE_BELASTING+C.EIG_GEWICHT_BRUG)*x**2/2 - (C.PUNT_BELASTING*(x-2/3) if x > 2/3 else 0)
        
        return N, D, M

    def calc_intern_balk(self, x, balk1: bool):
        # setup aliases
        cosgam = np.array(self.cosgam if balk1 else self.cosxi)
        singam = np.array(self.singam if balk1 else self.sinxi)
        FiA = np.array(self.FiA if balk1 else self.FiB)
        FiC = np.array(self.FiC if balk1 else self.FiD)

        cosa = self.cosa if balk1 else self.cosb
        sina = self.sina if balk1 else self.sinb
        h = self.h1 if balk1 else self.h2
        Va = self.Vi[0] if balk1 else self.Vi[-1]

        i = min(int(x // (h/self.N)), self.N-1)
        N = np.sum(FiA[:i]*sina + FiC[:i]*singam[:i]) - (Va + np.sum(FiA*sina + FiC*singam))
        D = np.sum(FiA[:i]*cosa - FiC[:i]*cosgam[:i])
        M = np.sum(FiA[:i]*cosa - FiC[:i]*cosgam[:i])*sum(x-h/self.N*ii for ii in range(i))
        #M = 0
        #for j in range(i):
        #    M += h/self.N*(FiA[j]*cosa - FiC[j]*cosgam[j])
        #M += (x%(h/self.N))*(FiA[i]*cosa - FiC[i]*cosgam[i])

        return N, D, M
