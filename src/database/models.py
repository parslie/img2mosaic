from sqlalchemy import ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class Color(Base):
    __tablename__ = "color"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    red: Mapped[int] = mapped_column()
    green: Mapped[int] = mapped_column()
    blue: Mapped[int] = mapped_column()

    image_id: Mapped[int] = mapped_column(ForeignKey("image.id"))
    image: Mapped["Image"] = relationship(back_populates="colors")

    def __repr__(self) -> str:
        return f"Color(red={self.red!r}, green={self.green!r}, blue={self.blue!r})"


class Image(Base):
    __tablename__ = "image"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    path: Mapped[str] = mapped_column()
    x: Mapped[int] = mapped_column()
    y: Mapped[int] = mapped_column()
    density: Mapped[int] = mapped_column()
    profile: Mapped[str] = mapped_column()

    colors: Mapped[list["Color"]] = relationship(back_populates="image")

    def __repr__(self) -> str:
        return f"Color(path={self.path!r}, x={self.x!r}, y={self.y!r}, density={self.density!r}, profile={self.profile!r})"
