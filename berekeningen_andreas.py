import math
import numpy as np

class Brug:

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
            B.append(800*deeltje + ( 400*(2/3-deeltje*i) if 2/3 < deeltje*(i+1) and 2/3 > deeltje*i else 0 ))

        return A,B
