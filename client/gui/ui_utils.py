import logging
import subprocess
import os

from client.utils import PATH


def compile_ui():
    for i in os.scandir(PATH.UI):
        i: os.DirEntry
        if i.name.lower().endswith('.ui'):
            proc = subprocess.run(['pyside6-uic', i.path], capture_output=True, check=True)
            path, _ = os.path.splitext(i.path)
            class_name = os.path.basename(path)
            logging.getLogger('meta').info(f'Compiling ui class {class_name}')
            with open(PATH.get(''.join((class_name, '.py')), mode='UI'), mode='wb') as f:
                f.write(proc.stdout)


if __name__ == '__main__':
    compile_ui()
