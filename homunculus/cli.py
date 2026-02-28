from __future__ import annotations

import argparse
from contextlib import contextmanager
from pathlib import Path
from urllib.parse import urlparse

from playwright.sync_api import sync_playwright

from homunculus.agent import run
from homunculus.browser_act import act_by_role_ref
from homunculus.browser_snapshot import snapshot_role_refs
from homunculus.playwright_utils import new_anonymous_context


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="homunculus")
    subparsers = parser.add_subparsers(dest="command", required=True)

    run_parser = subparsers.add_parser("run", help="Run the agent with a purpose")
    run_parser.add_argument("purpose", help="Purpose string")

    snapshot_parser = subparsers.add_parser(
        "snapshot-role-refs",
        help="Print role refs for all supported elements on a page",
    )
    snapshot_parser.add_argument(
        "target",
        help="Target URL (http/https) or local HTML file path",
    )
    snapshot_parser.add_argument(
        "--roles",
        help="Comma-separated list of ARIA roles to include",
    )

    act_parser = subparsers.add_parser(
        "act-by-role-ref",
        help="Perform an action on a role ref",
    )
    act_parser.add_argument(
        "target",
        help="Target URL (http/https) or local HTML file path",
    )
    act_parser.add_argument("role_ref", help="Role ref string to act on")
    act_parser.add_argument(
        "--action",
        choices=["click", "fill", "press"],
        required=True,
        help="Action to perform",
    )
    act_parser.add_argument(
        "--value",
        help="Value to fill when using action=fill",
    )
    act_parser.add_argument(
        "--key",
        help="Key to press when using action=press",
    )
    act_parser.add_argument(
        "--print-title",
        action="store_true",
        help="Print page title after performing the action",
    )

    return parser


def _resolve_target(target: str) -> str:
    parsed = urlparse(target)
    if parsed.scheme in {"http", "https", "file"}:
        return target
    path = Path(target).expanduser().resolve()
    return path.as_uri()


@contextmanager
def _page_for_target(target: str):
    target_url = _resolve_target(target)
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        context = new_anonymous_context(browser)
        try:
            page = context.new_page()
            page.goto(target_url, wait_until="domcontentloaded")
            yield page
        finally:
            context.close()
            browser.close()


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    if args.command == "run":
        done = run(args.purpose)
        print(done.summary)
        return 0

    if args.command == "snapshot-role-refs":
        include_roles = None
        if args.roles is not None:
            if not args.roles.strip():
                parser.error("--roles cannot be empty")
            include_roles = set()
            for entry in args.roles.split(","):
                role = entry.strip().lower()
                if not role:
                    parser.error("--roles cannot be empty")
                include_roles.add(role)
        with _page_for_target(args.target) as page:
            role_refs = snapshot_role_refs(page, include_roles=include_roles)
        for role_ref in role_refs:
            print(role_ref)
        return 0

    if args.command == "act-by-role-ref":
        if args.action == "fill" and args.value is None:
            parser.error("action 'fill' requires --value")
        if args.action == "press" and args.key is None:
            parser.error("action 'press' requires --key")
        with _page_for_target(args.target) as page:
            act_by_role_ref(page, args.role_ref, args.action, args.value, args.key)
            if args.print_title:
                print(page.title())
        return 0

    parser.error("Unknown command")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
