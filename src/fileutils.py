import pathlib
import os

def folder_exists(folder: str) -> bool:
    if pathlib.Path(folder).is_dir():
        return True

    print(f'Folder does not exists: {folder}')

    return False


def add_create_folder(fn: str, path: str) -> str:
    dir = os.path.dirname(fn)
    new_dir = os.path.join(dir, path)

    if not folder_exists(new_dir):
        os.mkdir(new_dir)

    return new_dir


def file_exists(fn: str) -> bool:
    if pathlib.Path(fn).is_file():
        return True

    print(f'File does not exists: {fn}')

    return False


def replace_file_ext(fn: str, ext: str) -> str:
    base = os.path.splitext(fn)[0]
    return f'{base}.{ext}'


def add_to_filename(fn: str, app: str) -> str:
    filename = os.path.splitext(fn)
    return f'{filename[0]}{app}{filename[1]}'


class DirContext:
    # from http://ralsina.me/weblog/posts/BB963.html
    def __init__(self, new_dir):
        self.new_dir = new_dir
        self.old_dir = None

    def __enter__(self):
        self.old_dir = os.getcwd()
        os.chdir(self.new_dir)

    def __exit__(self, *_):
        os.chdir(self.old_dir)
