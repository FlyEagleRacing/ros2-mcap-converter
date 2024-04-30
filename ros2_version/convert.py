import argparse
from rclpy.serialization import deserialize_message
from rosidl_runtime_py.utilities import get_message
from std_msgs.msg import String
import rosbag2_py
import json
import re
import os

'''
    Bohan Ren
    bobh@zendee.cn
    2024.4.22
'''

def read_messages(input_bag: str):
    reader = rosbag2_py.SequentialReader()
    reader.open(
        rosbag2_py.StorageOptions(uri=input_bag, storage_id="mcap"),
        rosbag2_py.ConverterOptions(
            input_serialization_format="cdr", output_serialization_format="cdr"
        ),
    )

    topic_types = reader.get_all_topics_and_types()

    def typename(topic_name):
        for topic_type in topic_types:
            if topic_type.name == topic_name:
                return topic_type.type
        raise ValueError(f"topic {topic_name} not in bag")

    while reader.has_next():
        topic, data, timestamp = reader.read_next()
        msg_type = get_message(typename(topic))
        msg = deserialize_message(data, msg_type)
        yield topic, msg, timestamp
    del reader

def obj_to_dict(obj):
    if isinstance(obj, (str, int, float, bool, type(None))):
        return obj
    elif isinstance(obj, dict):
        return {k: obj_to_dict(v) for k, v in obj.items()}
    elif hasattr(obj, "__dict__"):
        return {k: obj_to_dict(v) for k, v in obj.__dict__.items() if not k.startswith('__')}
    elif isinstance(obj, list):
        return [obj_to_dict(item) for item in obj]
    elif hasattr(obj, "get_fields_and_field_types"):  # 特别处理ROS消息对象
        fields = obj.get_fields_and_field_types()
        return {field: obj_to_dict(getattr(obj, field)) for field in fields}
    else:
        return str(obj)

def to_valid_filename(s):
    # Replace characters not allowed in Ubuntu file names
    s = re.sub(r'[\/:*?"<>|]', '_', s)
    return s

def main():
    count = 0
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "input", help="input bag path (folder or filepath) to read from"
    )
    parser.add_argument(
        "--output-json-dir", default="./json_output", help="You want to convert file to json, and store in where"
    )
    parser.add_argument(
        "--export-topic", metavar="string", nargs="+", default=[], help="Topic name list that you don't want to export"
    )
    parser.add_argument(
        "--noexport-topic", metavar="string", nargs="+", default=[], help="Topic name list that you don't want to export"
    )

    output_json = {}
    count_map = {}
    args = parser.parse_args()

    topic_list_to_export = args.export_topic
    topic_list_to_ignore = args.noexport_topic

    if not os.path.exists(args.output_json_dir):
        os.makedirs(args.output_json_dir)
        print(f"Directory '{args.output_json_dir}' created successfully.")

    for topic, msg, timestamp in read_messages(args.input):
        if topic in topic_list_to_ignore:
            continue
        if len(topic_list_to_export) != 0 and topic not in topic_list_to_export:
            continue
        count += 1
        tmp_obj = obj_to_dict(msg)
        tmp_obj["__ros2_bag_timestamp"] = timestamp
        if topic in output_json:
            output_json[topic].append(tmp_obj)
        else:
            output_json[topic] = []
            output_json[topic].append(tmp_obj)

    _, filename = os.path.split(args.input)
    filename = os.path.splitext(filename)[0]

    for key in output_json:
        with open(f"{str(args.output_json_dir)}/{filename}.{to_valid_filename(key)}.json", "w") as file:
            file.write(json.dumps(output_json[key]))
            count_map[key] = len(output_json[key])

    for key in count_map:
        print(f"> [{key}]: {count_map[key]} msgs.")

    print(f"finished, total {count} msgs")
if __name__ == "__main__":
    main()