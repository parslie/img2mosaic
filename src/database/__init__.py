import random
from pathlib import Path

from platformdirs import user_data_path
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from database.models import Base, Image
from util import colors_to_str


class Database:
    def __init__(self):
        dir_path = user_data_path("img2mosaic", "Parslie")
        dir_path.mkdir(parents=True, exist_ok=True)
        self.path = dir_path / "database.sqlite3"
        self.engine = create_engine(f"sqlite:///{self.path}")
        self.session = Session(self.engine)
        Base.metadata.create_all(self.engine)

    def commit(self):
        self.session.commit()

    def add(self, *rows):
        for row in rows:
            self.session.add(row)

    def has_image(self, profile: str, density: int, path: Path) -> bool:
        stmt = select(Image).filter_by(profile=profile, density=density, path=str(path))
        return self.session.execute(stmt).first() is not None

    def get_random_image(
        self, profile: str, density: int, colors: list[tuple[int, int, int]]
    ) -> Image:
        color_str = colors_to_str(colors)
        stmt = select(Image).filter_by(profile=profile, density=density, color_str=color_str)
        images = self.session.scalars(stmt).all()

        if len(images) != 0:
            idx = random.randint(0, len(images) - 1)
            return images[idx]

        stmt = select(Image).filter_by(profile=profile, density=density)
        images = self.session.scalars(stmt).all()

        closest_distance = float("inf")
        closest_image_idx = 0
        for idx, image in enumerate(images):
            distance = 0.0
            for color_idx in range(len(colors)):
                color_a = colors[color_idx]
                color_b = image.colors[color_idx]
                blue_diff = color_a[0] - color_b[0]
                green_diff = color_a[1] - color_b[1]
                red_diff = color_a[2] - color_b[2]
                distance += blue_diff**2 + green_diff**2 + red_diff**2
            if distance < closest_distance:
                closest_distance = distance
                closest_image_idx = idx
            if distance == 0:
                break

        return images[closest_image_idx]
