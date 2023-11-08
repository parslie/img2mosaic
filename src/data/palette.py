import json
from os import makedirs
from platformdirs import user_data_path


class Palette:
    def __init__(self, profile: str):
        self.path = user_data_path("img2mosaic", "Parslie").joinpath(f"palette.{profile}.json")
        print(f"Palette path: {self.path}")

        if self.path.exists():
            with self.path.open("r") as file:
                self.data = json.loads(file.read())
        else:
            self.data = {}

    def save(self):
        makedirs(self.path.parent, exist_ok=True)
        with self.path.open("w") as file:
            file.write(json.dumps(self.data, sort_keys=True))

    @property
    def paths(self) -> set:
        paths = set()
        for path in self.data.values():
            paths.update(path)
        return paths
    
    def get(self, key: str, default: list) -> list:
        return self.data.get(key, default)

    def set(self, key: str, val: list):
        self.data[key] = val
