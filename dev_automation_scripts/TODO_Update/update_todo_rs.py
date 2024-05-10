import os
# formatted for rust, change endswith() and comment syntax relative to target language



directories_to_search = ['./src', './lib']

todo_file_path = './TODO.md'

existing_todos = set()
if os.path.exists(todo_file_path):
    with open(todo_file_path, 'r') as f:
        for line in f:
            if line.startswith('- [ ] '):  # This assumes a specific format in TODO.md
                existing_todos.add(line.strip())

def format_todo_line(path, line_number, todo_comment):
    return f'- [ ] {path}:{line_number}: {todo_comment}'

new_todos = []
for directory in directories_to_search:
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.rs'):  # or any other file extensions
                path = os.path.join(root, file)
                with open(path, 'r') as f:
                    lines = f.readlines()
                    for i, line in enumerate(lines):
                        if '//TODO' in line:
                            todo_line = format_todo_line(path, i + 1, line.strip())
                            if todo_line not in existing_todos:
                                new_todos.append(todo_line)

# Update TODO.md only if there are new TODOs
if new_todos:
    with open(todo_file_path, 'a') as f:  # Open in append mode
        for todo in new_todos:
            f.write(f'{todo}\n')

print(f'Added {len(new_todos)} new TODOs to {todo_file_path}')

