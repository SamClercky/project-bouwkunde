"""
Bedoeling is om bruggen te berekenen AFK.
Dit wordt scriptje zoekt 1 keer een optimale brug
en wordt herhaald door een supervising script
"""

import genetic_algo as ga
from berekeningen_1piloon import print_brug

# Creeer van populatie
population = [ga.genRandomBrugVlot() for i in range(400)] # Populatie van 100
for i in range(1000): # 1000 generations
    print('.', end="")
    population = ga.kill_population(population)
    population = ga.regen_population(population,
                                    ga.genRandomBrugVlot,
                                    ga.genFromParentsVlot)

best = ga.find_best(population)
print_brug(best[1])
print(f"Score brug: {best[0]}")
