import argparse
import json
import random
from pathlib import Path
from signal import SIGINT, SIGTERM, signal
from threading import Event
from uuid import uuid4


class Generator:
    def __init__(
        self,
        output_path: str | Path,
        n: int,
        max_val: int,
        min_val: int,
    ) -> None:
        self.n = n
        self.max = max_val
        self.min = min_val
        self.output_path = Path(output_path)

    def random_integers(self) -> list[int]:
        return [random.randint(self.min, self.max) for _ in range(self.n)]

    def generate(self) -> None:
        # Ensure the target directory exists
        self.output_path.parent.mkdir(parents=True, exist_ok=True)

        # Staging file path (e.g., 'jobs/uuid.json.tmp')
        tmp_path = self.output_path.with_suffix(self.output_path.suffix + ".tmp")

        try:
            with open(tmp_path, "w") as file:
                json.dump(self.random_integers(), file)

            # Atomic move makes it visible to the reader cleanly
            tmp_path.replace(self.output_path)
        except Exception:
            tmp_path.unlink(missing_ok=True)
            raise


def run() -> None:
    parser = argparse.ArgumentParser(
        description="Generator CLI for producing lists of integers for sorting"
    )
    parser.add_argument(
        "--output",
        "-o",
        type=str,
        default=None,
        help="Output path or directory. Defaults to jobs/<generated-uuid>.json",
    )
    parser.add_argument(
        "--max",
        "-M",
        type=int,
        default=1000000,
        help="The maximum integer value. (Default=%(default)s)",
    )
    parser.add_argument(
        "--min",
        "-m",
        type=int,
        default=-1000000,
        help="The minimum integer value. (Default=%(default)s)",
    )
    parser.add_argument(
        "--length",
        "-n",
        type=int,
        default=1000000,
        help="The number of values to generate. (Default=%(default)s)",
    )
    parser.add_argument(
        "--daemon",
        "-d",
        action="store_true",
        help="Run as a daemon loop, dropping a new file periodically.",
    )
    parser.add_argument(
        "--interval",
        "-i",
        type=int,
        default=30,
        help="Interval in seconds between generation loops when running as a daemon. (Default=%(default)s)",
    )

    args = parser.parse_args()

    # Determine base directory (defaulting to 'jobs')
    if args.output is not None:
        provided_path = Path(args.output)
        # If user passed a directory name, we use it as base. Otherwise extract parent.
        base_dir = provided_path if provided_path.suffix == "" else provided_path.parent
    else:
        base_dir = Path("jobs")

    # Create the shutdown_event
    shutdown_event: Event = Event()

    def sig_handler(signal, frame):
        print("Generator commencing graceful shutdown...")
        shutdown_event.set()

    signal(SIGINT, sig_handler)
    signal(SIGTERM, sig_handler)

    while not shutdown_event.is_set():
        # Unique ID generation for every file iteration
        file_name = f"{uuid4()}.json"
        current_output_path = base_dir / file_name

        generator = Generator(
            output_path=current_output_path,
            n=args.length,
            min_val=args.min,
            max_val=args.max,
        )

        print(f"Generating {generator.n} random integers at {generator.output_path}")
        generator.generate()

        if not args.daemon or shutdown_event.is_set():
            break
        else:
            print(f"Sleeping for {args.interval} seconds before next drop...")
            shutdown_event.wait(args.interval)


if __name__ == "__main__":
    run()
