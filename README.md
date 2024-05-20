# CarlaLoop: A Comprehensive Closed-Loop Simulation Framework for Autonomous Driving Systems

CarlaLoop is a simulation framework designed to facilitate rigorous testing and evaluation of autonomous driving systems (ADSs). Leveraging the CARLA simulator, CarlaLoop seamlessly integrates with a variety of agents and employs diverse search algorithms to explore an endless array of driving scenarios in a closed-loop environment. This platform is engineered to provide a dynamic and versatile testing ground, ensuring that ADSs can be assessed under a multitude of conditions, thereby enhancing their robustness and reliability.

Key Features:

- **Integration with CARLA**: Utilizes the advanced capabilities of the CARLA simulator for high-fidelity, realistic driving scenarios.
- **Agent Compatibility**: Connects with various autonomous driving agents, allowing for comprehensive testing across different system architectures.
- **Algorithmic Flexibility**: Supports multiple search algorithms to systematically explore and test diverse driving scenarios.
- **Closed-Loop Testing**: Enables continuous, iterative testing processes to refine and improve autonomous driving performance.

CarlaLoop stands as a pivotal tool for researchers and developers aiming to push the boundaries of autonomous driving technology, offering a robust platform for simulation-based validation and verification.

## Contents

- [About](#about)
- [Setup](#setup)
  - [Install Carla](#install-carla)
  - [Install CarlaLoop](#install-carlaloop)
  - [Setup config](#setup-config)
- [Run simulation](#run-simulation)
- [Integration with agents](#integration-with-agents)
  - [Setup Interfuser](#setup-interfuser)
  - [TFPP](#tfpp)
- [Make more scenarios](#make-more-scenarios)

## About

CarlaLoop use Carla leaderboard and scenario_runner as the base and extend it to support closed-loop simulation. 

By default, we support the following agents:
- Behavior Agent (by Carla)
- [Interfuser](https://github.com/opendilab/InterFuser)
- [TFPP](https://github.com/autonomousvision/carla_garage)

we also support the following search algorithms:
- Random Search
- Particle Swarm Optimization
- Genetic Algorithm
- Replay

Default scenarios (see `leaderboard/data/routes_carlaloop.xml`):
- Hard Brake
- Cut In (1 NPC)
- Cut In (2 NPC)
- Opposite Vehicle Taking Priority
- Non-signalized Junction Left Turn
- Non-signalized Junction Right Turn

This project is developed and tested on Ubuntu 20.04.

## Setup

### Install Carla

Use the Carla 0.9.15 package is recommended. You can download it from [here](https://carla.org/2023/11/10/release-0.9.15/) and follow the installation guide.
Other versions of Carla may also work, but you may need to modify the code to make it work.

Test run Carla to make sure it works.

```bash
cd path_to_carla
./CarlaUE4.sh
```

If you see the Carla simulator window, and the spectator is moving when you drag the mouse, it means Carla is installed successfully.

### Install CarlaLoop

```bash
git clone --recurse-submodules https://github.com/TayYim/CarlaLoop.git
```

```bash
cd CarlaLoop
conda env create -n carlaloop python=3.10
conda activate carlaloop
pip install -r requirements.txt
```

Setup Carla leaderboard and scenario_runner
    
```bash
cd leaderboard
conda create -n lb python=3.7
conda activate lb
pip install -r requirements.txt
cd ../scenario_runner
pip install -r requirements.txt
```

### Setup config

Modify `config.json`:
- CARLA_ROOT: the path to your Carla installation
- SCENARIO_RUNNER_ROOT: the path to your scenario_runner installation
- LEADERBOARD_ROOT: the path to your leaderboard installation
- ROUTE_FILE: by default, it is "routes_carlaloop.xml". If you don't want to use the default routes, you can create your own routes and modify this value.
- LB_PYTHON_PATH: the path to the python executable in the "lb" environment

You can get the python path by running the following command:
```bash
conda activate lb
which python
```

## Run simulation

`search/cutin_two.py` is an example of running a closed-loop simulation with the cut in scenario and two NPC vehicles.

```bash
conda activate carlaloop
python search/cutin_two.py
```

By default, it will replay 4 pre-defined scenarios. You can modify the `search/cutin_two.py` to change the search algorithm, the number of iterations, and other parameters.

After the simulation is finished, you can find the results in the `output` folder. The file `search-*.csv` contains the results of each simulation. 
If a collision happens, `collision_status` will record the status of EGO and NPC vehicles at the time of the collision. 
The values in each status list are `[Location X, Location Y, Velocity, Yaw angle]`.
See `scenario_runner/srunner/scenariomanager/scenarioatomics/atomic_criteria.py L: 400` for more details.

You can modify the search loss function in `_simulate_carla()` in `search/basic_search.py`.

## Integration with agents

By default, 'ba' (Behavior Agent) is used. You can modify the agent in `search/cutin_two.py` to use other agents.

Currently, we support the following agents:
- 'interfuser': [Interfuser](https://github.com/opendilab/InterFuser)
- 'tfpp': [TFPP](https://github.com/autonomousvision/carla_garage)

To use them, you need to install the agents.

> [!Note]
> Both Interfuser and TFPP are developed to run in Carla Leaderboard 1.0. CarlaLoop use Carla Leaderboard 2.0. Some modifications are needed to make them work in CarlaLoop.

### Setup Interfuser

You can clone the Interfuser repository anywhere you like.

```bash
git clone https://github.com/opendilab/InterFuser.git
```

```bash
sudo apt install build-essential -y
cd InterFuser
conda create -n interfuser python=3.7
conda activate interfuser
pip install -r requirements.txt

cd interfuser
python setup.py develop
pip install --upgrade setuptools
```

You also need to install requirements of leaderboard and scenario_runner in the `interfuser` environment.

```bash
conda activate interfuser
cd CarlaLoop/leaderboard
pip install -r requirements.txt
cd ../scenario_runner
pip install -r requirements.txt
```

Download the pre-trained model from [here](http://43.159.60.142/s/p2CN), put it in `InterFuser/leaderboard/team_code/interfuser.pth.tar`. 

Modify `InterFuser/leaderboard/team_code/interfuser_config.py L:25`, change `model_path` to absolute path of `interfuser.pth.tar`.

You can also modify max_speed according to your need.

Modify `config.json` in CarlaLoop, change `INTERFUSER_ROOT` to the path of Interfuser, and `INTERFUSER_PYTHON_PATH` to the python executable in the `interfuser` environment.

Change the agent in `CarlaLoop/search/cutin_two.py` to 'interfuser'.


> [!Note] 
> InterFuser will generate a lot of logs. Watch your disk space.

## TFPP

Similar to Interfuser, you can clone the TFPP repository anywhere you like.

```bash
git clone https://github.com/autonomousvision/carla_garage.git
```

```bash
cd carla_garage
sudo apt install build-essential -y
conda env create -f environment.yml
conda activate garage
```

You also need to install requirements of leaderboard and scenario_runner in the `garage` environment.

```bash
conda activate garage
cd CarlaLoop/leaderboard
pip install -r requirements.txt
cd ../scenario_runner
pip install -r requirements.txt
```

Download the pre-trained model from [here](https://s3.eu-central-1.amazonaws.com/avg-projects-2/jaeger2023arxiv/models/pretrained_models.zip), extract it and put it in `carla_garage/team_code`.

Download [global_route_planner_dao.py](https://github.com/carla-simulator/carla/blob/c7b20769fb68bda1ebd847af07c321d12ed62831/PythonAPI/carla/agents/navigation/global_route_planner_dao.py) and put it in `CARLA_ROOT/PythonAPI/carla/agents/navigation/`.

Modify `config.json` in CarlaLoop, change `TFPP_ROOT` to the path of garage, and `TFPP_PYTHON_PATH` to the python executable in the `garage` environment.

Change the agent in `CarlaLoop/search/cutin_two.py` to 'tfpp'.


## Make more scenarios

CarlaLoop supports custom scenarios. 
You can create your own scenarios following the guidance of Carla [leaderboard](https://leaderboard.carla.org/get_started/) and [scenario_runner](https://github.com/carla-simulator/scenario_runner).

CarlaLoop use the leaderboard-2.0 branch of leaderboard and scenario_runner.

Scenarios are defined in `scenario_runner/srunner/scenarios`. You can create your own scenarios by modifying the existing ones or creating new ones.

After having standalone scenarios, you can add them to the routes file. The routes file is an XML file that describes several sceanrios to run along a route. You can find the default routes file in `leaderboard/data/routes_carlaloop.xml`.