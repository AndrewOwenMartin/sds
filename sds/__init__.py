from collections import namedtuple
import functools
import itertools
import json
import queue
import time # for time.sleep
import itertools # for itertools.count
import threading # for threading.Thread
import collections
import random
class Agent:
    """\
Data structure for defining an SDS Agent, can only maintain the
attributes 'hypothesis' and 'active'.\
"""
    __slots__ = ('hypothesis','active')

    def __init__(self, hypothesis=None, active=False):
        """\
Initialise an agent with specific values for hypothesis and active.
Defaults to inactive with no hypothesis.\
"""
        self.hypothesis = hypothesis

        self.active = active

    @staticmethod
    def initialise(agent_count):
        """\
    Returns a list of length agent_count, of inactive Agents with no
    hypothesis; suitable for use as a swarm. For example:
        swarm = sds.Agent.initialise(agent_count=1000)
    """
        return [
            Agent(hypothesis=None, active=False)
            for _
            in range(agent_count)
        ]

    def __iter__(self):
        """ Iterating over an agent returns its hypothesis, then its
            activity.
        """
        yield self.hypothesis
        yield self.active
ReadOnlyAgent = namedtuple("ReadOnlyAgent",("hypothesis","active"))

ReadOnlyAgent.__doc__ = """\
namedtuple representation of an agent. Attributes are hypothesis and
active.\
"""
def generic_test_phase(
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
convenient and readable functions sds.test_phase and
sds.comparative_test_phase.\
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

        test_results = (
            make_test(agent.hypothesis)
            for agent
            in swarm
        )

        test_results = list(test_results)

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
def test_phase(
    swarm,
    microtests,
    multitesting=1,
    multitest_function=all,
    synchronous=True,
    rng=random,
):
    """\
Perform a test phase with boolean microtests.

This function returns a generator which must be consumed once for each
agent.\
"""

    test_phase_generator = generic_test_phase(
        swarm=swarm,
        microtests=microtests,
        multitesting=multitesting,
        multitest_function=multitest_function,
        compare=False,
        synchronous=synchronous,
        rng=rng,
    )

    for _ in test_phase_generator:
        yield
def comparative_test_phase(
    swarm,
    microtests,
    multitesting=1,
    multitest_function=max,
    synchronous=True,
    rng=random,
):
    """\
Performs a test phase with scalar microtests, an agent becomes active
if their microtest result is larger than that of a randomly chosen
agent.

This function returns a generator which must be consumed once for each
agent.\
"""

    test_phase = generic_test_phase(
        swarm=swarm,
        microtests=microtests,
        multitesting=multitesting,
        multitest_function=multitest_function,
        compare=True,
        synchronous=synchronous,
        rng=rng,
    )

    for _ in test_phase:
        yield
def generic_single_agent_test(
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
"""

    try:
        test_result = multitest_function(
            rng.choice(microtests)(agent.hypothesis)
            for multitest_num
            in range(multitesting)
        )

    except TypeError:

        raise TypeError("""\
This error is most commonly raised if 'microtests' is not a \
collection. Confirm that 'microtests' is a collection, for example, a
list or set."""
        )

    if compare and compare_to_boolean:

        polled_hypothesis = rng.choice(swarm).hypothesis

        polled_result = multitest_function(
            rng.choice(microtests)(polled_hypothesis)
            for multitest_num
            in range(multitesting)
        )

        test_result = test_result > polled_result

    agent.active = test_result
def generic_diffusion(
    swarm,
    random_hypothesis_function,
    context_free,
    context_sensitive,
    multidiffusion,
    passive,
    active,
    rng=random,
):
    """\
Perform a diffusion phase, fully configurable. Consider using the more
convenient and readable functions passive_diffusion,
context_free_diffusion and context_sensitive_diffusion.

This function returns a generator which must be consumed once for each
agent.\
"""

    if context_sensitive:

        context_free = True

    if context_free and not active:

        old_swarm = [
            ReadOnlyAgent(a.hypothesis,a.active)
            for a
            in swarm
        ]

    else:

        old_swarm = swarm

    for agent in swarm:

        generic_single_agent_diffusion(
            agent,
            old_swarm,
            random_hypothesis_function,
            context_free,
            context_sensitive,
            multidiffusion,
            passive,
            active,
            rng,
        )

        yield
def generic_single_agent_diffusion(
    agent,
    swarm,
    random_hypothesis_function,
    context_free,
    context_sensitive,
    multidiffusion,
    passive,
    active,
    rng=random,
):
    """\
Perform diffusion, and set the hypothesis for a single agent.\
"""
    polled_agents = (
        rng.choice(swarm)
        for diffusion_num
        in range(int(multidiffusion))
    )

    for polled_agent in polled_agents:
        if (
            (passive and (not agent.active) and polled_agent.active)
            or (active and agent.active and (not polled_agent.active))
        ):
            break
    else:
        remainder = multidiffusion - int(multidiffusion)

        if remainder > 0:

            if rng.random() > remainder:

                polled_agent = rng.choice(swarm)

    if (
        (active and agent.active and (not polled_agent.active))
        or
        (passive and (not agent.active) and polled_agent.active)
    ):
        if agent.active:
            polled_agent.hypothesis = agent.hypothesis
        else:
            agent.hypothesis = polled_agent.hypothesis
    elif (
            not agent.active
        or
            polled_agent.active
            and context_free
            and (
                not context_sensitive
                or agent.hypothesis == polled_agent.hypothesis
            )
    ):
        agent.active = False
        agent.hypothesis = random_hypothesis_function(rng)
def passive_diffusion(
    swarm,
    random_hypothesis_function,
    multidiffusion=1,
    rng=random,
):
    """\
Perform a passive diffusion phase.

This function returns a generator which must be consumed once for each
agent.\
"""

    diffusion_phase = generic_diffusion(
        swarm,
        random_hypothesis_function,
        context_free=False,
        context_sensitive=False,
        multidiffusion=multidiffusion,
        passive=True,
        active=False,
        rng=rng,
    )

    for _ in diffusion_phase:
        yield
def context_free_diffusion(
    swarm,
    random_hypothesis_function,
    multidiffusion=1,
    passive=True,
    active=False,
    rng=random,
):
    """\
Perform a context free diffusion phase.

This function returns a generator which must be consumed once for each
agent.\
"""

    diffusion_phase = generic_diffusion(
        swarm,
        random_hypothesis_function,
        context_free=True,
        context_sensitive=False,
        multidiffusion=multidiffusion,
        passive=passive,
        active=active,
        rng=rng,
    )

    for _ in diffusion_phase:
        yield
def context_sensitive_diffusion(
    swarm,
    random_hypothesis_function,
    multidiffusion=1,
    passive=False,
    active=False,
    rng=random,
):
    """\
Perform a context sensitive diffusion phase.

This function returns a generator which must be consumed once for each
agent.\
"""

    diffusion_phase = generic_diffusion(
        swarm,
        random_hypothesis_function,
        context_free=True,
        context_sensitive=True,
        multidiffusion=multidiffusion,
        passive=passive,
        active=active,
        rng=rng,
    )

    for _ in diffusion_phase:
        yield
def synchronous_iterate(
    swarm,
    microtests,
    random_hypothesis_function,
    diffusion_function,
    test_phase_function=test_phase,
    multidiffusion=1,
    multitesting=1,
    multitest_function=None,
    rng=random,
):
    """\
Performs a synchronous iteration, one diffusion phase for all agents
followed by one test phase for all agents.

This function returns a generator which must be consumed once for each
iteration.\
"""

    while True:

        diffusion_phase_iterator = diffusion_function(
            swarm=swarm,
            random_hypothesis_function=random_hypothesis_function,
            multidiffusion=multidiffusion,
            rng=rng,)

        for _ in diffusion_phase_iterator:
            pass

        test_phase_iterator = test_phase_function(
            swarm=swarm,
            microtests=microtests,
            multitesting=multitesting,
            multitest_function=multitest_function,
            synchronous=True,
            rng=rng,)

        for _ in test_phase_iterator:
            pass

        yield
def asynchronous_iterate(
    swarm,
    microtests,
    random_hypothesis_function,
    diffusion_function,
    test_phase_function=test_phase,
    multidiffusion=1,
    multitesting=1,
    multitest_function=None,
    rng=random,
):
    """\
Performs an asynchronous iteration, all agents are selected in a
random order to perform one diffusion and one test in turn.

This function returns a generator which must be consumed once for each
iteration.\
"""

    while True:

        for agent in swarm:
            if agent.hypothesis is None:
                agent.hypothesis = random_hypothesis_function(rng)

        rng.shuffle(swarm)

        diffusion_phase_iterator = diffusion_function(
            swarm=swarm,
            random_hypothesis_function=random_hypothesis_function,
            multidiffusion=multidiffusion,
            rng=rng,)

        test_phase_iterator = test_phase_function(
            swarm=swarm,
            microtests=microtests,
            multitesting=multitesting,
            multitest_function=multitest_function,
            synchronous=False,
            rng=rng,)

        for _ in zip(diffusion_phase_iterator, test_phase_iterator):
            pass

        yield
def parallel_iterate(
    swarm,
    microtests,
    random_hypothesis_function,
    diffusion_function,
    test_phase_function=test_phase,
    multidiffusion=1,
    passive=True,
    active=False,
    multitesting=1,
    multitest_function=None,
    rng=random,
):
    """\
Performs a parallel iteration, all agents are updating their state (a
diffusion followed by a test) in parallel.

This function returns a generator which simply waits a short time
between yeilding, this can be used to ensure the parallel process
runs for a certain amount of wall clock time.\
"""

    context_free = diffusion_function is context_free_diffusion

    context_sensitive = (
        diffusion_function is context_sensitive_diffusion
    )

    compare = test_phase_function is comparative_test_phase
    compare_to_boolean = compare

    if compare:
        multitest_function = max
    else:
        multitest_function = all

    for agent in swarm:
        if agent.hypothesis is None:
            agent.hypothesis = random_hypothesis_function(rng)

    worker_threads = (
        threading.Thread(
            target=update_state,
            args=(
                agent,
                swarm,
                random_hypothesis_function,
                context_free,
                context_sensitive,
                multidiffusion,
                passive,
                active,
                microtests,
                multitesting,
                multitest_function,
                compare,
                compare_to_boolean,
                rng,
            )
        )
        for agent
        in swarm
    )

    for worker_thread in worker_threads:
        worker_thread.daemon = True
        worker_thread.start()

    while True:
        time.sleep(0.01)
        yield
def update_state(
    agent,
    swarm,
    random_hypothesis_function,
    context_free,
    context_sensitive,
    multidiffusion,
    passive,
    active,
    microtests,
    multitesting,
    multitest_function,
    compare,
    compare_to_boolean,
    rng=random,
):
    """\
Repeatedly perform a diffusion and a test for an agent, with a short
sleep. This function is a helper function to parallel_iterate.\
"""
    while True:

        generic_single_agent_diffusion(
            agent,
            swarm,
            random_hypothesis_function,
            context_free,
            context_sensitive,
            multidiffusion,
            passive,
            active,
            rng,
        )

        generic_single_agent_test(
            agent,
            swarm,
            microtests,
            compare,
            compare_to_boolean,
            multitesting,
            multitest_function,
        )

        sleepy_time = min(2,max(0,rng.gauss(1,1)))

        time.sleep(sleepy_time)
def never_halt(*args, **kwargs):
    """\
Always returns false, suitable as a halting function for a perpetual
SDS.\
"""

    return False
def make_stability_halting_function(lower, region, time):
    """\
Returns a function suitable for use as a halting function. Halts, by
returning True when it detects stability, defined by:

lower: Lower bound of proportion of activity of stability window.

region: Amount above lower which defines the upper bound of the
stability window.

time: Number of consecutive times this function must be called with
arguments within the stability window before it will halt.\
"""

    def generator_front_end(activity_count, halt_generator):
        next(halt_generator)
        halted = halt_generator.send(activity_count)
        return halted

    def is_stable_generator(lower, region, time):

        success_count = 0

        while True:

            swarm = yield

            active_count = sum(
                1
                for agent
                in swarm
                if agent.active
            ) / len(swarm)

            if active_count < lower or active_count > lower + region:

                success_count = 0

            else:

                success_count += 1

            yield success_count >= time

    halting_generator = is_stable_generator(lower, region, time)

    return functools.partial(
        generator_front_end,
        halt_generator=halting_generator,)
def make_instant_threshold_halt_function(threshold):
    """\
Returns a function suitable for use as a halting function. Halts, by
returning True when the proportion of global activity is greater than
threshold.\
"""
    def threshold_halt_function(swarm, threshold):

        activity = sum(1 for agent in swarm if agent.active)/len(swarm)

        return activity > threshold

    return functools.partial(
        threshold_halt_function,
        threshold=threshold,
    )
def make_instant_strong_halting_function(threshold):
    """\
Returns a function suitable for use as a halting function. Halts, by
returning True when the proportion of activity at the largest cluster is
greater than threshold.\
"""
    def strong_halt_function(swarm, threshold):

        largest_cluster_activity = (
            count_clusters(swarm).most_common(1)
            or [(None,0)]
        )

        hyp, cluster_size = largest_cluster_activity[0]

        activity = cluster_size/len(swarm)

        return activity > threshold

    return functools.partial(strong_halt_function, threshold=threshold)
def make_threshold_time_halting_function(lower, time):
    """\
Returns a function suitable for use as a halting function. Halts, by
returning True when the proportion of global activity is greater than
threshold for a number of calls to this function defined by time.\
"""

    def generator_front_end(activity_count, halt_generator):
        next(halt_generator)
        halted = halt_generator.send(activity_count)
        return halted

    def is_stable_generator(lower, time):

        success_count = 0

        while True:

            swarm = yield

            active_count = sum(
                1
                for agent
                in swarm
                if agent.active
            ) / len(swarm)

            if active_count < lower:
                success_count = 0
            else:
                success_count += 1

            yield success_count >= time

    halting_generator = is_stable_generator(lower, time)

    return functools.partial(
        generator_front_end,
        halt_generator=halting_generator,)
def run(
    swarm,
    microtests,
    random_hypothesis_function,
    max_iterations=1000,
    diffusion_function=passive_diffusion,
    halting_function=never_halt,
    halting_iterations=1,
    multitesting=1,
    multitest_function=None,
    report_iterations=10,
    test_phase_function=test_phase,
    hypothesis_string_function=str,
    max_cluster_report=None,
    iteration_function=synchronous_iterate,
    multidiffusion=1,
    report_function=None,
    rng=random,
):
    """\
The main front end to the SDS library. This will run forever until
manually halted, or until a halting condition is reached, afterwhich
it will return a collections.Counter of all the clusters.

:param swarm: A list of sds.Agent instances.
:param microtests: A collection of functions all of which take a hypothesis\
, as returned by random_hypothesis_function and return the result of a\
 microtest as either a scalar value or a boolean. All tests must \
return the same type.
:param random_hypothesis_function: A function which takes a random number \
generator and returns hypothesis suitable as input for all the \
functions in microtests.
:param max_iterations: The number of iterations afterwhich the SDS will \
halt.  If max_iterations=None, the SDS will never halt due to the num\
ber of iterations, but may be manually halted, or halted by the halti\
ng function.
:param diffusion_function: The diffusion function to use in the diffusion \
phase.
:param random: A random number generator, probably an instance of the rand\
om.Random class. Use an instance with an explicit seed to get repeata\
ble behaviour, else you may pass in the random module itself.
:param halting_function: (Default: never_halt) The function which takes \
the swarm as input and returns True if its condition is met.
:param halting_iterations: (Default: 0) The number of iterations between \
each call of the halting_function. If halting_iterations is a Falsy \
value (e.g. None, 0, False, [], '') then the halting_function is \
never called.
:param multitesting: (Default: 1) The number of microtests each agent \
performs in the test phase. Must be an integer.
:param multitest_function: (Default: None) The function which takes a \
list of microtest results and turns them into a single result. The \
most likely values for multitest_function will be 'all' i.e. all \
microtests must pass, and 'any' i.e. at least one microtest must pass.
:param report_iterations: (Default: None) The number of iterations \
between each report to stdout of the hypotheses with the largest \
clusters.
:param test_phase_function: (Default: test_phase) The function to use in \
the test phase.
:param hypothesis_string_function: (Default: str) The function to call \
on a hypothesis to turn it into a string, suitable for inclusion in \
the report. If hypotheses are using built-in data types, str is \
often enough, otherwise a custom 'to string' function must be supplied.
:param max_cluster_report: (Default: None) The maximum number of \
clusters to include in the report.
:param iteration_function: (Default: synchronous_iterate) The iteration \
function to call once per iteration.
:param multidiffusion: (Default: 1) The number of agents for a polling \
agent to poll during the diffusion phase. May be an integer or a \
float.\
"""
    if report_function is None:

        report_function = functools.partial(
            basic_report,
            hypothesis_string_function=hypothesis_string_function,
            max_cluster_report=max_cluster_report,
        )

    handle_reporting = functools.partial(
        generic_handle_reporting,
        report_iterations=report_iterations,
        report_function=report_function,
    )

    handle_halting = functools.partial(
        generic_handle_halting,
        halting_iterations=halting_iterations,
        halting_function=halting_function,
        max_iterations=max_iterations,
    )

    try:

        iteration_generator = iteration_function(
            swarm=swarm,
            microtests=microtests,
            random_hypothesis_function=random_hypothesis_function,
            diffusion_function=diffusion_function,
            test_phase_function=test_phase_function,
            multidiffusion=multidiffusion,
            multitesting=multitesting,
            multitest_function=multitest_function,
            rng=rng,
        )

        for iteration_num, iteration in enumerate(iteration_generator):

            handle_reporting(iteration_num, swarm)

            if handle_halting(iteration_num, swarm):

                break

    except KeyboardInterrupt:

        pass

    return count_clusters(swarm)
def generic_handle_halting(
    iteration_num,
    swarm,
    halting_iterations,
    halting_function,
    max_iterations,
):

    return (
        (
            halting_iterations
            and iteration_num % halting_iterations == 0
            and halting_function(swarm)
        ) or (
            max_iterations and iteration_num >= max_iterations
        )
    )
def basic_report(
    iteration_num,
    swarm,
    hypothesis_string_function=str,
    max_cluster_report=None,
):

    clusters = count_clusters(swarm)

    agent_count = len(swarm)

    return "{i:4} Activity: {a:0.3f}. {c}".format(
        i=iteration_num,
        a=sum(clusters.values())/float(agent_count),
        c=", ".join(
            "{hyp}:{count}".format(
                hyp=hypothesis_string_function(hyp),
                count=count
            )
            for hyp,count
            in clusters.most_common(max_cluster_report)
        ),
    )
def generic_handle_reporting(
    iteration_num,
    swarm,
    report_iterations,
    report_function,
):

    if (
        report_iterations
        and iteration_num % report_iterations == 0
    ):
        print(report_function(iteration_num, swarm))
def run_daemon(
    swarm,
    microtests,
    random_hypothesis_function,
    diffusion_function,
    max_iterations=None,
    halting_function=never_halt,
    halting_iterations=0,
    multitesting=1,
    multitest_function=None,
    report_iterations=None,
    test_phase_function=test_phase,
    hypothesis_string_function=str,
    max_cluster_report=None,
    out_file_name='/tmp/clusters.json',
    rng=random,
):
    """\
Calls sds.run in a daemon thread. The daemon can be interacted with
through the command line.

q: Halt the SDS and kill the daemon.
c: Print the largest clusters to the screen.
w: Write the largest clusters to file.

Anything else is printed to stdout.\
"""

    def write_status(swarm):
        with open(out_file_name,'w') as f:
            write_swarm(swarm,f)
            print('wrote swarm status to',out_file_name)

    control_queue = queue.Queue()
    control_queue.put(True)

    def swarm_iterator():

        print('starting SDS')
        run(
            swarm,
            microtests,
            random_hypothesis_function,
            max_iterations,
            diffusion_function,
            halting_function,
            halting_iterations,
            multitesting,
            multitest_function,
            report_iterations,
            test_phase_function,
            hypothesis_string_function,
            max_cluster_report,
            rng,)

        print('finishing SDS')

        write_status(swarm)

        control_queue.task_done()

    t = threading.Thread(target=swarm_iterator)
    t.daemon = True # Program will exit when only daemons are left.
    t.start()
    del t

    def interface_manager():

        while True:

            instr = input()

            if instr == 'q':

                print("'q' received quitting")

                control_queue.task_done()

                break

            elif instr == 'c':

                print(
                    count_clusters(swarm)
                    .most_common(max_cluster_report)
                )

            elif instr == 'w':

                write_status(swarm)

            else:

                print('You said:',instr.upper())

    t = threading.Thread(target=interface_manager)
    t.daemon = True # Program will exit when only daemons are left.
    t.start()
    del t

    control_queue.join()

    print('done run_daemon')

    return count_clusters(swarm)
def coupled_diffusion(
    swarms,
    random,
    random_hypothesis_functions,
    diffusion_functions,
):
    """\
Performs Coupled diffusion when passed a list of swarms, a list of
random hypothesis functions and a list of diffusion functions. Not
tested with the newest version of sds.run.\
"""
    for swarm, diffusion_function, random_hypothesis_function in zip(
        swarms,
        diffusion_functions,
        random_hypothesis_functions
    ):
        diffusion_function(swarm, random, random_hypothesis_function)
def generic_coupled_test_phase(
    master_swarm_num,
    swarms,
    random,
    multitesting,
    multitest_function,
    microtests,
    compare,
    rng=random,
):
    """\
Performs Coupled test when passed the index of a master swarm, a list
of swarms, and a list of lists of microtests. Not tested with the
latest version of sds.run.\
"""

    if not multitesting == 1:
        raise NotImplementedError(
            "Sorry, I've not got around to multitesting for coupled "
            "sds yet. When I do, remember to make multitest_function"
            " default to None, as it should default to 'all' when "
            "scalar=True and 'max' when compare=False")

    test_results = []

    tested_agents = []

    for master_agent in swarms[master_swarm_num]:

        agents = [rng.choice(swarm) for swarm in swarms]

        agents[master_swarm_num] = master_agent

        hypotheses = tuple(agent.hypothesis for agent in agents)

        microtest = rng.choice(microtests)

        test_results.append(microtest(*hypotheses))

        tested_agents.append(agents)

    if False and compare:

        test_results = [
            test_result > rng.choice(test_results)
            for test_result
            in test_results
        ]

    for test_result, agents in zip(test_results, tested_agents):

        for agent in agents:

            agent.active = test_result
# master/slave synchronisation
def synchronous_coupled_test_phase(
    swarms,
    random,
    multitesting,
    multitest_function,
    microtests,
    compare,
    rng=random,
):
    """\
Perform a Synchronous coupled test phase. Not tested with the latest
version of sds.run.\
"""

    master_swarm_num = 0

    generic_coupled_test_phase(
        master_swarm_num,
        swarms,
        random,
        multitesting,
        multitest_function,
        microtests,
        compare,
        rng,
    )
def sequential_coupled_test_phase(
    swarms,
    random,
    multitesting,
    multitest_function,
    microtests,
    compare,
    rng=random,
):
    """\
Perform a Sequential master coupled test phase. Not tested with the
latest version of sds.run.\
"""

    for master_swarm_num in range(len(swarms)):

        generic_coupled_test_phase(
            master_swarm_num,
            swarms,
            random,
            multitesting,
            multitest_function,
            microtests,
            compare,
            rng,
        )
def iterate_coupled(
    swarms,
    random_hypothesis_functions,
    diffusion_functions,
    random,
    multitesting,
    multitest_function,
    report_iterations,
    test_phase_function,
    microtests,
    compare,
):
    """\
Perform an iteration of Coupled SDS. Not tested with the latest version
of sds.run.\
"""

    coupled_diffusion(
        swarms,
        random,
        random_hypothesis_functions,
        diffusion_functions)

    test_phase_function(
        swarms,
        random,
        multitesting,
        multitest_function,
        microtests,
        compare,
    )
def run_coupled(
    swarms,
    random_hypothesis_functions,
    max_iterations,
    diffusion_functions,
    random,
    multitesting,
    multitest_function,
    report_iterations,
    test_phase_function,
    hypothesis_string_function,
    max_cluster_report,
    microtests,
    compare,
):
    """\
Perform a Coupled SDS. Not tested with the latest version of sds.run.\
"""

    if max_iterations is None:

        iterator = itertools.count()

    else:

        iterator = range(max_iterations)

    if compare:

        multitest_function = max

    else:

        multitest_function = all

    try:

        for iteration in iterator:

            iterate_coupled(
                swarms,
                random_hypothesis_functions,
                diffusion_functions,
                random,
                multitesting,
                multitest_function,
                report_iterations,
                test_phase_function,
                microtests,
                compare,
            )

            if report_iterations and iteration % report_iterations == 0:

                clusters_list = tuple(
                    count_clusters(swarm)
                    for swarm
                    in swarms
                )

                agent_counts = tuple(len(swarm) for swarm in swarms)

                active_count = tuple(
                    sum(clusters.values())
                    for clusters
                    in clusters_list)

                print(agent_counts,active_count,clusters_list)

    except KeyboardInterrupt:

        pass

    return tuple(count_clusters(swarm) for swarm in swarms)
def count_clusters(swarm):
    """\
Returns the number of active agents at each hypothesis with at least one
active agent as a collections.Counter.\
"""

    return collections.Counter(
        agent.hypothesis
        for agent
        in swarm
        if agent.active
    )
def write_swarm(swarm, outfile):
    """\
Writes a swarm to a file-like object.\
"""
    json.dump(
        {
            'agent count':len(swarm),
            'clusters':count_clusters(swarm).most_common(),
        },
        outfile,
    )
def activity(swarm):
    """\
Return the proportion of the swarm which are active between 0 and 1.\
"""

    agent_count = len(swarm)

    active_count = sum(1 for agent in swarm if agent.active)

    return active_count/agent_count
def estimate_noise(
    microtests,
    random_hypothesis_function,
    noise_agent_count=100,
    iterations=100,
    rng=random,
):
    """\
Returns an estimate of the uniform background noise, between 0 and 1.\
"""

    def no_diffusion(swarm, random, random_hypothesis_function):
        for agent in swarm:
            agent.active = False
            agent.hypothesis = random_hypothesis_function(rng)

    noise_swarm = Agent.initialise(100)

    activities = []

    for iteration in range(iterations):
        synchronous_iterate(
            noise_swarm,
            microtests,
            random_hypothesis_function,
            no_diffusion,
            random,)

        activities.append(activity(noise_swarm))

    return sum(activities)/iterations
def swarm_from_clusters(agent_count, clusters):
    """\
Returns a swarm suitable for use in functions like sds.run.

Clusters should be a dictionary or collections.Counter of the
hypotheses of active agents.\
"""

    active_agents = (
        (
            Agent(hypothesis=hyp,active=True)
            for _ in
            range(count)
        )
        for hyp, count
        in clusters.items())

    inactive_count = agent_count - sum(clusters.values())

    return (
        Agent.initialise(inactive_count)
        + list(itertools.chain.from_iterable(active_agents)))
def pretty_print_with_values(
    clusters,
    search_space,
    max_clusters=None,
):

    string_template = "{c:6d} at hyp {h:6d} (value: {e:0.6f})"

    cluster_strings = [
        string_template.format(
            c=count,
            h=hyp,
            e=search_space[hyp])
        for hyp, count
        in clusters.most_common(max_clusters)
    ]

    return "\n".join(cluster_strings)
def simulate(
    scores,
    max_iterations=1000,
    report_iterations=500,
    diffusion_function=passive_diffusion,
    agent_count=1000,
    multitesting=1,
    multitest_function=all,
    random=random,
    random_hyp=None,
    halting_function=never_halt,
    halting_iterations=None,
):

    if random_hyp is None:

        def random_hyp(rnd): return rnd.randrange(1,len(scores))

    if halting_iterations is None:
        halting_iterations = report_iterations

    def make_microtest(test_num, rnd):
        return lambda hyp: rnd.random() < scores[test_num]

    microtests = [
        lambda hyp: random.random() < scores[hyp]
    ]

    swarm=Agent.initialise(agent_count=agent_count)

    swarm[0].active = True
    swarm[0].hypothesis = 0

    clusters = run(
        swarm=swarm,
        microtests=microtests,
        random_hypothesis_function=random_hyp,
        max_iterations=max_iterations,
        diffusion_function=passive_diffusion,
        multitesting=multitesting,
        multitest_function=multitest_function,
        random=random,
        report_iterations=report_iterations,
        halting_function=halting_function,
        halting_iterations=halting_iterations,
    )

    return clusters
