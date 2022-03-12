from datetime import datetime

from cyclotron import Cyclotron

TIME_DELTA_FORMAT = "%H:%M:%S"
TO_MINUTES = 1 / 60


tron = Cyclotron(num_teams=4, num_champions=2, num_tests = 1)
#tron.get_start_population("champs.dat", input_is_champions=True)
tron.get_start_population()

tic = datetime.today()
tron.grind_es(2, dump_step=0)
toc = datetime.today()
delta = toc-tic
delta_s = delta.total_seconds()
delta_min = delta_s * TO_MINUTES
print(f"Time used: {delta_s:.1f}s or {delta_min:.1f}min")

#tron.export_champions("champs.dat")
#tron.showmatch()