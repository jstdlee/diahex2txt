import sys
from typing import List, Optional

import typer

from .decoder import DiameterDecoder

app = typer.Typer(help="CLI tool to decode Diameter messages from HEX input.")


@app.command()
def decode(
    hex_input: Optional[List[str]] = typer.Argument(
        None, help="Hex string(s), e.g. '0x01...'. Reads stdin if omitted or '-'."
    )
):
    """
    Decodes one or more Diameter messages from a HEX string and prints the structure.
    """
    if not hex_input or hex_input == ["-"]:
        text = sys.stdin.read()
    else:
        text = " ".join(hex_input)
    result = DiameterDecoder().decode(text)
    print(result)
    # Errors can follow good messages in a multi-message stream, so check every line
    if any(line.startswith("Error") for line in result.splitlines()):
        raise typer.Exit(code=1)


if __name__ == "__main__":
    app()
