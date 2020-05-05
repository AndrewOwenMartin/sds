```
INITIALISE (mappings);

REPEAT

    TEST (mappings);

    DIFFUSE (mappings);

UNTIL TERMINATION;
// SDS  as introduced by Bishop in 1989
```

# Introduction

Stochastic Diffusion Search (SDS) is a swarm intelligence algorithm characterised by two features.

1. Partial evaluation of solutions
1. Diffusion of promising solutions throughout the swarm

There are two canonical stories which describe the operation of SDS in simple terms.

* [The Restaurant Game](doc/restaurant-game.md)
* [The Mining Game](doc/mining-game.md)

This library allows you to quickly and flexibly apply SDS to many problems.

# Example

In this example we will use SDS to locate a model string in a larger search space string.
In this case to locate something is to identify the index of the search space which is the first character of the model.

```python
search_space = "xxxxxhexlodxxxsakllajadsweklhheaekfjllkahelehlehlehlexxx"

model = "hello"
```

A task of SDS must be described as a set of "hypotheses" and a set of "microtests", the hypotheses are the set of all possible solutions. In this case it is the set of all possible indices of the search space. The microtests are the set of all partial evaluations of the hypothesis.

```python
hypotheses = range(len(search_space))
```

The search will find the hypothesis that passes the most microtests, an ideal solution is one that passes all microtests.

For this task there will be one microtest for each letter in the model, each one will answer the question "Is the *n*th letter from my hypothesis the same as the *n*th letter of the model?"

```python
microtests = [
    lambda hyp: hyp+0 < len(search_space) and search_space[hyp+0] == "h" 
    lambda hyp: hyp+1 < len(search_space) and search_space[hyp+1] == "e" 
    lambda hyp: hyp+2 < len(search_space) and search_space[hyp+2] == "l" 
    lambda hyp: hyp+3 < len(search_space) and search_space[hyp+3] == "l" 
    lambda hyp: hyp+4 < len(search_space) and search_space[hyp+4] == "o" 
]
```

These functions have been defined manually, but Python provides a number of ways to automatically define functions for more complex tasks. Even this example could have been produced by looping over a single function which returns test functions like the ones defined here.

These hypotheses and microtests will be processed by a swarm of agents.

```python
import sds

agent_count = 50

swarm = sds.Swarm(agent_count=agent_count)
```

Now we have to define the SDS variant which will manipulate the swarm of agents. There are an unlimited number of variants of SDS and with unlimited dimensions of variation. Standard SDS is defined as such.

```python
# DH is the mode of hypothesis selection.
# DH_uniform is uniformly random hypothesis selection.
DH = sds.DH_uniform(hypotheses=hypotheses, rng=rng)

# D is the mode of diffusion.
# D_passive is passive diffusion.
D = sds.D_passive(DH=DH, swarm=swarm, rng=rng)

# TM is the mode of microtest selection.
# TM_uniform is uniformly random microtest selection.
TM = sds.TM_uniform(microtests, rng=rng)

# T is the mode of testing.
# T_boolean is boolean testing.
T = sds.T_boolean(TM=TM)

# I is the mode of iterations.
# I_sync is synchronous iteration.
I = sds.I_sync(D=D, T=T, swarm=swarm)

# H is the mode of halting.
# H_fixed is fixed number of iterations halting.
H = sds.H_fixed(iterations=max_iterations)
```

These features are defined in the [Formalism of SDS](doc/formalism.md)

You can now run `sds.SDS`, this will process the `swarm` and modify it in-place.

```python
sds.SDS(I=I, H=H)
```

And a cluster (a number of agents maintaining the same hypothesis) will form at the hypothesis which passes the most microtests.

```python
>>> print("All clusters", swarm.clusters.most_common())

All clusters [(5, 38)]

>>> print("Largest cluster", swarm.largest_cluster)

Largest cluster Cluster(hyp=5, agents=38, size=0.76)
```
