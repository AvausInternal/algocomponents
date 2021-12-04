import importlib
import inspect
import os
import sys

import definitions


def main():
    if len(sys.argv) < 2:
        print("Missing file name of task to start")
        return
    task_file_name = sys.argv[1]

    all_modules = find_modules(
        ignored_files=["__init__.py"],
        ignored_dirs=["venv", ".git"],
    )

    if task_file_name not in all_modules.keys():
        print(f"Did not find file \"{task_file_name}\"")
        print("Following files available:")

        for module_name, module_path in all_modules.items():
            print(f"{module_name}: {module_path}")
        return

    sys.path.append(definitions.ROOT_DIR)
    module_path = all_modules[task_file_name]
    module = importlib.import_module(module_path)

    classes_in_module = get_classes_in_module(module)

    if len(classes_in_module) == 0:
        print(f"\"{task_file_name}\" found at {module_path} "
              f"but has no classes, cannot start.")
        return

    if len(classes_in_module) > 1:
        print(f"\"{task_file_name}\" found at {module_path} "
              f"but has more than one class, cannot start.")
        return

    task = classes_in_module[0]()

    start_method = getattr(task, "start", None)
    if not callable(start_method):
        print(f"\"{task_file_name}\" found at {module_path} "
              f"has only one method but has no start method, cannot start.")
        return

    task.start()


def find_modules(ignored_files, ignored_dirs):
    modules_found = {}
    for root, dirs, files in os.walk(definitions.ROOT_DIR):
        if any(ignored_dir in root for ignored_dir in ignored_dirs):
            continue
        for file in files:
            if file in ignored_files:
                continue
            if not file.endswith(".py"):
                continue

            # file.py
            file = file[:-3]
            # file

            if file in modules_found.keys():
                print("Found duplicate file names")

            full_path = os.path.join(root, file)
            # /root/path/project/path/file

            project_path = full_path[len(definitions.ROOT_DIR)+1:]
            # project/path/file

            import_format = project_path.replace("/", ".")
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


if __name__ == "__main__":
    main()
