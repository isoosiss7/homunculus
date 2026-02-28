from __future__ import annotations

import argparse

from homunculus.agent import run


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="homunculus")
    subparsers = parser.add_subparsers(dest="command", required=True)

    run_parser = subparsers.add_parser("run", help="Run the agent with a purpose")
    run_parser.add_argument("purpose", help="Purpose string")

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    if args.command == "run":
        done = run(args.purpose)
        print(done.summary)
        return 0

    parser.error("Unknown command")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
