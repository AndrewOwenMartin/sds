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

To see an animation that may help you to understand the process, [go here](https://www.aomartin.co.uk/sds-animation/).

This library allows you to quickly and flexibly apply SDS to many problems.

# Definitions

This library allows you to define an instance of SDS using higher-order functions, that is functions which return other functions.

The main functions are named as follows:
* `SDS` the wrapper function, calling this iterates the algorithm until halt.
* `I` the iteration function, called once per iteration.
* `D` the diffusion function, takes an agent and modifies it as per the mode of diffusion. This function is normally responsible the hypothesis of an agent.
* `T` the test function, takes an agent and modifies it as per the mode of testing. This function is normally responsible for the activity of an agent.
* `H` the halting function, this is a function that gets called once per iteration, when it returns *true*, the algorithm halts.

Those are the main functions, it would be hard to describe anything as a variant of SDS if it does not at least use those functions. I also expect any model that is related to SDS to implement something akin to the following two functions.

* `DH` the hypothesis selection function, a function that takes no parameters and returns a hypothesis. This function is not required to be a pure function, even though it takes no parameters, it may still be influenced by state such as the activity of other agents or the history of the calling agent.
* `TM` the microtest selection function, a function that takes no parameters and returns a microtest function. The microtest function takes a hypothesis as an argument and most commonly returns a boolean value.

What follows is a description of the functions which define **Standard SDS** (what is referred to in some publications as Vanilla SDS), which implements passive diffusion, boolean testing, synchronous iteration, full connectivity, uniformly random hypothesis selection and uniformly random agent polling,

# Standard SDS

First the definition of SDS, this isn't actually a higher order function. It simply takes `I` and `H` and calls `I` until `H` returns *true*.

```python
def SDS(I, H):

    while not H():

        I()
```

## Iteration

The standard `I` function, known as synchronous iteration, takes the parameters `D` (the mode of diffusion), `T` (the mode of testing) and a swarm. It returns a function which performs `D` on all agents followed by performing `T` on all agents.

```python
def I_sync(D, T, swarm):

    def I():

        for agent in swarm:
            D(agent)
        for agent in swarm:
            T(agent)

    return I
```

## Diffusion

The standard `D` function, known as passive diffusion takes the parameters `DH` (new hypothesis selection), a swarm, and `rng` a random number generator. It performs uniformly random agent polling with the Python function `rng.choice` and selects new hypotheses with `DH`.

```python
def D_passive(DH, swarm, rng):

    def D(agent):

        if agent.inactive:
            polled = rng.choice(swarm)
            if polled.active:
                agent.hyp = polled.hyp
            else:
                agent.hyp = DH()

    return D
```

### Hypothesis selection

The `DH` function for uniformly random hypothesis selection is simple, though it requires `hypothesis' to be previously defined and passed as a parameter. This can be any data structure understood by the [[rng.choice]] function.

```python
def DH_uniform(hypotheses, rng):

    def DH():

        return rng.choice(hypotheses)

    return DH
```

## Testing

The standard `T` function, known as boolean testing takes the parameter `TM` (random microtest selection) and returns a function which performs a randomly selected microtest against the hypothesis of a passed agent.

```python
def T_boolean(TM):

    def T(agent):

        microtest = TM()

        agent.active = microtest(agent.hyp)

    return T
```

### Microtest selection

The `TM` function for uniformly random microtest selection also is simple, though it requires `microtests` to be previously defined and passed as a parameter. It also requires a random number generator is passed as a parameter.

```python
def TM_uniform(microtests, rng):

    def TM():

        return rng.choice(microtests)

    return TM
```

## Halting

Finally a halting function needs to be defined, to keep it simple I'll use the function for halting after a fixed number of iterations. This higher-order function therefore requires the maximum number of iteration as a parameter, and returns a function that returns true once it has been called that number of times. Ignore the [[nonlocal]] Python keyword, that's required to clarify the scope of the `iteration_count` variable.


```python
def H_fixed(iterations):

    iteration_count = 0

    def H():

        nonlocal iteration_count

        iteration_count += 1

        return bool(iteration_count > iterations)

    return H
```

## Conclusion

Given the above an instance of SDS can be defined in a way resembling maths.

```python
T_standard = T_boolean(TM_uniform(microtests, rng))

D_standard = D_passive(DH_uniform(hypotheses, rng), swarm, rng)

I_standard = I_sync(T_standard, D_standard)

SDS_standard = lambda H: SDS(I_standard, H)

H_standard = H_fixed(1000)

SDS_standard(H=H_standard)

```

or as a fully defined convenience function

```python
def standard_sds(microtests, hypotheses, agent_count, max_iterations):

    rng = random.Random() # instantiate a random number generator

    swarm = sds.Swarm(agent_count=agent_count) # instantiate a swarm of agents

    DH = sds.DH_uniform(hypotheses=hypotheses, rng=rng)

    D = sds.D_passive(DH=DH, swarm=swarm, rng=rng)

    TM = sds.TM_uniform(microtests=microtests, rng=rng)

    T = sds.T_boolean(TM=TM)

    I = sds.I_sync(D=D, T=T, swarm=swarm)

    H = sds.H_fixed(iterations=max_iterations)

    sds.SDS(I=I, H=H)

    return swarm
```

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
