from pathlib import Path
import re

def is_line_number(line):
    return re.fullmatch(r'\d+', line.strip()) is not None

def clean_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()
    with open(file_path, 'w', encoding='utf-8') as file:
        for line in lines:
            if not is_line_number(line):
                file.write(line)

def process_directory(directory_path):
    for file_path in Path(directory_path).rglob('*.rs'):
        clean_file(file_path)

process_directory('path/to/target/directory')

