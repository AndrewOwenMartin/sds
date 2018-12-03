import collections

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

    def __iter__(self):
        """ Iterating over an agent returns its hypothesis, then its
            activity.
        """
        yield self.hypothesis
        yield self.active
    
    def __str__(self):

        return "<Agent h={h} a={a}>".format(
            h=self.hypothesis,
            a=self.active,
        )

ReadOnlyAgent = collections.namedtuple(
    "ReadOnlyAgent",
    ("hypothesis","active"),
)

ReadOnlyAgent.__doc__ = """\
namedtuple representation of an agent. Attributes are hypothesis and
active.\
"""

def make_swarm(agent_count, hypothesis=False, active=False):

    return [
        Agent(hypothesis=hypothesis, active=active)
        for agent_num
        in range(agent_count)
    ]
