import random
import functools

def test_phase(
    swarm,
    microtests,
    multitesting=1,
    multitest_function=None,
    compare=False,
    compare_to_boolean=False,
    synchronous=True,
    rng=random,
):
    """\
Perform a test phase. Fully configurable. Consider using the more
convenient and readable functions test_phase and
comparative_test_phase.\
"""

    if compare:

        multitest_function = max

    else:

        multitest_function = all

    def make_test(hyp):

        return multitest_function(
            rng.choice(microtests)(hyp)
            for test_num
            in range(multitesting)
        )

    if compare and synchronous:

        test_results = [
            make_test(hyp=agent.hypothesis)
            for agent
            in swarm
        ]

        if compare_to_boolean:

            test_results = [
                test_result > rng.choice(test_results)
                for test_result
                in test_results
            ]

        for agent, test_result in zip(swarm, test_results):

            agent.active = test_result

            yield

    else:

        for agent in swarm:

            generic_single_agent_test(
                agent,
                swarm,
                microtests,
                compare,
                compare_to_boolean,
                multitesting,
                multitest_function,
            )

            yield

def mean_avg(values):

    acc = 0

    for num, value in enumerate(values, start=1):
        
        acc += value

    return acc / num

def agent_test(
    agent,
    swarm,
    microtests,
    compare,
    compare_to_boolean,
    multitesting,
    multitest_function,
    rng=random,
):
    """\
Peform a random microtest, and set the activity, for a single agent.\

It seems strange to duplicate the evaluation of the activities every
time for each agent, as happens with boolean comparative test phase.
Use functools lru_cache?
"""

    try:

        test_result = multitest_function(
            rng.choice(microtests)(agent.hypothesis)
            for multitest_num
            in range(multitesting)
        )

        print(test_result)

    except TypeError:

        raise TypeError("""\
This happens if you pass a function to microtests, which expects a list.
""".format(
            mtf=multitest_function,
            mt=microtests,
        ))

    if compare and compare_to_boolean:

        polled_hypothesis = rng.choice(swarm).hypothesis

        print('polled hyp',polled_hypothesis)

        polled_result = multitest_function(
            rng.choice(microtests)(polled_hypothesis)
            for multitest_num
            in range(multitesting)
        )

        test_result = test_result > polled_result

    agent.active = test_result
