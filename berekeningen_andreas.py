import math
import numpy as np

from brug import BrugInterface

class Brug(BrugInterface):

    def __init__(self, h1, h2, d1, d2, N):
        self.h1 = h1
        self.h2 = h2
        self.d1 = d1
        self.d2 = d2
        self.N = N

        self.update_data()
    
    def update_data(self):
        """
        Bereken automatisch alpha en beta in de constructie
        """
        self.cosa = 2.0/(self.N+1)/math.sqrt(
                (self.h1/self.N)**2 + (2.0/(self.N+1))**2)
        self.sina = (self.h1/self.N)/math.sqrt(
                (self.h1/self.N)**2 + (2.0/(self.N+1))**2)
        self.cosb = 2.0/(self.N+1)/math.sqrt(
                (self.h2/self.N)**2 + (2.0/(self.N+1))**2)
        self.sinb = (self.h2/self.N)/math.sqrt(
                (self.h2/self.N)**2 + (2.0/(self.N+1))**2)

    def calc_reactie_krachten(self):
        # Opstellen van matrix
        # Uitrekenen van veel voorkomende bewerkingen
        deeltje = 2/(self.N+1)

        # Invoeren van VA-krachten
        A = []
        B = []
        for i in range(self.N+1):
            A.append([*[0]*i*2, 1, 1, *[0]*(self.N-i)*2])
            B.append(800*deeltje + ( 400 if 2/3 < deeltje*(i+1) and 2/3 > deeltje*i else 0 ))

        # Invoeren van momenten
        for i in range(self.N+1):
            A.append([*[0]*i*2, 0, deeltje, *[0]*(self.N-i)*2])
            B.append(800*deeltje**2/2 + ( 400*(2/3-deeltje*i) if 2/3 < deeltje*(i+1) and 2/3 > deeltje*i else 0 ))

        solv = np.linalg.solve(A, B)
        self.Va = solv[0]
        self.Vb = solv[-1]
        self.Fi = [solv[i] + solv[i+1] for i in range(1, len(solv)-1, 2)]

        return self.Va, self.Vb, self.Fi

    def calc_touw_kracht(self):
        try:
            solv = [
                    np.linalg.solve([
                        [self.cosa, self.cosb],
                        [self.sina, self.sinb],
                    ], [0, Fi]) for Fi in self.Fi]
        except np.linalg.LinAlgError:
            # Gebeurt als cosa = cosb en sina = sinb (singulier)
            solv = [[Fi/(2*self.sina)]*2 for Fi in self.Fi]

        self.FiA, self.FiB = list(zip(*solv))
        return self.FiA, self.FiB

    def calc_kant(self):
        def calc_i(i, h, d, FiA, cosa):
            cosgam = d/math.sqrt((h/self.N*i)**2 + d**2)
            singam = (h/self.N*i)/math.sqrt((h/self.N*i)**2 + d**2)

            FiC = FiA[i]*cosa/cosgam
            return FiC, cosgam, singam

        # Deel C
        FiC, cosgam, singam = list(zip(*[calc_i(
            i, self.h1, self.d1, self.FiA, self.cosa) for i in range(len(self.FiA))]))
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
            i, self.h2, self.d2, self.FiB, self.cosb) for i in range(len(self.FiA))]))
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
        i = min(int(x // deeltje), len(self.Fi)) # integer deling
        N = 0
        D = self.Va + sum(Fi for Fi in self.Fi[0:i]) - 800*x - (400 if x > 2/3 else 0)
        # M = self.Va*x + sum(self.Fi[ii]*(x-deeltje*ii) for ii in range(i)) - 800*x**2/2 - (400*(x-2/3) if x > 2/3 else 0)
        M = self.Va*x + sum(self.Fi[ii]*(x-deeltje*ii) for ii in range(len(self.Fi))) - self.Vb*(2-x) - 400*(x-2/3) - 800*x**2/2
        
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
        Va = self.Va if balk1 else self.Vb

        i = int(x // (h/self.N))
        N = np.sum(FiA[:i]*sina + FiC[:i]*singam[:i]) - (Va + np.sum(FiA*sina + FiC*singam))
        D = np.sum(FiA[:i]*cosa - FiC[:i]*cosgam[:i])
        M = np.sum(FiA[:i]*cosa - FiC[:i]*cosgam[:i])*sum(x-h/self.N*ii for ii in range(i))

        return N, D, M

    def calc_fitness(self):
        """
        Optimaliseren voor zo min mogelijk krachten in pilonen en wegdek (duur tov van kabels)
        Functie roept zelf benodigde methoden aan
        """
        self.update_data()
        self.calc_reactie_krachten()
        self.calc_touw_kracht()
        self.calc_kant()
        wdN, wdD, wdM = list(zip(*[self.calc_intern_wegdek(x) for x in np.arange(0, 2, 0.1)])) # wd = wegdek
        b1N, b1D, b1M = list(zip(*[self.calc_intern_balk(x, True) for x in np.arange(0, self.h1, 0.01)]))
        b2N, b2D, b2M = list(zip(*[self.calc_intern_balk(x, False) for x in np.arange(0, self.h2, 0.01)]))
        wdN, wdD, wdM = max(np.abs(wdN)), max(np.abs(wdD)), max(np.abs(wdM))
        b1N, b1D, b1M = max(np.abs(b1N)), max(np.abs(b1D)), max(np.abs(b1M))
        b2N, b2D, b2M = max(np.abs(b2N)), max(np.abs(b2D)), max(np.abs(b2M))

        return wdD*1 + b1N*2 + b2N*2
