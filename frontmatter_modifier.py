import os
import yaml
import argparse
import json
from yaml.loader import SafeLoader

def process_file(file_path, add_props, modify_props, remove_props, default_props, rename_props):
    with open(file_path, 'r+', encoding='utf8') as file:
        content = file.read()
        front_matter_end = content.find('---', 3)
        
        if front_matter_end != -1:
            front_matter = yaml.load(content[:front_matter_end + 3], Loader=SafeLoader)
            if front_matter is None:
                front_matter = {}
        else:
            front_matter = {}

        updated = False

        # Add default front matter if missing
        for key, value in default_props.items():
            if key not in front_matter:
                front_matter[key] = value
                updated = True

        # Add properties
        for key, value in add_props.items():
            front_matter[key] = value
            updated = True

        # Modify properties
        for key, value in modify_props.items():
            if key in front_matter and front_matter[key] == value['old']:
                front_matter[key] = value['new']
                updated = True

        # Remove properties
        for key in remove_props:
            if key in front_matter:
                del front_matter[key]
                updated = True

        # Rename properties
        for old_key, new_key in rename_props.items():
            if old_key in front_matter:
                front_matter[new_key] = front_matter.pop(old_key)
                updated = True

        if updated:
            new_content = '---\n' + yaml.dump(front_matter) + '---' + content[front_matter_end + 3:]
            file.seek(0)
            file.write(new_content)
            file.truncate()

def main():
    parser = argparse.ArgumentParser(description="Modify markdown front matter in bulk.")
    parser.add_argument("path", help="Path to the folder or file to process")
    parser.add_argument("--add", default="{}", help="JSON string to add properties")
    parser.add_argument("--modify", default="{}", help="JSON string to modify properties (format: {'key': {'old': value, 'new': value}})")
    parser.add_argument("--remove", nargs='*', default=[], help="List of properties to remove")
    parser.add_argument("--default", default="{}", help="JSON string for default front matter")
    parser.add_argument("--rename", default="{}", help="JSON string to rename properties (format: {'old_key': 'new_key'})")
    args = parser.parse_args()

    add_props = json.loads(args.add)
    modify_props = json.loads(args.modify)
    remove_props = args.remove
    default_props = json.loads(args.default)
    rename_props = json.loads(args.rename)

    if os.path.isdir(args.path):
        for root, dirs, files in os.walk(args.path):
            for file in files:
                if file.endswith('.md'):
                    process_file(os.path.join(root, file), add_props, modify_props, remove_props, default_props, rename_props)
    elif os.path.isfile(args.path):
        process_file(args.path, add_props, modify_props, remove_props, default_props, rename_props)
    else:
        print("Invalid path provided.")

if __name__ == "__main__":
    main()
