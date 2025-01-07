import json
import toml


if __name__ == "__main__":
    # Load pyproject.toml
    with open("pyproject.toml", "r") as f:
        pyproject = toml.load(f)

    # Extract the version from the [tool.poetry] section or the appropriate section
    version = (
        pyproject["project"]["version"]
    )

    # Save the extracted version to VERSION.txt
    with open("./version.json", "w") as version_file:
        json.dump({"version": version}, version_file)
