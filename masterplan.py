from cyclotron import Cyclotron
from matplotlib.pyplot import plot, show
tron = Cyclotron(num_champions=20, num_teams=400)
#tron.get_start_population("population/630gen_20_400.dat", input_is_champions=False)
tron.get_start_population("population/630gen_20_400.dat")
tron.grind(120, dump_step=20)
tron.export_champions(".dat")
plot(tron.champ_scores); show()
tron.showmatch()