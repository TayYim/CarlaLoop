script_dir=$(dirname "$(realpath "$0")")
config_file="$script_dir/../config.json"

while IFS="=" read -r key value
do
    export $key="$value"
done < <(python3 -c "import json, sys, os; \
    config=json.load(open(os.path.realpath('$config_file'))); \
    env=config.get('env', {}); \
    print('\n'.join([f'{k}={v}' for k, v in env.items()]));")

export PYTHONPATH=${HIGHWAY_SCEN_GEN_ROOT}:${PYTHONPATH}
export PYTHONPATH="${CARLA_ROOT}/PythonAPI/carla/":"${CARLA_ROOT}/PythonAPI/carla/dist/carla-0.9.15-py3.7-linux-x86_64.egg":${PYTHONPATH}
export PYTHONPATH="${SCENARIO_RUNNER_ROOT}":"${LEADERBOARD_ROOT}":${PYTHONPATH}

# Interfuser
# export INTERFUSER_ROOT="/home/tay/Workspace/LB-agents/InterFuser"
export PYTHONPATH=$PYTHONPATH:${INTERFUSER_ROOT}/leaderboard/team_code:${INTERFUSER_ROOT}/leaderboard:${INTERFUSER_ROOT}
export SAVE_PATH=${INTERFUSER_ROOT}/data/eval

# Process route id passed as argument
if [ -z "\$1" ]
then
    export ROUTES_SUBSET=1
else
    export ROUTES_SUBSET=$1
fi

export ROUTES=${LEADERBOARD_ROOT}/data/routes_carlaloop.xml
export REPETITIONS=1
export DEBUG_CHALLENGE=0
export TEAM_AGENT=${INTERFUSER_ROOT}/leaderboard/team_code/interfuser_agent.py
export TEAM_CONFIG=${INTERFUSER_ROOT}/leaderboard/team_code/interfuser_config.py
export CHECKPOINT_ENDPOINT=${LEADERBOARD_ROOT}/results.json
export CHALLENGE_TRACK_CODENAME=SENSORS

${INTERFUSER_PYTHON_PATH} ${LEADERBOARD_ROOT}/leaderboard/leaderboard_evaluator.py \
--routes=${ROUTES} \
--routes-subset=${ROUTES_SUBSET} \
--repetitions=${REPETITIONS} \
--track=${CHALLENGE_TRACK_CODENAME} \
--checkpoint=${CHECKPOINT_ENDPOINT} \
--debug-checkpoint=${DEBUG_CHECKPOINT_ENDPOINT} \
--agent=${TEAM_AGENT} \
--agent-config=${TEAM_CONFIG} \
--debug=${DEBUG_CHALLENGE} \
--record=${RECORD_PATH} \
--resume=${RESUME}