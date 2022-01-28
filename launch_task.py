import argparse
import importlib
import inspect
import os
import sys

from definitions import ROOT_DIR


def main(task_file_name: str):
    ignored_files = ["__init__.py"]
    ignored_dirs = ["venv", ".git"]
    all_modules = find_modules(
        ignored_files=ignored_files,
        ignored_dirs=ignored_dirs,
    )

    if task_file_name not in all_modules.keys():
        module_list = ""
        for module_name, module_path in all_modules.items():
            module_list += f"{module_name}: {module_path}\n"

        raise AttributeError(f"Did not find file \"{task_file_name}\"\n"
                             f"Ignored these files: {ignored_files}\n"
                             f"Ignored these dirs: {ignored_dirs}\n"
                             f"The following files available:\n"
                             f"{module_list}")

    sys.path.append(ROOT_DIR)
    module_path = all_modules[task_file_name]
    module = importlib.import_module(module_path)

    classes_in_module = get_classes_in_module(module)

    if len(classes_in_module) == 0:
        raise AttributeError(f"\"{task_file_name}\" found at {module_path} "
                             f"but has no classes, cannot start.")

    if len(classes_in_module) > 1:
        raise AttributeError(f"\"{task_file_name}\" found at {module_path} "
                             f"but has more than one class, cannot start.")

    task = classes_in_module[0]()
    start_method = getattr(task, "start", None)
    if not callable(start_method):
        raise AttributeError(f"\"{task_file_name}\" found at {module_path} has "
                             f"one class but no start method, cannot start.")

    task.start()


def find_modules(ignored_files, ignored_dirs):
    modules_found = {}
    for root, _, files in os.walk(ROOT_DIR):

        # root/path/project/path
        relative_path = root[len(ROOT_DIR)+1:]
        # project/path
        if any(ignored_dir in relative_path for ignored_dir in ignored_dirs):
            continue

        for file in files:
            if not file.endswith(".py"):
                continue
            if file in ignored_files:
                continue

            # file.py
            file = file[:-3]
            # file

            file_path = os.path.join(relative_path, file)
            # project/path/file

            if file in modules_found.keys():
                print(f"Found duplicate file names for {file}")
                print(f"    {file_path}")
                print(f"    {modules_found[file].replace('.', '/')}")

            import_format = file_path.replace("/", ".")
            # project.path.file

            modules_found[file] = import_format

    return modules_found


def get_classes_in_module(module):
    classes = []
    for _, obj in inspect.getmembers(module):
        if not inspect.isclass(obj) or inspect.isabstract(obj):
            continue
        if obj.__module__ != module.__name__:
            continue
        classes.append(obj)

    return classes


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--task", dest="task_file_name")
    parsed_kwargs = vars(parser.parse_args())
    return parsed_kwargs


if __name__ == "__main__":
    kwargs = parse_args()
    main(**kwargs)
