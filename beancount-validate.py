import argparse
from pathlib import Path
import sys

from rich.progress import Progress, TextColumn
from rich.console import Console

from beancount.parser import parser, printer

from beancount.ops.validation import (
    BASIC_VALIDATIONS,
    HARDCORE_VALIDATIONS,
    ValidationError,
)


def main():
    args = parse_args()

    ledger_file_path_str = args.file_path
    ledger_file = Path(ledger_file_path_str)

    assert (
        ledger_file.exists()
    ), f"Provided ledger file path {ledger_file_path_str} not found"
    assert (
        ledger_file.is_file()
    ), f"Provided ledger file at {ledger_file_path_str} is not a file"

    suffix = ledger_file.suffix.lower()

    assert (
        suffix == ".beancount" or suffix == ".bean"
    ), f"Provided file at {ledger_file_path_str} is not a .beancount or .bean file"

    entries, errors, options_map = parser.parse_string(ledger_file.read_text())

    if errors:
        printer.print_errors(errors, sys.stderr)

        print(f"Found {len(errors)} errors during initial parsing", file=sys.stderr)

        sys.exit(1)

    validations = []
    validations.extend(BASIC_VALIDATIONS)
    validations.extend(HARDCORE_VALIDATIONS)

    progress_columns = list(Progress.get_default_columns())
    succeededOfTotal = TextColumn("Errors: {task.fields[errors]}")
    progress_columns.insert(1, succeededOfTotal)

    validations_errors = []

    with Progress(*progress_columns, console=Console(file=sys.stderr)) as progress:
        for validation_function, task in [
            (f, progress.add_task(f"{f.__name__}", total=1, errors=str(0)))
            for f in validations
        ]:
            new_errors = validation_function(entries, options_map)
            validations_errors.extend(new_errors)
            progress.update(task, advance=1, errors=str(len(new_errors)))

    errors.extend(validations_errors)

    if errors:
        printer.print_errors(errors, sys.stderr)

        print(f"Found {len(errors)} errors", file=sys.stderr)

        sys.exit(1)

    printer.print_entries(entries, file=sys.stdout)

    print(f"No errors. Found {len(entries)} entries", file=sys.stderr)


def parse_args():
    parser = argparse.ArgumentParser(
        description="Parses a beancount ledger and applies validation rules to it"
    )

    parser.add_argument(
        "--file-path", "-f", required=True, help="Path to the beancount ledger file"
    )

    args = parser.parse_args()
    return args


if __name__ == "__main__":
    main()
