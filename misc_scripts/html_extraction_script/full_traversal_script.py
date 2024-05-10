from bs4 import BeautifulSoup
from pathlib import Path
import os

input_dir = Path('add path to input dir for extraction')
output_dir = Path('./target_dir/')

output_dir.mkdir(parents=True, exist_ok=True)
pattern = '<add pattern for targeting files in directory traversal>'

for sub_dir in input_dir.glob(pattern):
    if sub_dir.is_dir():
        for file_path in sub_dir.glob('*.rs.html'):
            with open(file_path, 'r', encoding='utf-8') as file:
                soup = BeautifulSoup(file, 'html.parser')

                code_blocks = soup.find_all('pre')
                rust_code = '\n\n'.join(block.get_text() for block in code_blocks)

                new_filename = file_path.name.replace('.rs.html', '.rs')
                new_file_path = output_dir / file_path.relative_to(input_dir).parent / new_filename
                
                new_file_path.parent.mkdir(parents=True, exist_ok=True)
                
                with open(new_file_path, 'w', encoding='utf-8') as new_file:
                    new_file.write(rust_code)

print("complete.")
