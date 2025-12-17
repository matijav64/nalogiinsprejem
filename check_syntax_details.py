import sys
import os

def check_syntax(file_path):
    with open(file_path,'rb') as f:
        data = f.read()
    try:
        code_str = data.decode('utf-8')
    except UnicodeDecodeError as e:
        print(f'[ERROR] {file_path}: Cannot decode as UTF-8: {e}')
        return
    try:
        compile(code_str, file_path, 'exec')
    except SyntaxError as e:
        print(f'[SYNTAX ERROR] {file_path}: {e}')
        lines = code_str.splitlines(True)
        if e.lineno is not None and 1 <= e.lineno <= len(lines):
            problem_line = lines[e.lineno - 1]
            print(f'Problematic line (line {e.lineno}):')
            print('  Raw repr:', repr(problem_line))

def main():
    start_path = os.path.abspath('.')
    print(f'Checking syntax in directory: {start_path}')
    print('=' * 60)
    for root, dirs, files in os.walk(start_path):
        for fname in files:
            if fname.lower().endswith('.py'):
                full_path = os.path.join(root, fname)
                check_syntax(full_path)
    print('=' * 60)
    print('Done checking. Any SyntaxErrors above should show the problematic line.')

if __name__ == '__main__':
    main()
