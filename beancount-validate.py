import argparse
from pathlib import Path
import sys

from beancount.parser import parser, printer


def main():
    args = parse_args()

    ledger_file_path_str = args.file_path
    reexport_into_file = args.reexport_into_file
    ledger_file = Path(ledger_file_path_str)

    assert ledger_file.exists(), f"Provided ledger file path {ledger_file_path_str} not found"
    assert ledger_file.is_file(), f"Provided ledger file at {ledger_file_path_str} is not a file"

    suffix = ledger_file.suffix.lower()

    assert (
        suffix == ".beancount" or suffix == ".bean"
    ), f"Provided file at {ledger_file_path_str} is not a .beancount or .bean file"

    entries, errors, _ = parser.parse_string(ledger_file.read_text())

    if errors:
        printer.print_errors(errors, sys.stderr)

        print(f"Found {len(errors)} errors", file=sys.stderr)

        sys.exit(1)

    if reexport_into_file:
        with ledger_file.open(mode="w") as file:
            printer.print_entries(entries, file=file)
    else:
        printer.print_entries(entries, file=sys.stdout)

    print(f"Found {len(entries)} entries", file=sys.stderr)

def parse_args():
    parser = argparse.ArgumentParser(
        description="Parses a beancount ledger and applies validation rules to it"
    )

    parser.add_argument(
        "--file-path", "-f", required=True, help="Path to the beancount ledger file"
    )

    parser.add_argument(
        "--reexport-into-file",
        "-r",
        action="store_true",
        help="Reexports input file after parsing for convencience",
    )


    args = parser.parse_args()
    return args


if __name__ == "__main__":
    main()
