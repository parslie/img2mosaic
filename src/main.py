import click

import command


@click.group()
@click.option(
    "-p", "--profile", help="Profile to store analyzed images in.", default="default", type=str
)
@click.option(
    "-d",
    "--density",
    help="Amount of pixels each axes of an analzed image represents.",
    default=1,
    type=click.IntRange(min=1),
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


@main.command()
@click.pass_context
def analyze(ctx: click.Context):
    profile: str = ctx.obj["profile"]
    density: int = ctx.obj["density"]
    command.analyze(profile, density)


if __name__ == "__main__":
    main()
