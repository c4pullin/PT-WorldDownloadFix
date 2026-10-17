import zipfile
from pathlib import Path

import click
import msgspec


def show_extracting(file: zipfile.ZipInfo | None) -> str | None:
    return file.filename if file else None


def show_adding_meta(location: Path | None) -> str | None:
    return location.name if location else None


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
def main(file: Path, output: Path) -> None:
    """Cause Polytoria wouldn't fix it themselves :("""
    if file.suffix != ".poly":
        click.secho(
            "Are you sure you selected the correct .poly file you got?",
            fg="red",
        )
        return

    if output.exists() and next(output.iterdir(), None) != None:
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
            zip_infos = zip.infolist()
            total_size = sum(z.file_size for z in zip_infos)
            with click.progressbar(
                length=total_size,
                label=f"Unzipping {file.name}",
                item_show_func=show_extracting,
            ) as bar:
                for info in zip_infos:
                    _ = zip.extract(info, output)
                    bar.update(info.file_size, info)
    except zipfile.BadZipFile:
        click.secho("Is your file corrupted? Not possible to unzip!", fg="red")
        return
    else:
        click.echo(f"Unzipped {file.name}")

    search = next(output.rglob("meta.json"), None)
    if not search:
        click.secho("Could not find the meta.json file!", fg="red")
        return
    _ = search.rename(search.with_name("project.ptproj"))

    click.echo("Renamed meta.json -> project.ptproj")

    references = next(output.rglob("index.json"), None)
    if not references:
        click.secho("index.json wasn't present!", fg="red")
        return

    click.echo("Found index.json, file references will be fixed next.")

    try:
        script_references = msgspec.json.decode(
            references.read_bytes(), type=dict[str, str]
        )
    except msgspec.DecodeError as e:
        click.secho(
            f"index.json didn't have the expected format!\n{e}", fg="red"
        )
        return

    if not script_references.pop("world_main.poly", None):
        click.secho("Didn't find world_main.poly in index.json!", fg="red")
        return

    encoder = msgspec.json.Encoder()
    with click.progressbar(
        length=len(script_references),
        label="Writing .luau.meta files...",
        item_show_func=show_adding_meta,
    ) as bar:
        for id, location in script_references.items():
            meta_file = output.joinpath(location).with_suffix(".luau.meta")
            _ = meta_file.write_bytes(encoder.encode({"id": id}))
            bar.update(1, meta_file)

    references.unlink()

    click.secho(
        "Your .poly file was (hopefully) converted succesfully.", fg="green"
    )


if __name__ == "__main__":
    main()
