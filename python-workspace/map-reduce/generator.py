import json
import random
from uuid import uuid4


class Generator:
    def __init__(
        self,
        output_path: str,
        n: int,
        max: int,
        min: int,
    ) -> None:
        self.n = n
        self.max = max
        self.min = min
        self.output_path = output_path

    def random_integers(self) -> list[int]:
        return [random.randint(self.min, self.max) for _ in range(self.n)]

    def generate(self) -> None:
        with open(self.output_path, "w") as file:
            json.dump(self.random_integers(), file)


import argparse


def run() -> None:
    parser = argparse.ArgumentParser(
        "Generator CLI for producing lists of integers for sorting"
    )
    parser.add_argument(
        "--output",
        "-o",
        type=str,
        default=None,
        help="Output path.  Defaults to jobs/<generated-uuid>.json",
    )
    parser.add_argument(
        "--max",
        "-M",
        type=int,
        default=1000000,
        help="The maximum integer value.  (Default=%(default)s)",
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

    args = parser.parse_args()
    path = args.output if args.output is not None else f"jobs/{uuid4()}.json"

    generator = Generator(output_path=path, n=args.length, min=args.min, max=args.max)

    print(f"Generating {generator.n} random integers at {generator.output_path}")

    generator.generate()


if __name__ == "__main__":
    run()
