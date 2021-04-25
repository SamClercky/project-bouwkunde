"""
Bedoeling is om bruggen te berekenen AFK.
Dit wordt scriptje zoekt 1 keer een optimale brug
en wordt herhaald door een supervising script
"""

import genetic_algo as ga

# Creeer van populatie
population = [ga.genRandomBrugA() for i in range(100)] # Populatie van 100
for i in range(100): # 1000 generations
    print('.', end="")
    population = ga.kill_population(population)
    population = ga.regen_population(population,
                                    ga.genRandomBrugA,
                                    ga.genFromParentsA)

best = ga.find_best(population)
ga.print_brug(best[1])
print(f"Score brug: {best[0]}")
