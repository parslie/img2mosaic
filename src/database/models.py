from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from util import str_to_colors


class Base(DeclarativeBase):
    pass


class Image(Base):
    __tablename__ = "image"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    path: Mapped[str] = mapped_column()
    x: Mapped[int] = mapped_column()
    y: Mapped[int] = mapped_column()
    density: Mapped[int] = mapped_column()
    profile: Mapped[str] = mapped_column()
    color_str: Mapped[str] = mapped_column()

    @property
    def colors(self) -> list[tuple[int, int, int]]:
        return str_to_colors(self.color_str)

    def __repr__(self) -> str:
        return f"Image(path={self.path!r}, x={self.x!r}, y={self.y!r}, density={self.density!r}, profile={self.profile!r}, colors={self.color_str!r})"
