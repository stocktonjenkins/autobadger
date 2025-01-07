import json
import toml


if __name__ == "__main__":
    with open("pyproject.toml", "r") as f:
        pyproject = toml.load(f)

    version = pyproject["project"]["version"]

    fp = "./scripts/version.json"
    with open(fp, "w") as version_file:
        json.dump({"version": version}, version_file)
