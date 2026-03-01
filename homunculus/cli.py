from __future__ import annotations

import argparse
import json
import sys
from contextlib import contextmanager
from pathlib import Path
from urllib.parse import urlparse

from playwright.sync_api import sync_playwright

from homunculus.agent import run
from homunculus.browser_act import act_by_role_ref
from homunculus.browser_snapshot import snapshot_role_refs
from homunculus.playwright_utils import new_anonymous_context
from homunculus.role_ref import RoleRef
from homunculus.role_snapshot import snapshot_role_snapshot
from homunculus.snapshot_act import (
    snapshot_then_act_by_role_ref,
    snapshot_then_extract_text_by_role_ref,
)


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
    snapshot_parser.add_argument(
        "--json",
        action="store_true",
        help="Print role refs as a JSON array (sorted for stable output)",
    )

    role_snapshot_parser = subparsers.add_parser(
        "snapshot-role-snapshot",
        help="Print a stable element snapshot with compact refs",
    )
    role_snapshot_parser.add_argument(
        "target",
        help="Target URL (http/https) or local HTML file path",
    )
    role_snapshot_parser.add_argument(
        "--roles",
        help="Comma-separated list of ARIA roles to include",
    )
    role_snapshot_parser.add_argument(
        "--json",
        action="store_true",
        help="Print the snapshot as JSON",
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
        choices=["click", "fill", "type", "press", "hover", "wait"],
        required=True,
        help="Action to perform",
    )
    act_parser.add_argument(
        "--value",
        help="Value to fill when using action=fill or action=type",
    )
    act_parser.add_argument(
        "--key",
        help="Key to press when using action=press",
    )
    act_parser.add_argument(
        "--slowly",
        action="store_true",
        help="Type with a delay when using action=type",
    )
    act_parser.add_argument(
        "--print-title",
        action="store_true",
        help="Print page title after performing the action",
    )
    act_parser.add_argument(
        "--timeout-ms",
        type=int,
        help="Action timeout in milliseconds",
    )
    act_parser.add_argument(
        "--state",
        help="Target wait state when using action=wait",
    )

    snapshot_act_parser = subparsers.add_parser(
        "snapshot-act",
        help="Validate a role ref exists and perform an action on it",
    )
    snapshot_act_parser.add_argument(
        "target",
        help="Target URL (http/https) or local HTML file path",
    )
    snapshot_act_parser.add_argument("role_ref", help="Role ref string to act on")
    snapshot_act_parser.add_argument(
        "--action",
        choices=["click", "fill", "type", "press", "hover", "wait"],
        required=True,
        help="Action to perform",
    )
    snapshot_act_parser.add_argument(
        "--value",
        help="Value to fill when using action=fill or action=type",
    )
    snapshot_act_parser.add_argument(
        "--key",
        help="Key to press when using action=press",
    )
    snapshot_act_parser.add_argument(
        "--slowly",
        action="store_true",
        help="Type with a delay when using action=type",
    )
    snapshot_act_parser.add_argument(
        "--print-title",
        action="store_true",
        help="Print page title after performing the action",
    )
    snapshot_act_parser.add_argument(
        "--timeout-ms",
        type=int,
        help="Action timeout in milliseconds",
    )
    snapshot_act_parser.add_argument(
        "--state",
        help="Target wait state when using action=wait",
    )

    snapshot_extract_parser = subparsers.add_parser(
        "snapshot-extract-text",
        help="Validate a role ref exists and extract its visible text",
    )
    snapshot_extract_parser.add_argument(
        "target",
        help="Target URL (http/https) or local HTML file path",
    )
    snapshot_extract_parser.add_argument("role_ref", help="Role ref string to extract")
    snapshot_extract_parser.add_argument(
        "--include-role",
        action="append",
        help="ARIA role to include in snapshot validation (repeatable)",
    )
    snapshot_extract_parser.add_argument(
        "--timeout-ms",
        type=int,
        help="Wait timeout in milliseconds",
    )
    snapshot_extract_parser.add_argument(
        "--state",
        help="Target wait state when extracting",
    )
    snapshot_extract_parser.add_argument(
        "--json",
        action="store_true",
        help="Print extracted text as JSON",
    )

    act_role_parser = subparsers.add_parser(
        "act",
        aliases=["act-by-role"],
        help="Perform an action on a role/name selector",
    )
    act_role_parser.add_argument(
        "target",
        help="Target URL (http/https) or local HTML file path",
    )
    act_role_parser.add_argument(
        "--role",
        required=True,
        help="ARIA role of the target element",
    )
    act_role_parser.add_argument(
        "--name",
        required=True,
        help="Accessible name of the target element",
    )
    act_role_parser.add_argument(
        "--nth",
        type=int,
        default=0,
        help="Zero-based index when multiple elements match (default: 0)",
    )
    act_role_parser.add_argument(
        "--action",
        choices=["click", "fill", "type", "press", "hover", "wait"],
        required=True,
        help="Action to perform",
    )
    act_role_parser.add_argument(
        "--value",
        help="Value to fill when using action=fill or action=type",
    )
    act_role_parser.add_argument(
        "--key",
        help="Key to press when using action=press",
    )
    act_role_parser.add_argument(
        "--slowly",
        action="store_true",
        help="Type with a delay when using action=type",
    )
    act_role_parser.add_argument(
        "--print-title",
        action="store_true",
        help="Print page title after performing the action",
    )
    act_role_parser.add_argument(
        "--timeout-ms",
        type=int,
        help="Action timeout in milliseconds",
    )
    act_role_parser.add_argument(
        "--state",
        help="Target wait state when using action=wait",
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
        if args.json:
            print(json.dumps(sorted(role_refs)))
        else:
            for role_ref in role_refs:
                print(role_ref)
        return 0

    if args.command == "snapshot-role-snapshot":
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
            snapshot = snapshot_role_snapshot(page, include_roles=include_roles)
        if args.json:
            print(json.dumps(snapshot.to_dict(), sort_keys=True))
        else:
            print(f"url: {snapshot.url}")
            print(f"title: {snapshot.title}")
            print(f"count: {snapshot.stats['count']}")
            for item in snapshot.items:
                print(f"{item.ref}\t{item.role_ref}")
        return 0

    if args.command == "act-by-role-ref":
        if args.action == "fill" and args.value is None:
            parser.error("action 'fill' requires --value")
        if args.action == "type" and args.value is None:
            parser.error("action 'type' requires --value")
        if args.action == "press" and args.key is None:
            parser.error("action 'press' requires --key")
        if args.state is not None and args.action != "wait":
            parser.error("--state can only be used with action 'wait'")
        if args.slowly and args.action != "type":
            parser.error("--slowly can only be used with action 'type'")
        with _page_for_target(args.target) as page:
            act_by_role_ref(
                page,
                args.role_ref,
                args.action,
                args.value,
                args.key,
                args.timeout_ms,
                args.state,
                args.slowly,
            )
            if args.print_title:
                print(page.title())
        return 0

    if args.command == "snapshot-act":
        if args.action == "fill" and args.value is None:
            parser.error("action 'fill' requires --value")
        if args.action == "type" and args.value is None:
            parser.error("action 'type' requires --value")
        if args.action == "press" and args.key is None:
            parser.error("action 'press' requires --key")
        if args.state is not None and args.action != "wait":
            parser.error("--state can only be used with action 'wait'")
        if args.slowly and args.action != "type":
            parser.error("--slowly can only be used with action 'type'")
        with _page_for_target(args.target) as page:
            try:
                snapshot_then_act_by_role_ref(
                    page,
                    args.role_ref,
                    args.action,
                    args.value,
                    args.key,
                    args.timeout_ms,
                    args.state,
                    args.slowly,
                    include_roles=None,
                )
            except ValueError as exc:
                print(str(exc), file=sys.stderr)
                return 1
            if args.print_title:
                print(page.title())
        return 0

    if args.command == "snapshot-extract-text":
        include_roles = None
        if args.include_role is not None:
            include_roles = set()
            for entry in args.include_role:
                role = entry.strip().lower() if entry is not None else ""
                if not role:
                    parser.error("--include-role cannot be empty")
                include_roles.add(role)
        with _page_for_target(args.target) as page:
            try:
                text = snapshot_then_extract_text_by_role_ref(
                    page,
                    args.role_ref,
                    include_roles=include_roles,
                    timeout_ms=args.timeout_ms,
                    state=args.state,
                )
            except ValueError as exc:
                print(str(exc), file=sys.stderr)
                return 1
        if args.json:
            print(json.dumps({"text": text, "role_ref": args.role_ref}))
        else:
            print(text)
        return 0

    if args.command in {"act", "act-by-role"}:
        if args.action == "fill" and args.value is None:
            parser.error("action 'fill' requires --value")
        if args.action == "type" and args.value is None:
            parser.error("action 'type' requires --value")
        if args.action == "press" and args.key is None:
            parser.error("action 'press' requires --key")
        if args.state is not None and args.action != "wait":
            parser.error("--state can only be used with action 'wait'")
        if args.slowly and args.action != "type":
            parser.error("--slowly can only be used with action 'type'")
        role_ref = RoleRef(role=args.role, name=args.name, nth=args.nth).to_str()
        with _page_for_target(args.target) as page:
            act_by_role_ref(
                page,
                role_ref,
                args.action,
                args.value,
                args.key,
                args.timeout_ms,
                args.state,
                args.slowly,
            )
            if args.print_title:
                print(page.title())
        return 0

    parser.error("Unknown command")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
