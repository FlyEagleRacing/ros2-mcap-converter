# ros2-mcap-converter

Convert ros2bag .mcap file to .json or other formats.

## Requirements

Install needed librarys

```bash
pip3 install mcap
pip3 install mcap-ros2-support
```

## If you have installed ROS2

try `ros2_version` folder will be probably better.

## Run

usage: `convert.py [-h] [--output-json-dir OUTPUT_JSON_DIR] [--export-topic string [string ...]] [--noexport-topic string [string ...]] input`

```
positional arguments:
  input                 input bag path (folder or filepath) to read from

optional arguments:
  -h, --help            show this help message and exit
  --output-json-dir OUTPUT_JSON_DIR
                        You want to convert file to json, and store in where
  --export-topic string [string ...]
                        Topic name list that you don't want to export
  --noexport-topic string [string ...]
                        Topic name list that you don't want to export
```

## Example

```bash
 python3 convert.py ./input_mcap/static_a2rl_track/static_mountpoint_1_0.mcap --export-topic /vectornav/raw/gps
```

