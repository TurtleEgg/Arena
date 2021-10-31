

class HyperParameters():
    def __init__(self, mut_type=1, mut_rate=0.05, step=0, step_interval=3000):
        self.mut_type = mut_type
        self.mut_rate = mut_rate
        self.step = step
        self.step_interval = step_interval

    def update(self):
        self.step += 1
        if self.step > 1 and (self.step + 1) % self.step_interval == 0:
            self.mut_rate = self.mut_rate / 2