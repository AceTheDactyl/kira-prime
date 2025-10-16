#!/usr/bin/env python3
from __future__ import annotations

"""VesselOS CLI (minimal)

Commands:
  generate   – rebuild schema + chapters
  listen     – process a single input line
  validate   – run validator via Kira
  mentor     – run Kira mentor (optionally --apply)
  publish    – dry-run publish
"""
import argparse
import json
import subprocess
import sys
from pathlib import Path

from interface.dispatcher import dispatch_freeform
from agents.kira.kira_agent import KiraAgent
from agents.echo.echo_agent import EchoAgent
from agents.garden.garden_agent import GardenAgent
from agents.limnus.limnus_agent import LimnusAgent


ROOT = Path(__file__).resolve().parent


def run(cmd: list[str]) -> int:
    p = subprocess.run(cmd, cwd=ROOT)
    return p.returncode


def cmd_generate(args: argparse.Namespace) -> int:
    rc = run(["python3", "src/schema_builder.py"]) or run(["python3", "src/generate_chapters.py"])
    return rc

def cmd_listen(args: argparse.Namespace) -> int:
    if args.text:
        res = dispatch_freeform(args.text)
        print(res)
        return 0
    print("Provide --text for now (streaming capture not implemented)")
    return 2

def cmd_validate(args: argparse.Namespace) -> int:
    result = KiraAgent(ROOT).validate()
    if isinstance(result, dict):
        print(json.dumps(result, indent=2))
        return 0 if result.get("passed") else 1
    print(result)
    return 0 if result == "valid" else 1

def cmd_mentor(args: argparse.Namespace) -> int:
    res = KiraAgent(ROOT).mentor(apply=args.apply)
    print(res)
    return 0

def cmd_publish(args: argparse.Namespace) -> int:
    assets = args.asset or []
    res = KiraAgent(ROOT).publish(
        run=args.run,
        release=args.release,
        tag=args.tag,
        notes_file=args.notes_file,
        notes=args.notes,
        assets=assets,
    )
    print(res)
    return 0


def cmd_echo(args: argparse.Namespace) -> int:
    e = EchoAgent(ROOT)
    if args.sub == "summon":
        print(e.summon())
    elif args.sub == "mode":
        print(e.mode(args.which))
    elif args.sub == "say":
        print(e.say(args.message))
    elif args.sub == "learn":
        print(e.learn(args.text))
    elif args.sub == "status":
        print(e.status())
    elif args.sub == "calibrate":
        print(e.calibrate())
    return 0


def cmd_garden(args: argparse.Namespace) -> int:
    g = GardenAgent(ROOT)
    if args.sub == "start":
        print(g.start())
    elif args.sub == "next":
        print(g.next())
    elif args.sub == "open":
        print(g.open(args.scroll, prev=args.prev, reset=args.reset))
    elif args.sub == "resume":
        print(g.resume())
    elif args.sub == "log":
        print(g.log(args.text))
    elif args.sub == "ledger":
        print(g.ledger())
    return 0


def cmd_limnus(args: argparse.Namespace) -> int:
    l = LimnusAgent(ROOT)
    if args.sub == "cache":
        print(l.cache(args.text))
    elif args.sub == "recall":
        print(l.recall(args.query))
    elif args.sub == "commit-block":
        print(l.commit_block(args.kind, {"text": args.data}))
    elif args.sub == "encode-ledger":
        print(l.encode_ledger())
    elif args.sub == "decode-ledger":
        print(l.decode_ledger())
    elif args.sub == "status":
        print(json.dumps(l.status(), indent=2))
    elif args.sub == "reindex":
        print(json.dumps(l.reindex(backend=args.backend), indent=2))
    return 0


def cmd_kira(args: argparse.Namespace) -> int:
    k = KiraAgent(ROOT)
    if args.sub == "validate":
        print(k.validate())
    elif args.sub == "mentor":
        print(k.mentor(apply=args.apply))
    elif args.sub == "mantra":
        print(k.mantra())
    elif args.sub == "seal":
        print(k.seal())
    elif args.sub == "push":
        print(k.push(run=args.run, message=args.message, include_all=args.all))
    elif args.sub == "publish":
        assets = args.asset or []
        print(
            k.publish(
                run=args.run,
                release=args.release,
                tag=args.tag,
                notes_file=args.notes_file,
                notes=args.notes,
                assets=assets,
            )
        )
    return 0


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(prog="vesselos", description="VesselOS Unified CLI")
    sub = ap.add_subparsers(dest="cmd", required=True)

    sg = sub.add_parser("generate", help="Rebuild schema and chapters")
    sg.set_defaults(func=cmd_generate)

    sl = sub.add_parser("listen", help="Process input through agents")
    sl.add_argument("--text", help="Input text", default=None)
    sl.set_defaults(func=cmd_listen)

    sv = sub.add_parser("validate", help="Run validator via Kira")
    sv.set_defaults(func=cmd_validate)

    sm = sub.add_parser("mentor", help="Run Kira mentor")
    sm.add_argument("--apply", action="store_true", help="Apply mentor recommendation")
    sm.set_defaults(func=cmd_mentor)

    sp = sub.add_parser("publish", help="Dry-run publish")
    sp.add_argument("--run", action="store_true")
    sp.add_argument("--release", action="store_true")
    sp.add_argument("--tag", default=None)
    sp.add_argument("--notes-file", default=None, help="Path to release notes file")
    sp.add_argument("--notes", default=None, help="Inline release notes text")
    sp.add_argument("--asset", action="append", default=None)
    sp.set_defaults(func=cmd_publish)

    # Echo subcommands
    se = sub.add_parser("echo", help="Echo agent commands")
    se_sub = se.add_subparsers(dest="sub", required=True)
    se0 = se_sub.add_parser("summon"); se0.set_defaults(func=cmd_echo)
    se1 = se_sub.add_parser("mode"); se1.add_argument("which"); se1.set_defaults(func=cmd_echo)
    se2 = se_sub.add_parser("say"); se2.add_argument("message"); se2.set_defaults(func=cmd_echo)
    se3 = se_sub.add_parser("learn"); se3.add_argument("text"); se3.set_defaults(func=cmd_echo)
    se4 = se_sub.add_parser("status"); se4.set_defaults(func=cmd_echo)
    se5 = se_sub.add_parser("calibrate"); se5.set_defaults(func=cmd_echo)

    # Garden subcommands
    sg2 = sub.add_parser("garden", help="Garden agent commands")
    sg2_sub = sg2.add_subparsers(dest="sub", required=True)
    sg2_sub.add_parser("start").set_defaults(func=cmd_garden)
    sg2_sub.add_parser("next").set_defaults(func=cmd_garden)
    op = sg2_sub.add_parser("open"); op.add_argument("scroll"); op.add_argument("--prev", action="store_true"); op.add_argument("--reset", action="store_true"); op.set_defaults(func=cmd_garden)
    sg2_sub.add_parser("resume").set_defaults(func=cmd_garden)
    gl = sg2_sub.add_parser("log"); gl.add_argument("text"); gl.set_defaults(func=cmd_garden)
    sg2_sub.add_parser("ledger").set_defaults(func=cmd_garden)

    # Limnus subcommands
    sl2 = sub.add_parser("limnus", help="Limnus agent commands")
    sl2_sub = sl2.add_subparsers(dest="sub", required=True)
    cc = sl2_sub.add_parser("cache"); cc.add_argument("text"); cc.set_defaults(func=cmd_limnus)
    rc = sl2_sub.add_parser("recall"); rc.add_argument("query", nargs="?"); rc.set_defaults(func=cmd_limnus)
    cb = sl2_sub.add_parser("commit-block"); cb.add_argument("kind"); cb.add_argument("data"); cb.set_defaults(func=cmd_limnus)
    sl2_sub.add_parser("encode-ledger").set_defaults(func=cmd_limnus)
    sl2_sub.add_parser("decode-ledger").set_defaults(func=cmd_limnus)
    st = sl2_sub.add_parser("status"); st.set_defaults(func=cmd_limnus)
    ri = sl2_sub.add_parser("reindex"); ri.add_argument("--backend", choices=["sbert", "faiss"], default=None); ri.set_defaults(func=cmd_limnus)

    # Kira subcommands
    sk2 = sub.add_parser("kira", help="Kira agent commands")
    sk2_sub = sk2.add_subparsers(dest="sub", required=True)
    sk2_sub.add_parser("validate").set_defaults(func=cmd_kira)
    me = sk2_sub.add_parser("mentor"); me.add_argument("--apply", action="store_true"); me.set_defaults(func=cmd_kira)
    sk2_sub.add_parser("mantra").set_defaults(func=cmd_kira)
    sk2_sub.add_parser("seal").set_defaults(func=cmd_kira)
    pu = sk2_sub.add_parser("push"); pu.add_argument("--run", action="store_true"); pu.add_argument("--message", default=None); pu.set_defaults(func=cmd_kira)
    pu.add_argument("--all", action="store_true", help="Stage untracked files as well")
    pb = sk2_sub.add_parser("publish")
    pb.add_argument("--run", action="store_true")
    pb.add_argument("--release", action="store_true")
    pb.add_argument("--tag", default=None)
    pb.add_argument("--notes-file", default=None)
    pb.add_argument("--notes", default=None)
    pb.add_argument("--asset", action="append", default=None)
    pb.set_defaults(func=cmd_kira)

    args = ap.parse_args(argv[1:])
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
