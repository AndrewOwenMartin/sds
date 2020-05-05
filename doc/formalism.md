# A formal specification for SDS

As SDS can be modified in a practically unlimited number of ways a strict definition of what is and is not a variant cannot be given, instead a specification which succinctly describes the majority of the published variants is presented.

## Areas of potential variation in SDS

The four main areas of variation of SDS have been identified.

1. The *iteration* of the test phase and diffusion phase.
1. The *test phase*, where hypotheses are partially evaluated.
1. The *diffusion phase*, where new hypotheses are selected and potentially distributed amongst the swarm.
1. The *halting* conditions, in which the aim is to halt the procedure once SDS has converged to a solution.

A variant of SDS will be defined as a combination of its modes of iteration (I), diffusion (D), test (T) and halting (H).

## Formalism

An instance of SDS can be described as a combination of its mode of iteration (I) and halting (H). Before each iteration the halting function is evaluated and the process continues to perform iterations until the halting function evaluates as `true`.
`I` defines the mode of iteration, each evaluation of the `I` function will count as one iteration.
Each iteration of SDS modifies a swarm in place, once it has halted the solution can be extracted from the state of the swarm.

```python
def SDS(I, H):
    while(not H()):
        I()
```

### Mode of iteration - I

The mode of iteration in the original description of SDS is known as synchronous operation.
A single iteration is defined as having passed once all agents perform the diffusion phase followed by all agents performing the test phase.
This mode of iteration, named `I_sync` can be seen below.
The definition of the mode of iteration therefore requires the parameters D to define the mode of diffusion, T to define the mode of testing, and a reference to the swarm.
The returned function has no arguments and each call effects a single iteration on the swarm.

```python
def I_sync(D, T, swarm):
    def I():
        for agent in swarm:
            D(agent)
        for agent in swarm:
            T(agent)
    return I
```

### Mode of diffusion - D

The mode of diffusion is the mechanism by which agents share hypotheses or select new hypotheses, each search space therefore requires a unique method by which hypotheses are selected.
The definition of the mode of diffusion therefore requires the parameter DH which defines a function for selecting new hypotheses, and a reference to the swarm.
The returned function takes an agent as an argument and each call effects the mode of diffusion on that agent.
Passive diffusion relies on inactive agents requesting hypotheses from active agents and is the mode of diffusion of standard SDS.

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

### Mode of hypothesis selection - DH

The hypothesis selecting function is the method by which agents select new hypotheses.
The definition of DH therefore requires the parameter `hypotheses` which represents the set of all the possible hypotheses.
When implementing this function the set of all possible hypotheses may be fully enumerated, or selected as required by an underlying function.
Where full enumeration is likely to require less computational resources it will likely require more memory and conversely selecting hypotheses from a function will likely require more computational resources but less memory.
The returned function takes no arguments and each call returns a randomly selected hypothesis.

The standard method for selecting hypotheses is to uniformly randomly distribute new hypotheses over the search space.
This does not require any specific a priori knowledge of the task, and will evenly distribute the resources through the search space.
This technique does not modify its behaviour as a result of previous activity and so has the advantage of never being trapped indefinitely in locally optimal areas of the search space, but has the disadvantage of not responding to potentially helpful information.
`DH_uniform`Algorithm \ref{alg:dh-uniform} shows uniformly random hypothesis selection.

```python
def DH_uniform(hypotheses, rng):
    """ uniformly random hypothesis generation """
    def DH():
        return rng.choice(hypotheses)
    return DH
```

### Mode of testing - T
The mode of testing for each agent involves selecting a microtest, using that microtest to perform a partial evaluation of their hypothesis and updating their activity correspondingly.
The definition of the mode of testing therefore requires the parameter `TM` which defines a function for selecting a microtest.
The returned function takes an agent as an argument and each call effects the mode of testing on that agent.
Boolean testing is the mode of testing of standard SDS, it is important to note that while the mechanism of boolean testing is simple, it requires that a method of evaluating a hypothesis be defined as a set of boolean functions.
This is a significant requirement as the solutions to many search tasks cannot be evaluated with a set of boolean functions, or the functions themselves may include the use of predetermined thresholds.

```python
def T_boolean(TM):
    """ Boolean testing """
    def T(agent):
        microtest = TM()
        agent.active = microtest(agent.hyp)
    return T
```

### Mode of microtest selection - TM
The microtest selecting function is the method by which agents select how they will partially evaluate their hypothesis.
The definition of TM therefore requires the parameter `microtests` which represents the set of all possible microtests.
As with the `hypotheses` parameter to `DH` the set of microtests may be fully enumerated or selected as required, however the number of microtests is often to be small compared to other features of a search space and so full enumeration is more common.
The returned function takes no arguments and each call returns a randomly selected microtest.
Uniformly random microtest selection defines the microtest selection of standard SDS.


```python
def TM_uniform(microtests, rng):
    """ uniform microtest selection """
    def TM():
        return rng.choice(microtests)
    return TM
```

### Mode of halting - H
The halting function is the method by which an instance of SDS determines whether or not to continue to call `I` and hence perform further iterations.
There are many different halting functions, a very simple example is to halt after a predetermined number of iterations.
This method, called fixed iterations halting, requires the parameter `max_iterations` to define the maximum number of iterations that will elapse.
The returned function takes no arguments and will return `false` until it has been called a number of times greater than `max_iterations`.
Other halting functions perform more complicated operations over the current and previous states of the swarm and so require a more complicated set of parameters.

```python
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
```

### Standard SDS

Standard sds can be therefore denoted as follows

```python
def standard_sds(swarm, hypotheses, microtests, rng):

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

    # SDS executes the variant defined as a combination of I and H
    sds.SDS(I=I, H=H)
```
