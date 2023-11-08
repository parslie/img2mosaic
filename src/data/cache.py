import json
from os import makedirs
from platformdirs import user_data_path


class Cache:
    def __init__(self, profile: str):
        self.path = user_data_path("img2mosaic", "Parslie").joinpath(f"cache.{profile}.json")
        print(f"Cache path: {self.path}")
        
        if self.path.exists():
            with self.path.open("r") as file:
                self.data = json.loads(file.read())
        else:
            self.data = {}

    def save(self):
        makedirs(self.path.parent, exist_ok=True)
        with self.path.open("w") as file:
            file.write(json.dumps(self.data, sort_keys=True))
