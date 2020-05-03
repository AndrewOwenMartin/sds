import collections
import logging

log = logging.getLogger(__name__)


class Agent:
    def __init__(self, active=False, hyp=None):
        self.active = active
        self.hyp = hyp

    @property
    def inactive(self):

        return not self.active

    @property
    def clone(self):

        return ReadOnlyAgent(active=self.active, hyp=self.hyp)

    def __iter__(self):

        yield ("active", self.active)
        yield ("hyp", self.hyp)

    def __str__(self):

        if self.active:

            return str(self.hyp)

        else:

            return "Inactive"


class Swarm(collections.UserList):
    def __init__(self, agent_count=None, swarm=None, AgentClass=Agent):

        if swarm is None:

            if agent_count is None:

                raise ValueError("One of agent_count or swarm must be passed")

            else:

                self.data = [AgentClass() for _ in range(agent_count)]

        else:

            self.data = swarm

    def __str__(self):

        return ", ".join(
            f"(Hyp:{hyp}, Agents:{cluster_size})"
            for hyp, cluster_size in self.clusters.most_common()
        )

    @property
    def activity(self):

        if not self:

            return 0

        return sum(1 for agent in self if agent.active) / len(self)

    @property
    def clusters(self):

        return collections.Counter(agent.hyp for agent in self if agent.active)

    @property
    def largest_cluster(self):

        try:

            hyp, agents = self.clusters.most_common(1)[0]

        except IndexError:

            hyp, agents = None, 0

        return Cluster(hyp=hyp, agents=agents, size=agents / len(self))

    def report_clusters(self, significant_hypotheses):

        clusters = self.clusters

        opt = tuple((hyp, clusters[hyp]) for hyp in significant_hypotheses)

        active = sum(clusters.values())

        inactive = len(self) - active

        noise_active = active - sum(size for hyp, size in opt)

        log.debug(
            "Opt hyp: %s, active: %s, inactive: %s, noise active: %s",
            opt,
            active,
            inactive,
            noise_active,
        )

        return {
            "opt-hyp": opt,
            "active": active,
            "inactive": inactive,
            "noise active": noise_active,
        }


Cluster = collections.namedtuple("Cluster", ("hyp", "agents", "size"))


def SDS(I, H):

    while not H():

        I()


def I_sync(D, T, swarm):
    def I():

        for agent in swarm:

            D(agent)

        for agent in swarm:

            T(agent)

    return I


def D_passive(DH, swarm, rng):
    def D(agent):

        if agent.inactive:

            polled = rng.choice(swarm)

            if polled.active:

                agent.hyp = polled.hyp

            else:

                agent.hyp = DH()

    return D


def DH_uniform(hypotheses, rng):
    """ uniformly random hypothesis generation """

    def DH():

        return rng.choice(hypotheses)

    return DH


def TM_uniform(microtests, rng):
    """ uniform microtest selection """

    def TM():

        return rng.choice(microtests)

    return TM


def H_fixed(iterations):
    """ makes a function for halting after a fixed number of iterations """

    iteration_count = 0

    def H():

        nonlocal iteration_count

        iteration_count += 1

        if iteration_count > iterations:

            log.log(logging.DEBUG, "h_fixed(%s) halting", iterations)

            return True

        else:

            return False

    return H


def T_boolean(TM):
    """ Boolean testing """

    def T(agent):

        microtest = TM()

        agent.active = microtest(agent.hyp)

    return T
