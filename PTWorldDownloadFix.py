import json
import zipfile
from pathlib import Path

import click


@click.command()
@click.argument(
    "file",
    type=click.Path(exists=True, dir_okay=False, path_type=Path),
    help="The file you downloaded from Polytoria",
)
@click.argument(
    "output",
    type=click.Path(file_okay=False, writable=True, path_type=Path),
    help="Where the exported folder should be placed",
)
def main(file: Path, output: Path):
    """Cause Polytoria wouldn't fix it themselves :("""
    if file.suffix != ".poly":
        click.secho(
            "Are you sure you selected the correct .poly file you got?",
            fg="red",
        )
        return

    if output.exists() and next(output.iterdir()) != None:
        prompt_result = click.prompt(
            "The output folder is not empty. Proceed anyways?",
            type=bool,
            default=False,
            show_default=False,
        )

        if not prompt_result:
            click.secho("Conversion cancelled.", fg="magenta")
            return

    try:
        with zipfile.ZipFile(file, "r") as zip:
            zip.extractall(output)
    except zipfile.BadZipFile:
        click.secho("Is your file corrupted? Not possible to unzip.", fg="red")
        return

    click.echo(f"Unzipped {file.name}")

    search = output.rglob("meta.json")
    if not search:
        click.secho("Could not find the meta.json file.", fg="red")
        return
    search = next(search)
    search.rename(search.with_name("project.ptproj"))

    click.echo("Renamed meta.json -> project.ptproj")

    references = output.rglob("index.json")
    if not references:
        click.secho("index.json wasn't present...", fg="red")
        return

    click.echo("Found index.json, file references will be fixed next.")

    references = next(references)
    with references.open() as ref:
        script_references = json.load(ref)

    with click.progressbar(
        script_references.items(), label="Writing .luau.meta files..."
    ) as bar:
        for id, location in bar:
            if location == "main.poly":
                continue
            output.joinpath(location).with_suffix(".luau.meta").write_text(
                json.dumps({"id": id})
            )

    references.unlink()

    click.secho("The fix has finished!", fg="green")


if __name__ == "__main__":
    main()
