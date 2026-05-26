"""Entry point for Instagram Analytics RAG — Layer 1."""

import sys
from pathlib import Path

from layer1.config import Config
from layer1.loader import load_csv
from layer1.processor import process_rows

DATASET_PATH = Path("data/instagram_dataset.csv")
COST_PER_CALL_USD = 0.002


def main() -> None:
    """Load config, validate data, confirm with user, then run the processor."""
    try:
        config = Config.from_env()
    except EnvironmentError as exc:
        print(f"[Config error] {exc}")
        sys.exit(1)

    try:
        rows = load_csv(DATASET_PATH)
    except (FileNotFoundError, ValueError) as exc:
        print(f"[Data error] {exc}")
        sys.exit(1)

    total = len(rows)
    estimated_cost = total * COST_PER_CALL_USD
    print(f"Loaded {total} rows. Starting Layer 1 processing...")
    print(f"Model      : {config.openai_model}")
    print(f"Output dir : {config.output_dir}/")
    print(f"Est. cost  : ${estimated_cost:.2f} ({total} rows × ${COST_PER_CALL_USD:.3f}/call)")
    print()

    answer = input("Proceed? (y/n): ").strip().lower()
    if answer != "y":
        print("Aborted.")
        sys.exit(0)

    print()
    success, errors = process_rows(rows, config)

    print()
    print("=" * 50)
    print(f"Layer 1 complete.")
    print(f"  Successful : {success}")
    print(f"  Errors     : {errors}")
    print(f"  Output dir : {config.output_dir.resolve()}/")
    if errors:
        print(f"  Error files: {config.output_dir}/*_error.json")


if __name__ == "__main__":
    main()
