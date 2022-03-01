from numpy import mean


CRITICAL_SUCCESS_RATE = 0.2


def __init__(self, mut_type=1, mut_rate=0.05, step=0, step_interval=3000):
    self.mut_type = mut_type

    self.mut_rate = mut_rate
    self.step = step
    self.step_interval = step_interval


def update_hyper_parameters(hyper_parameters, scores=None):
    hyper_parameters["mut_rate"] = hyper_parameters["mut_rate"] * 0.9862327 # уполовинивается каждые 50 шагов
    print(f'{hyper_parameters["mut_rate"]=}')
    if scores:
        scores.sort(reverse=True)
        mean_score = mean(scores)
        success = [score for score in scores if score > mean_score]
        success_rate = len(success)/len(scores)
        print(f'{mean_score=}\n{success_rate=}')

        """if success_rate > CRITICAL_SUCCESS_RATE:
            hyper_parameters["mut_rate"] = hyper_parameters["mut_rate"] * 0.5
            print(f'{hyper_parameters["mut_rate"]}')
        """


    return hyper_parameters
