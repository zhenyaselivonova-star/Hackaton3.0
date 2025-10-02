import os
import re


def fix_imports_in_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Заменяем все from app. на from app.
    new_content = re.sub(r'from myapp\.', 'from app.', content)
    # Заменяем все import app. на import app.
    new_content = re.sub(r'import myapp\.', 'import app.', new_content)

    if new_content != content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"Fixed: {file_path}")


def scan_and_fix():
    for root, dirs, files in os.walk('.'):
        # Пропускаем venv
        if '.venv' in root or '__pycache__' in root:
            continue

        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                fix_imports_in_file(file_path)


if __name__ == '__main__':
    scan_and_fix()
    print("All imports fixed!")