import sds.standard
import logging

log = logging.getLogger(__name__)


def D_confirmation(swarm, removed_clusters, DH, rng):

    non_removed_agents = [agent for agent in swarm if not agent.removed]

    def D(agent):

        if agent.removed:

            return

        polled = rng.choice(non_removed_agents)

        if agent.active:

            if polled.active and agent.hyp == polled.hyp:

                agent.terminating = True

        else:

            if polled.active:

                if polled.terminating:

                    agent.remove(final_hyp=polled.hyp)
                    non_removed_agents.remove(agent)

                    removed_clusters[polled.hyp] += 1

                else:

                    agent.hyp = polled.hyp

            else:

                agent.hyp = DH()

    return D


def D_independent(swarm, removed_clusters, DH, rng):

    remaining_swarm = [agent for agent in swarm if not agent.removed]

    swarm_is_empty = False

    def D(agent):

        nonlocal swarm_is_empty

        if agent.removed or swarm_is_empty:

            return

        while True:

            polled = rng.choice(remaining_swarm)

            if polled is not agent:

                break

        if agent.inactive and polled.inactive:

            agent.hyp = DH()
            polled.hyp = DH()

        elif agent.active and (not agent.terminating) and polled.inactive:

            polled.hyp = agent.hyp

        elif polled.active and (not polled.terminating) and agent.inactive:

            agent.hyp = polled.hyp

        elif agent.terminating and not polled.terminating:

            polled.remove(final_hyp=agent.hyp)
            remaining_swarm.remove(polled)
            swarm_is_empty = len(remaining_swarm) < 2

            removed_clusters[agent.hyp] += 1

        elif polled.terminating and not agent.terminating:

            agent.remove(final_hyp=polled.hyp)
            remaining_swarm.remove(agent)
            swarm_is_empty = len(remaining_swarm) < 2

            removed_clusters[polled.hyp] += 1

        elif agent.terminating and polled.terminating:

            both_agents = [agent, polled]
            rng.shuffle(both_agents)
            removed, removing = both_agents

            removed.remove(final_hyp=removing.hyp)
            remaining_swarm.remove(removed)
            swarm_is_empty = len(remaining_swarm) < 2

            removed_clusters[removing.hyp] += 1

        elif agent.hyp == polled.hyp:

            agent.terminating = polled.terminating = True

    return D


def D_running_mean(DH, quorum_threshold, min_interaction_count, activities, swarm, rng):

    non_removed_agents = [agent for agent in swarm if not agent.removed]

    swarm_is_empty = False

    def D(agent):

        nonlocal swarm_is_empty

        if agent.removed or swarm_is_empty:

            return

        polled = rng.choice(non_removed_agents)

        if agent.inactive:

            agent.memory.clear()

            if polled.active:

                agent.hyp = polled.hyp

            else:

                agent.hyp = DH()

        else:  # agent is active

            if agent.terminating:

                if not (agent.hyp == polled.hyp):

                    polled.remove(final_hyp=agent.hyp)
                    non_removed_agents.remove(polled)
                    swarm_is_empty = len(non_removed_agents) < 2

            else:  # agent has not sensed quorum

                activity_at_hypothesis = activities[agent.hyp] / len(non_removed_agents)

                agent.memory.append(activity_at_hypothesis)

                interaction_count = len(agent.memory)

                # confidence is 0 if interaction_count < min_iteration_count
                confidence = interaction_count >= min_interaction_count and (
                    sum(agent.memory) / interaction_count
                )

                if confidence >= quorum_threshold:
                    # agent has sensed quorum

                    agent.terminating = True

    return D


def D_qs(DH, quorum_threshold, decay, swarm, rng):

    non_removed_agents = [agent for agent in swarm if not agent.removed]

    swarm_is_empty = False

    def D(agent):

        nonlocal swarm_is_empty

        if agent.removed or swarm_is_empty:

            return

        polled = rng.choice(non_removed_agents)

        if agent.inactive:

            agent.confidence = 0

            if polled.active:

                agent.hyp = polled.hyp

            else:

                agent.hyp = DH()

        else:  # agent is active

            if agent.terminating:

                if not (agent.hyp == polled.hyp):

                    polled.remove(final_hyp=agent.hyp)
                    non_removed_agents.remove(polled)
                    swarm_is_empty = len(non_removed_agents) < 2

            else:  # agent has not sensed quorum

                if polled.active and (agent.hyp == polled.hyp):

                    agent.confidence += 1

                agent.confidence *= decay

                if agent.confidence >= quorum_threshold:  # agent has sensed quorum

                    agent.terminating = True

    return D


class ReducingAgent(sds.Agent):
    def __init__(self, active=False, hyp=None, terminating=False, removed=False):
        super().__init__(active=active, hyp=hyp)
        self.terminating = terminating
        self.removed = removed

    def remove(self, final_hyp):

        self.removed = True
        self.hyp = final_hyp
        self.active = False
        self.terminating = False

    def __str__(self):

        s = super().__str__()

        if self.terminating:

            s = f"{s} Terminating"

        elif self.removed:

            s = f"{self.hyp} Removed"

        return s

    def __iter__(self):

        yield from super().__iter__()
        yield ("terminating", self.terminating)
        yield ("removed", self.removed)


class QSAgent(ReducingAgent):
    def __init__(
        self, active=False, hyp=None, terminating=False, removed=False, confidence=0
    ):
        super().__init__(
            active=active, hyp=hyp, terminating=terminating, removed=removed
        )
        self.confidence = confidence

    def __str__(self):

        s = super().__str__()

        if self.active:

            s = f"{s} Confidence: {self.confidence:2.2g}"

        return s

    def __iter__(self):

        yield from super().__iter__(self)
        yield ("confidence", self.confidence)


class QSRunningMeanAgent(ReducingAgent):
    def __init__(self, active, hyp, terminating, removed, memory):

        super().__init__(
            active=active, hyp=hyp, terminating=terminating, removed=removed
        )

        self.memory = memory

    def new(memory_length):

        return QSRunningMeanAgent(
            active=False,
            hyp=None,
            terminating=False,
            removed=False,
            memory=collections.deque(maxlen=memory_length),
        )

    def __str__(self):

        s = super().__str__()

        if self.active:

            memory_str = ", ".join(format(avg, ".2g") for avg in self.memory)

            s = f"{s} Confidence: [{memory_str}]"

        return s

    def __iter__(self):

        yield from super().__iter__(self)
        yield ("memory", self.memory)


class ReducingSwarm(sds.standard.Swarm):
    @property
    def clusters(self):

        return collections.Counter(
            agent.hyp for agent in self if agent.active or agent.removed
        )

    @property
    def size(self):

        return len(self) - len(self.removed)

    @property
    def removed(self):

        return [agent for agent in self if agent.removed]


def H_all_terminating(swarm):
    def H():

        halt = all(agent.terminating for agent in swarm if not agent.removed)

        return halt

    return H


def H_empty_swarm(swarm):
    def H():
        return all(agent.removed for agent in swarm)

    return H


def H_reducing(swarm):

    is_empty = H_empty_swarm(swarm)
    is_all_terminating = H_all_terminating(swarm)

    return halting_methods.any_functions(is_empty, is_all_terminating)


def T_reducing(TM):

    T_inner = sds.standard.T_boolean(TM=TM)

    def T(agent):

        if not (agent.terminating or agent.removed):

            T_inner(agent)

    return T
