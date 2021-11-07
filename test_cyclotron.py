from cyclotron import Cyclotron

tron = Cyclotron(num_teams=5, num_champions=1)
tron.get_start_population()

tron.grind(1)
tron.showmatch()