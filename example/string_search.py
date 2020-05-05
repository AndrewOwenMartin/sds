import sds
import random
import functools
def microtest(hyp, offset, search_space, model):

    search_space_index = hyp + offset

    return (
        search_space_index < len(search_space) # avoid out of bounds index errors
        and search_space[search_space_index] == model[offset]
    )
def make_microtests(search_space, model):

    return [
        functools.partial(
            microtest, offset=offset, search_space=search_space, model=model
        )
        for offset
        in range(len(model))
    ]
def main():

    agent_count = 50
    rng = random.Random()

    max_iterations = 100
    model = "hello"

    search_space = "xxxxxhexlodxxxsakllajadsweklhheaekfjllkahelehlehlehlexxx"
    swarm = sds.Swarm(agent_count=agent_count)
    microtests = make_microtests(search_space, model)
    hypotheses = range(len(search_space))
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

    # SDS executes the variant defined as a combination of I and H
    sds.SDS(I=I, H=H)

    # The state of the swarm is now updated
    print("All clusters", swarm.clusters.most_common())
    print("Largest cluster", swarm.largest_cluster)


if __name__ == "__main__":

    main()
