import argparse
import sys


def greet(name: str) -> str:
    if not name:
        raise ValueError("Name must not be empty.")
    return f"Hello, {name}!"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="app",
        description="A simple Python CLI scaffold.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    hello = subparsers.add_parser("hello", help="Print a greeting.")
    hello.add_argument("name", help="Name to greet.")
    hello.add_argument("--loud", action="store_true", help="Shout the greeting.")

    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    if args.command == "hello":
        try:
            message = greet(args.name)
        except ValueError as e:
            print(f"Error: {e}", file=sys.stderr)
            return 1
        if args.loud:
            message = message.upper()
        print(message)
        return 0

    return 1


if __name__ == "__main__":
    sys.exit(main())
