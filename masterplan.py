from cyclotron import Cyclotron
tron = Cyclotron()
tron.get_start_population()
tron.grind(5)
from matplotlib.pyplot import plot, show
plot(tron.champ_scores); show()
tron.showmatch()