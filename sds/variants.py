def I_async(D, T, swarm):
    def I_prime():

        for agent in swarm:

            D(agent)

            T(agent)

    return I_prime


def H_time(duration):

    start = None

    def H():

        nonlocal start

        if start is None:

            start = datetime.datetime.now()

        return (now - start) > duration

    return H


def D_context_free(DH, swarm, rng):
    def D(agent):

        polled = rng.choice(swarm)

        if agent.inactive or polled.active:

            if agent.inactive and polled.active:

                agent.hyp = polled.hyp

            else:

                agent.active = False

                agent.hyp = DH()

    return D


def D_context_sensitive(DH, swarm, rng):
    def D(agent):

        polled = rng.choice(swarm)

        if polled.active and agent.inactive:

            agent.hyp = polled.hyp

        else:

            if agent.inactive or polled.active and agent.hyp == polled.hyp:

                agent.active = False

                agent.hyp = DH()

    return D


def D_multidiffusion(rng, swarm, multidiffusion_amount, DH):
    def D(agent):

        if agent.inactive:

            polled_agents = (rng.choice(swarm) for num in range(multidiffusion_amount))

            active_agents = [agent for agent in polled_agents if agent.active]

            if active_agents:

                agent.hyp = rng.choice(active_agents).hyp

            else:

                agent.hyp = DH()

    return D


def D_noise(swarm, DN, DH, rng):
    def D(agent):

        if agent.inactive:

            polled = rng.choice(swarm)

            if polled.active:

                agent.hyp = DN(polled.hyp)

            else:

                agent.hyp = DH()

    return D


def DN_gauss(mean, sigma, rng):
    """ add noise from a gaussian distribution to hypothesis transmission """

    def DN(hyp):

        return hyp + rng.gauss(mean, sigma)

    return DN


def DN_normal(rng):
    """ add noise from a normal gaussian distribution to hypothesis
    transmission """

    DN = DN_gauss(mean=0, sigma=1, rng=rng)

    return DN


def DH_continuous(min_hyp, max_hyp, rng):
    def DH():

        return rng.uniform(min_hyp, max_hyp)

    return DH


def T_comparative(TM, swarm, rng):
    def T_prime(agent):

        microtest = TM()

        agent_partial_evaluation = microtest(agent.hyp)

        polled = rng.choice(swarm)

        polled_partial_evaluation = microtest(polled.hyp)

        agent.active = agent_partial_evaluation > polled_partial_evaluation

    return T_prime


def TM_multitesting(microtests, rng, multitesting_amount, combinator):
    def TM():

        microtest_sample = iter(
            rng.choice(microtests) for num in range(multitesting_amount)
        )

        def multi_test(hyp):

            return combinator(microtest(hyp) for microtest in microtest_sample)

        return multi_test

    return TM


def H_threshold(swarm, threshold):
    """ makes a function for halting once the global activity is over a fixed
    threshold """

    def H():

        activity = swarm.activity
        # return activity > threshold
        if activity > threshold:
            log.log(
                SILENT, f"Threshold activity {activity} > threshold {threshold}. halt!"
            )
            return True
        else:
            log.log(
                SILENT,
                "Threshold activity {activity} < threshold {threshold}. not halting",
            )
            return False

    return H


def H_largest_cluster_threshold(swarm, threshold):
    """ makes a function for halting once the largest cluster activity is over
    a fixed threshold """

    def H():

        return swarm.largest_cluster.size >= threshold

    return H


def H_unique_hyp_count(swarm, unique_threshold):
    def H():

        unique_hyps = len(swarm.clusters)

        return unique_hyps < unique_threshold

    return H


def H_elite_cluster_consensus(swarm, elite_count, rng):

    elite_agents = rng.sample(swarm, elite_count)

    def H():

        elite_agent_gen = (agent for agent in swarm if agent in elite_agents)

        first_elite_agent = next(elite_agent_gen)

        elite_hyp = first_elite_agent.hyp

        return first_elite_agent.active and all(
            elite_agent.active and elite_agent.hyp == elite_hyp
            for elite_agent in elite_agent_gen
        )

    return H


def H_stable(swarm, max_memory_length, stability_threshold, min_stable_iterations):

    memory = collections.deque(maxlen=max_memory_length)

    stable_iterations = 0

    def H():

        nonlocal stable_iterations

        activity = swarm.activity

        memory.append(activity)

        mean_activity = sum(memory) / len(memory)

        deviations = [activity - mean_activity for activity in memory]

        sum_of_squared_deviations = sum(pow(deviation, 2) for deviation in deviations)

        standard_deviation = math.sqrt(sum_of_squared_deviations / len(memory))

        if standard_deviation > stability_threshold:

            stable_iterations = 0

            return False

        stable_iterations += 1

        is_stable = stable_iterations >= min_stable_iterations

        return is_stable

    return H


def H_weak(swarm, threshold_activity, stability_threshold, min_stable_iterations):

    stable_iterations = 0

    if not (
        ((2 * stability_threshold) < 1)
        and ((stability_threshold + threshold_activity) <= 1)
        and (threshold_activity - stability_threshold >= 0)
    ):

        raise ValueError("not valid values")

    def H():

        nonlocal stable_iterations

        activity = swarm.activity

        stability = abs(activity - threshold_activity)

        if stability < stability_threshold:

            stable_iterations += 1

        else:

            stable_iterations = 0

        return stable_iterations > min_stable_iterations

    return H


def H_strong(
    swarm, threshold_cluster_size, stability_threshold, min_stable_iterations  # a  # b
):

    stable_iterations = 0

    swarm_size = len(swarm)

    if not (
        ((2 * stability_threshold) < swarm_size)
        and ((stability_threshold + threshold_cluster_size) <= swarm_size)
        and (threshold_cluster_size - stability_threshold >= 0)
    ):

        raise ValueError(
            (
                f"not valid values. "
                f"((2 * stability_threshold) < 1) {((2 * stability_threshold) < 1)}, "
                f"((stability_threshold + threshold_cluster_size) <= 1) {((stability_threshold + threshold_cluster_size) <= 1)}, "
                f"(threshold_cluster_size - stability_threshold >= 0) {(threshold_cluster_size - stability_threshold >= 0)}."
            )
        )

    def H():

        nonlocal stable_iterations

        cluster_size = swarm.largest_cluster.agents

        stability = abs(cluster_size - threshold_cluster_size)

        if stability < stability_threshold:

            stable_iterations += 1

        else:

            stable_iterations = 0

        return stable_iterations > min_stable_iterations

    return H


def all_functions(*function_list):
    def F():

        results = [function() for function in function_list]

        log.log(SILENT, "all functions %s", results)

        return all(results)

    return F


def any_functions(*function_list):
    def F():

        results = [function() for function in function_list]

        log.log(SILENT, "any functions %s", results)

        return any(results)

    return F


def round_clusters(clusters):

    rounded_clusters = collections.Counter()

    for hyp, size in clusters.items():

        rounded_clusters[round(hyp)] += size

    return rounded_clusters
