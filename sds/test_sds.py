import unittest
import sds.sds as sds
import random

class TestSDS(unittest.TestCase):

    def test_initialise(self):

        swarm = sds.Agent.initialise(agent_count=10)

        self.assertEqual(len(swarm),10)

        self.assertTrue(all((type(a) is sds.Agent) for a in swarm))
        
    def test_run(self):

        swarm = sds.Agent.initialise(agent_count=10)

        microtests = [lambda hyp: hyp==0 and random.random() > 0.1]

        random_hypothesis_function = lambda rng: rng.randint(0,1)

        sds.run(
            swarm=swarm,
            microtests=microtests,
            random_hypothesis_function=random_hypothesis_function,
            report_iterations=None,
        )
