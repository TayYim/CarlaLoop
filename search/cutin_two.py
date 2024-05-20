from basic_search import BasicSearch
from pathlib import Path

from datetime import datetime


class FrontCutInWithTwoNPC(BasicSearch):
    # Overwrite methods according to your need
    pass


if __name__ == "__main__":

    name = "front_cut_in_with_two_npc"
    n_particles = 2
    max_iter = 2
    # agent: ba (behavior agent), tfpp, interfuser
    agent = "ba"
    random_seed = 0
    formatted_time = datetime.now().strftime("%m%d%H%M")

    output_path = Path(
        f"output/{name}/{agent}/{formatted_time}_{n_particles}x{max_iter}_{random_seed}"
    )

    scenarioInstance = FrontCutInWithTwoNPC(
        name=name,
        render=True,
        route_id=2,
        save_data=True,
        output_path=output_path,
        debug=True,
        random_seed=random_seed,
        agent=agent,
    )

    # Shall align with the params in routes xml file
    # param_name: [min, max]
    params_dict = {
        "absolute_v": [0, 21.214],
        "relative_p_1": [0.238, 69.291],
        "relative_v_1": [-8.163, 9.373],
        "relative_p_2": [-89.708, -0.005],
        "relative_v_2": [-10.132, 13.686],
    }

    scenarioInstance.setup(params_dict)

    # Example 1: Replay the given params
    params_list = [
        [5, 10, 2, -10, 5],
        [5, 15, -2, -20, 10],
        [10, 15, -2, -20, 10],
        [1, 15, -2, -20, 10],
    ]
    scenarioInstance.replay(params_list)

    # Example 2: Particle Swarm Optimization
    # scenarioInstance.search_pso(n_particles=n_particles, max_iter=max_iter)

    # Example 3: Genetic Algorithm
    # scenarioInstance.search_ga(n_population=n_particles, n_generation=max_iter)

    # Example 4: Random Search
    # scenarioInstance.search_random(n_iter=max_iter)
