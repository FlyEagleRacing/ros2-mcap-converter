import argparse
import json
import re
import os
from mcap.reader import make_reader
from mcap_ros2.decoder import DecoderFactory


'''
    Bohan Ren
    bobh@zendee.cn
    2024.4.10
'''


def is_basic_type(obj):
    """
    检查对象是否是基本类型
    """
    basic_types = (int, float, str, bool, type(None))
    return isinstance(obj, basic_types)

def get_members_dict(obj, visited=None):
    """
    递归获取对象的所有成员，并以字典形式返回
    """
    if visited is None:
        visited = set()

    # 防止无限递归
    obj_id = id(obj)
    if obj_id in visited:
        return '<circular reference>'
    visited.add(obj_id)

    if is_basic_type(obj):
        return obj

    members_dict = {}
    # 获取对象的所有成员
    for attr in dir(obj):
        # 忽略特殊方法和属性
        if attr.startswith("__") and attr.endswith("__"):
            continue
        if attr == "_full_text" or attr == "_type":
            continue
        try:
            attr_value = getattr(obj, attr)
            if is_basic_type(attr_value):
                members_dict[attr] = attr_value
            else:
                # 对于复杂类型，递归调用
                members_dict[attr] = get_members_dict(attr_value, visited)
        except Exception as e:
            members_dict[attr] = f'<error accessing: {str(e)}>'
    return members_dict

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
    with open(args.input, "rb") as f:
        reader = make_reader(f, decoder_factories=[DecoderFactory()])
        for schema, channel, message, ros_msg in reader.iter_decoded_messages():
            topic = channel.topic
            if topic in topic_list_to_ignore:
                continue
            if len(topic_list_to_export) != 0 and topic not in topic_list_to_export:
                continue
            count += 1
            tmp_obj = get_members_dict(ros_msg)
            tmp_obj["__ros2_bag_timestamp"] = message.log_time
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