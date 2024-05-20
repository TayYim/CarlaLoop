import numpy as np
from sko.PSO import PSO
from sko.GA import GA
import time
import types
from datetime import datetime
import os
import random
import functools
import subprocess
import json
import os
import signal
import sys
from utils import change_route_value, save_pickle, save_csv, is_process_running

np.seterr(divide="ignore", invalid="ignore")


class BasicSearch:
    def __init__(
        self,
        name="BasicSearch",
        render=True,
        route_id=2,
        save_data=True,
        output_path="output/",
        debug=False,
        random_seed=0,
        agent="ba",
    ):

        self.search_method = None
        self.route_id = str(route_id)
        self.render = render  # Show carla window or not

        self.debug = debug
        self.params_dict = None

        self.save_data = save_data

        self.set_random_seed(random_seed)

        self.output_root_path = output_path
        self.set_name(name)

        # Extra, for additional information if needed
        self.extra_info = None

        self.run_step = None

        # Agent Config
        self.agent = agent  #  ba, interfuser, tfpp
        current_path = os.path.dirname(os.path.abspath(__file__))
        parent_path = os.path.dirname(current_path)

        # Read config json
        with open(os.path.join(parent_path, "config.json"), "r") as f:
            self.config = json.load(f)

        simulate_script_dict = {
            "ba": os.path.join(parent_path, "carla_simulate/simulate_ba.sh"),
            "interfuser": os.path.join(
                parent_path, "carla_simulate/simulate_interfuser.sh"
            ),
            "tfpp": os.path.join(parent_path, "carla_simulate/simulate_tfpp.sh"),
        }

        self.simulate_script = simulate_script_dict[self.agent]

        # Carla config
        self.route_file = os.path.join(
            self.config["env"]["LEADERBOARD_ROOT"],
            f'data/{self.config["env"]["ROUTE_FILE"]}',
        )
        self.carla_shell = os.path.join(self.config["env"]["CARLA_ROOT"], "CarlaUE4.sh")
        self.carla_restart_gap = 10  # Restart Carla after this number of simulations

    def setup(
        self,
        params_dict,
    ):
        self.set_params_dict(params_dict)
        self._clear_data()
        self._generate_run_step()

    def set_params_dict(self, params_dict):
        self.params_dict = params_dict
        self.dim = len(params_dict)

    def set_save_data(self, save_data):
        self.save_data = save_data

    def set_debug(self, debug):
        self.debug = debug

    def set_name(self, name):
        self.name = name
        self.output_path = self.output_root_path

    # setter of random_seed
    def set_random_seed(self, random_seed):
        self.random_seed = random_seed
        np.random.seed(self.random_seed)
        random.seed(self.random_seed)

    def set_extra_info(self, extra_info):
        self.extra_info = extra_info

    def _clear_data(self):
        self.search_collector = {
            "search_id": [],
            "ttc": [],
            "loss": [],
            "time": [],
            "distance": [],
            "collision_status": [],
        }
        for key in self.params_dict.keys():
            self.search_collector[key] = []

    def _generate_run_step(self):
        params_list = list(self.params_dict.keys())

        def run_step(self, *args):
            for key, value in zip(params_list, args):
                self.search_collector[key].append(value)
            return self._simulate_carla()

        self.run_step = types.MethodType(run_step, self)

    def _run_step_warp(self, x):
        return self.run_step(*x)

    def within_bounds(self, var_name, var_value):
        if (
            var_value >= self.params_dict[var_name][0]
            and var_value <= self.params_dict[var_name][1]
        ):
            return True
        else:
            return False

    def _simulate_carla(self, attempt=1):

        search_id = str(time.time()) + "-" + str(random.randint(0, 1000))

        # If reach the max attempt, return the previous loss
        if attempt <= 5:

            search_count = len(self.search_collector["search_id"])

            if self.debug:
                print("sim_count: ", search_count)

            if search_count % self.carla_restart_gap == 0:
                self._restart_carla()
            while not self._is_carla_running():
                self._restart_carla()

            # Set params
            for key in self.params_dict.keys():
                change_route_value(
                    self.route_file, self.route_id, key, self.search_collector[key][-1]
                )

            # Start simulation
            process = subprocess.Popen(
                ["/bin/bash", self.simulate_script, self.route_id],
                stdout=subprocess.PIPE,
            )

            try:
                process.wait(timeout=300)  # 5 mins
            except:
                print(f"Simulation timed out at {datetime.now().strftime('%m%d%H%M')}")
                process.kill()
                self._restart_carla()
                print(f"Process terminated. Retrying... [No.{attempt}]")
                return self._simulate_carla(attempt=attempt + 1)  # Recursive retry
        else:
            print("Max attempt reached. Return previous loss.")
            self._kill_carla()

        # Get result
        with open("epoch_result.json", "r") as f:
            result = json.load(f)

        collision_flag = result["collision_flag"]
        min_ttc = result["min_ttc"]
        collision_status = result["collision_status"]
        distance = result["distance"]

        # Change to your own loss
        loss = min_ttc

        # Collect data
        self.search_collector["ttc"].append(min_ttc)
        self.search_collector["loss"].append(loss)
        self.search_collector["search_id"].append(search_id)
        self.search_collector["collision_status"].append(collision_status)
        self.search_collector["distance"].append(distance)

        return loss

    # Decorator of search_ methods
    def search_method_decorator(method_name):
        def decorator(func):
            @functools.wraps(func)
            def wrapper(self, *args, **kwargs):
                self.search_method = method_name
                self._clear_data()
                start_time = time.perf_counter()

                if self.debug:
                    print("Start to search by {}...".format(method_name))

                self.set_random_seed(self.random_seed)

                def terminate(start_time):
                    end_time = time.perf_counter()
                    time_usage = end_time - start_time
                    self.search_collector["time"].append(time_usage)

                    save_pickle(
                        self.output_path, "search_collector.pkl", self.search_collector
                    )

                    if self.save_data:
                        save_csv(
                            self.output_path,
                            "search_{}.csv".format(self.search_method),
                            data=self.search_collector,
                        )

                    print(
                        "Method:{},time:{:.2f}s".format(self.search_method, time_usage)
                    )
                    print(f"Restuls saved in {self.output_path}")
                    print("Please wait for the termination of the process...")

                    self._kill_carla()

                def signal_handler(sig, frame):
                    print("User interrupt the process")
                    terminate(start_time)
                    sys.exit(0)

                signal.signal(signal.SIGINT, signal_handler)

                retval = func(self, *args, **kwargs)  # Execute search algorithm

                terminate(start_time)

                return retval

            return wrapper

        return decorator

    @search_method_decorator("pso")
    def search_pso(self, n_particles=40, max_iter=50, w=0.8, c1=0.5, c2=0.5):
        # w: weight of inertia
        # c1: single memory
        # c2: collective memory
        # Particle Swarm Optimization

        x_lb = [x[0] for x in self.params_dict.values()]
        x_ub = [x[1] for x in self.params_dict.values()]
        dim = len(x_lb)
        pso = PSO(
            func=self._run_step_warp,
            dim=dim,
            pop=n_particles,
            max_iter=max_iter,
            lb=x_lb,
            ub=x_ub,
            w=w,
            c1=c1,
            c2=c2,
        )
        pso.record_mode = True
        pso.run()

        print(f"Best y: {pso.best_y}, Best x: {pso.best_x}")
        pso_result = {
            "best_y": pso.best_y,
            "best_x": pso.best_x,
            "gbest_y_hist": pso.gbest_y_hist,
            "record_value": pso.record_value,
        }
        save_pickle(self.output_path, "pso_result.pkl", pso_result)

    @search_method_decorator("replay")
    def replay(self, params_list):
        # params_list: should contain a list of parameters' list

        for this_params in params_list:
            self._run_step_warp(this_params)

    @search_method_decorator("random")
    def search_random(self, n_iter=50):
        # Random Search

        x_lb = [x[0] for x in self.params_dict.values()]
        x_ub = [x[1] for x in self.params_dict.values()]
        dim = len(x_lb)

        for i in range(n_iter):
            if self.debug:
                print("Step: {}".format(i))
            x = np.random.uniform(x_lb, x_ub, dim)
            self._run_step_warp(x)

    @search_method_decorator("ga")
    def search_ga(self, n_population=50, n_generation=50, prob_mut=0.01):
        # Genetic Algorithm

        x_lb = [x[0] for x in self.params_dict.values()]
        x_ub = [x[1] for x in self.params_dict.values()]
        dim = len(x_lb)

        ga = GA(
            func=self._run_step_warp,
            n_dim=dim,
            size_pop=n_population,
            max_iter=n_generation,
            lb=x_lb,
            ub=x_ub,
            prob_mut=prob_mut,
        )
        ga.run()

        print(f"Best y: {ga.best_y}, Best x: {ga.best_x}")
        ga_result = {
            "best_y": ga.best_y,
            "best_x": ga.best_x,
            "generation_best_Y": ga.generation_best_Y,
            "generation_best_X": ga.generation_best_X,
            "all_history_FitV": ga.all_history_FitV,
            "all_history_Y": ga.all_history_Y,
        }
        save_pickle(self.output_path, "ga_result.pkl", ga_result)

    def _kill_carla(self):
        # Run multiple times to ensure the process is killed
        # Also kill leaderboard to avoid zombie process
        subprocess.call(["pkill", "-f", "leaderboard_evaluator"])
        subprocess.call(["pkill", "-f", "leaderboard_evaluator"])
        subprocess.call(["pkill", "-f", "leaderboard_evaluator"])
        subprocess.call(["pkill", "CarlaUE4"])
        subprocess.call(["pkill", "CarlaUE4"])
        subprocess.call(["pkill", "CarlaUE4"])
        if self.agent == "interfuser":
            subprocess.call(["pkill", "-f", "interfuser"])
        if self.agent == "tfpp":
            subprocess.call(["pkill", "-f", "tfpp"])
        if self.agent == "ba":
            subprocess.call(["pkill", "-f", "simulate_ba"])
        time.sleep(10)

    def _restart_carla(self):
        self._kill_carla()
        cmds = [self.carla_shell, "-ResX=400", "-ResY=300"]
        if not self.render:
            cmds.append("-RenderOffScreen")
        env = os.environ.copy()
        # If you are using a Ubuntu server,
        # please modify the DISPLAY value according to your own server
        if "DISPLAY" not in env.keys():
            env["DISPLAY"] = ":10.0"
        self.process = subprocess.Popen(
            cmds, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, env=env
        )
        time.sleep(10)

    def _is_carla_running(self):
        return is_process_running("CarlaUE4")
