
import math
from RegionsManager import Expert

if __name__ == "__main__":

    # generating exemplars
    exemplars = []
    for i in range(1,15):
        exemplar = ((math.floor(100*math.sin(math.pi*i/4)),),
                    (math.floor(100*math.sin(math.pi*i/3)),),
                    (math.floor(100*math.sin(math.pi*i/2)),))
        exemplars.append(exemplar)
    print("Generated exemplars: ", exemplars)

    # instantiate an Expert
    expert = Expert()

    # appending data to expert
    for exemplar in exemplars:

        S = exemplar[0]
        M = exemplar[1]
        S1 = exemplar[2]
        print("\n Test case ", S, M, S1)

        # have the expert make prediction
        S1_predicted = expert.predict(S, M)
        print(S1_predicted)

        # do action

        # add exemplar to expert
        expert.append(S + M, S1)
        expert.split()  # won't actually split if the condition is not met

        L, M1 = expert.get_expected_reward(S1)
        print("Expected Reward", L)
        print("Next Action", M1)

    expert.print()

