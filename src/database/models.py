from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


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
        colors = []
        for idx in range(0, len(self.color_str), 9):
            blue_str = self.color_str[idx : idx + 3]
            green_str = self.color_str[idx + 3 : idx + 6]
            red_str = self.color_str[idx + 6 : idx + 9]
            colors.append((int(blue_str), int(green_str), int(red_str)))
        return colors

    def __repr__(self) -> str:
        return f"Image(path={self.path!r}, x={self.x!r}, y={self.y!r}, density={self.density!r}, profile={self.profile!r}, colors={self.color_str!r})"
