import json
from argparse import ArgumentParser

from src.lib.autobadger import Autobadger, Callback, AutobadgerCallback
from src.lib.enums import Project, Registry
from src.lib.registry import get_registry, RegisteredTestClass


def _parse_args_():
    parser = ArgumentParser()
    parser.add_argument("--project", type=Project, required=True)
    return parser.parse_args()


def main():
    args = _parse_args_()
    project = args.project
    tests: list[RegisteredTestClass] = get_registry(project, registry=Registry.TEST)
    callbacks: list[Callback] = get_registry(project, registry=Registry.CALLBACK)
    autobadger = Autobadger(project, tests, callback=AutobadgerCallback(callbacks))
    result = autobadger()
    # TODO: given config from arguments, use results to...
    #       1. Output to score.json?
    #       2. Save in a remote place?
    #       3. Other?
    with open("result.json", "w") as file:
        json.dump(result.to_dict(), file, indent=2)


if __name__ == "__main__":
    main()
