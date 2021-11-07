from cyclotron import Cyclotron
#from cyclotron import InitType
#tron = Cyclotron(num_champions = 10, num_teams = 100, init_type = InitType.POPULATION)
tron = Cyclotron(num_champions = 20, num_teams = 200)
tron.get_start_population()
tron.population.import_from_file("125gen_10_100_001.dat")
tron.grind(5)
tron.population.export_to_file(".dat")
from matplotlib.pyplot import plot, show
plot(tron.champ_scores); show()
tron.showmatch()