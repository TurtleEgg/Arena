from cyclotron import Cyclotron
tron = Cyclotron(num_champions = 1, num_teams = 10)
tron.get_start_population()
tron.grind(5)
from matplotlib.pyplot import plot, show
plot(tron.champ_scores); show()
tron.showmatch()