import argparse
import importlib
import inspect
import os
import sys

from definitions import ROOT_DIR


def main(task_file_name: str, section: str, **task_kwargs):
    """Find a task by file name and start it with it's .start()-method"""

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

    task = classes_in_module[0](section=section, **task_kwargs)
    start_method = getattr(task, "start", None)
    if not callable(start_method):
        raise AttributeError(f"\"{task_file_name}\" found at {module_path} has "
                             f"one class but no start method, cannot start.")

    task.start()


def find_modules(ignored_files, ignored_dirs):
    """Find all python modules in the repository"""

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
    """Finds all classes declared in a module, aka a .py-file"""
    classes = []

    for _, obj in inspect.getmembers(module):

        # If the obj is not a class, or if it is abstract, skip it
        if not inspect.isclass(obj) or inspect.isabstract(obj):
            continue

        # At this point, we know obj is a non-abstract class. But we do not know
        # if it is from the module we are inspecting, or if it is imported.
        # obj.__module__ is the name of the file in which obj is declared, and
        # module.__name__ is the name of the file we are inspecting (they are
        # both.written.like.this). If these are not the same, it means the obj
        # we are currently looking at is declared in another file, so it is
        # imported. Therefore, we skip it.
        if obj.__module__ != module.__name__:
            continue

        # Any remaining objects are classes declared in the module we are
        # inspecting, and shall be returned.
        classes.append(obj)

    return classes


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--task", dest="task_file_name", required=True
    )
    parser.add_argument(
        "--sec", "--section", dest="section", default="DEFAULT"
    )
    known_kwargs_namespace, unknown_kwargs_list = parser.parse_known_args()

    known_kwargs = vars(known_kwargs_namespace)
    unknown_kwargs = parse_unknown_kwargs(unknown_kwargs_list)

    return known_kwargs, unknown_kwargs


def parse_unknown_kwargs(unknown_kwargs_list):
    unknown_kwargs = {}
    for kwarg_string in unknown_kwargs_list:
        arg, val = kwarg_string.lstrip("-").split("=")
        unknown_kwargs[arg] = val

    return unknown_kwargs


if __name__ == "__main__":
    launch_task_kwargs, task_specific_kwargs = parse_args()
    main(**launch_task_kwargs, **task_specific_kwargs)
