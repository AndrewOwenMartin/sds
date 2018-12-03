import random
import functools
import sds

search_space = "xxhellxelloxhexhelxoxxxhxlloxxx"
model = "hello"

def random_hyp(rnd): return rnd.randint(0,len(search_space)-len(model))

def make_microtest(offset):
	return lambda hyp: search_space[hyp+offset] == model[offset]

microtests = [make_microtest(offset) for offset in range(len(model))]

clusters = sds.run(
	swarm=sds.Agent.initialise(agent_count=1000),
	microtests=microtests,
	random_hypothesis_function=random_hyp,
	max_iterations=300,
	diffusion_function=sds.passive_diffusion,
	rng=random.Random(),
	report_iterations=10,
)

print(clusters.most_common())
