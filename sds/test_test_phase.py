import unittest
import random
import sds.agent
import sds.test_phase

class TestTestPhase(unittest.TestCase):

    def test_true(self):
        
        self.assertTrue(True)
    
    def test_agent_test(self):

        good_hyp_agent = sds.agent.Agent(
            hypothesis=1234,
            active=False,
        )

        swarm = [sds.agent.Agent()]

        sds.test_phase.agent_test(
            agent=good_hyp_agent,
            swarm=[],
            microtests=[lambda hyp: hyp==1234],
            compare=False,
            compare_to_boolean=False,
            multitesting=1,
            multitest_function=all,
            rng=random,
        )

        self.assertTrue(good_hyp_agent.active)

        bad_hyp_agent = sds.agent.Agent(
            hypothesis=0,
            active=False,
        )

        sds.test_phase.agent_test(
            agent=bad_hyp_agent,
            swarm=[],
            microtests=[lambda hyp: hyp==1234],
            compare=False,
            compare_to_boolean=False,
            multitesting=1,
            multitest_function=all,
            rng=random,
        )

        self.assertFalse(bad_hyp_agent.active)

        compare_hyp_agent = sds.agent.Agent(
            hypothesis='foo',
            active=False,
        )

        swarm = [sds.agent.Agent(
            hypothesis='foo',
            active=0.5,
        )]

        sds.test_phase.agent_test(
            agent=compare_hyp_agent,
            swarm=swarm,
            microtests=[lambda hyp: 0.8],
            compare=True,
            compare_to_boolean=False,
            multitesting=10,
            multitest_function=sds.test_phase.mean_avg,
            rng=random,
        )

        self.assertEqual(
            compare_hyp_agent.active,
            (0.8+0.8+0.8+0.8+0.8+0.8+0.8+0.8+0.8+0.8)/10
        )


        compare_hyp_agent = sds.agent.Agent(
            hypothesis='foo',
            active=False,
        )

        print(compare_hyp_agent, [str(a) for a in swarm])

        sds.test_phase.agent_test(
            agent=compare_hyp_agent,
            swarm=swarm,
            microtests=[lambda hyp: 0.8],
            compare=True,
            compare_to_boolean=True,
            multitesting=10,
            multitest_function=sds.test_phase.mean_avg,
            rng=random,
        )

        print(compare_hyp_agent)
