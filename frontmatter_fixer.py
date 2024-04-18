import os
import yaml
import argparse
import logging
from yaml.loader import SafeLoader

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def is_property_line(line):
    """Check if a line is a valid YAML property line."""
    return ':' in line or line.strip().startswith('-') or line.strip() == ''

def fix_frontmatter(file_path, modified_files):
    with open(file_path, 'r+', encoding='utf8') as file:
        lines = file.readlines()
        in_frontmatter = False
        frontmatter = []
        body = []
        misplaced_lines = []
        modified = False
        first_dash = False

        # Process lines to categorize them properly
        for line in lines:
            if line.strip() == '---':
                if not first_dash:
                    in_frontmatter = True
                    first_dash = True
                    frontmatter.append('---\n')
                elif in_frontmatter:
                    in_frontmatter = False
                    frontmatter.append('---\n')
            elif in_frontmatter:
                if is_property_line(line):
                    frontmatter.append(line)
                else:
                    misplaced_lines.append(line)
                    modified = True
            else:
                body.append(line)

        if misplaced_lines:
            body = ['\n', '```', *misplaced_lines, '```', '\n'] + body
            modified = True

        # Rewrite the file if necessary
        if modified:
            file.seek(0)
            file.writelines(frontmatter + body)
            file.truncate()
            modified_files.append(file_path)
            logging.info(f"Modified {file_path}")

def main():
    parser = argparse.ArgumentParser(description="Fix Markdown front matter issues.")
    parser.add_argument("path", help="Path to the folder or file to process")
    args = parser.parse_args()

    modified_files = []

    if os.path.isdir(args.path):
        for root, dirs, files in os.walk(args.path):
            for file in files:
                if file.endswith('.md'):
                    fix_frontmatter(os.path.join(root, file), modified_files)
    elif os.path.isfile(args.path):
        fix_frontmatter(args.path, modified_files)
    else:
        logging.error("Invalid path provided")
        return

    # Output the list of modified files
    with open("modified_files.txt", "w") as f:
        for file in modified_files:
            f.write(f"{file}\n")

    if modified_files:
        logging.info(f"Total modified files: {len(modified_files)}")
    else:
        logging.info("No files were modified.")

if __name__ == "__main__":
    main()
