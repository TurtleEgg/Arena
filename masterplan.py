from cyclotron import Cyclotron
from matplotlib.pyplot import plot, show
tron = Cyclotron(num_champions=20, num_teams=200)
#tron.get_start_population("population/350gen_20_200_ch.dat", input_is_champions=True)
tron.get_start_population("population/350gen_20_200_ch.dat")
tron.grind(120, dump_step=20)
tron.export_champions(".dat")
plot(tron.champ_scores); show()
tron.showmatch()