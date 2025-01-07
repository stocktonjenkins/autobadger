import json
from argparse import ArgumentParser

import toml

from lib.autobadger import Autobadger, Callback, AutobadgerCallback
from lib.enums import Project, Registry, StdOut
from lib.registry import get_registry, RegisteredTestClass


def _parse_args_():
    parser = ArgumentParser()
    parser.add_argument("--project", type=Project)
    parser.add_argument("--info", action="store_true")
    parser.add_argument("--stdout", type=StdOut, default=StdOut.PRINT)
    return parser.parse_args()


def print_cli_info_and_usage():
    pyproject = toml.load("pyproject.toml")
    version = pyproject["project"]["version"]
    print("Welcome to Autobadger!")
    print(f"Current Version: {version}")
    print(
        "Usage: autobadger [--project PROJECT (p1-p8)] [--stdout STDOUT (print|json)]"
    )


def main():
    args = _parse_args_()
    project = args.project
    info = args.info
    stdout = args.stdout
    if not info and not project:
        raise ValueError('Project not specified. Pass --project="..." to CLI.')
    if info:
        print_cli_info_and_usage()
        return
    tests: list[RegisteredTestClass] = get_registry(project, registry=Registry.TEST)
    callbacks: list[Callback] = get_registry(project, registry=Registry.CALLBACK)
    autobadger = Autobadger(project, tests, callback=AutobadgerCallback(callbacks))
    result = autobadger()
    # TODO: given config from arguments, use results to...
    #       1. Output to score.json?
    #       2. Save in a remote place?
    #       3. Other?
    if stdout == StdOut.PRINT:
        print(json.dumps(result.to_dict(), indent=2))
    else:
        with open("score.json", "w") as file:
            json.dump(result.to_dict(), file, indent=2)
            print("Saved results to score.json")


if __name__ == "__main__":
    main()
