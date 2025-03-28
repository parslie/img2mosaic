from platformdirs import user_data_path
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from database.models import Base


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
