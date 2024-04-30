Firstly source your workspace env:

source ~/BIT/new_track_sim/tii-bvs-dist/install/setup.bash

Then start to convert the rosbag:

python3 convert.py ./rosbag/rosbag2_2024_03_21-17_04_18_0.mcap --output-json-dir json_output1

You can specify which topic you want to export by "--export-topic"

python3 convert.py ./rosbag/rosbag2_2024_03_21-17_04_18_0.mcap --export-topic /a2rl/observer/ego_state /a2rl/eav24_bsu/hl_msg_03

Or you can ignore specific topic by "--noexport-topic"

python3 convert.py ./rosbag/rosbag2_2024_03_21-17_04_18_0.mcap --noexport-topic /a2rl/observer/ego_state
