from pathlib import Path

import click

import command


@click.group()
@click.option(
    "-p", "--profile", help="Profile to store analyzed images in.", default="default", type=str
)
@click.option(
    "-d",
    "--density",
    help="Amount of pixels each axes of an analyzed image represents.",
    default=1,
    type=click.IntRange(min=1),
    metavar="INTEGER",
)
@click.pass_context
def main(ctx: click.Context, profile: str, density: int):
    ctx.ensure_object(dict)
    ctx.obj["profile"] = profile
    ctx.obj["density"] = density


@main.command()
@click.pass_context
def generate(ctx: click.Context):
    profile: str = ctx.obj["profile"]
    density: int = ctx.obj["density"]
    command.generate(profile, density)


@main.command(help="Analyze the colors of images to use during generation.")
@click.argument("path", type=click.Path(exists=True, path_type=Path))
@click.option(
    "-r",
    "--recurse",
    help="Analze directories recursively.",
    type=bool,
    is_flag=True,
    default=False,
)
@click.pass_context
def analyze(ctx: click.Context, path: Path, recurse: bool):
    profile: str = ctx.obj["profile"]
    density: int = ctx.obj["density"]
    command.analyze(profile, density, path, recurse)


if __name__ == "__main__":
    main()
