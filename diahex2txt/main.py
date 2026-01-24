import typer
from .decoder import DiameterDecoder

app = typer.Typer(help="CLI tool to decode Diameter messages from HEX input.")

@app.command()
def decode(
    hex_input: str = typer.Argument(..., help="Hex encoded Diameter message string (e.g. '0x01...')")
):
    """
    Decodes a Diameter message from HEX string and prints the structure.
    """
    decoder = DiameterDecoder()
    result = decoder.decode(hex_input)
    print(result)

if __name__ == "__main__":
    app()
