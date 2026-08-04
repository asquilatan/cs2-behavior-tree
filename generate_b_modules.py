#!/usr/bin/env python3
"""Generate clean, non-interrupting KV3 subtrees for B Anchor and B Rotate for ln_mirage."""
import re
from pathlib import Path

KV3_HEADER = "<!-- kv3 encoding:text:version{e21c7f3c-8a33-41c5-9977-a76d3a32aa0d} format:generic:version{7412167c-06e9-4698-aff2-e63eb59037e7} -->"

def parse_positions(md_path: Path):
    content = md_path.read_text(encoding="utf-8")
    sections = {}
    current_sec = None
    for line in content.splitlines():
        if line.startswith("## "):
            current_sec = line[3:].strip()
            sections[current_sec] = []
        elif current_sec and "setpos " in line and "setang " in line:
            m = re.search(r"setpos\s+([-\d\.\s]+);setang\s+([-\d\.\s]+)", line)
            if m:
                pos_str = m.group(1).strip()
                ang_str = m.group(2).strip()
                ang_parts = ang_str.split()
                if len(ang_parts) == 2:
                    ang_str += " 0.000000"
                sections[current_sec].append((pos_str, ang_str))
    return sections

def build_position_step(pos_list: list[tuple[str, str]], indent: str) -> list[str]:
    out = []
    n = len(pos_list)
    for i, (pos, ang) in enumerate(pos_list):
        comma = "," if i < n - 1 else ""
        out.append(f"{indent}{{")
        out.append(f"{indent}\ttype = \"condition_is_equal\"")
        out.append(f"{indent}\tsource = \"PosChoice\"")
        out.append(f"{indent}\tdestination = {i}")
        out.append(f"{indent}\tchild =")
        out.append(f"{indent}\t{{")
        out.append(f"{indent}\t\ttype = \"sequencer\"")
        out.append(f"{indent}\t\tchildren =")
        out.append(f"{indent}\t\t[")
        out.append(f"{indent}\t\t\t{{")
        out.append(f"{indent}\t\t\t\ttype = \"action_move_to\"")
        out.append(f"{indent}\t\t\t\tdestination = \"{pos}\"")
        out.append(f"{indent}\t\t\t\tmovement_type = \"BT_ACTION_MOVETO_RUN\"")
        out.append(f"{indent}\t\t\t\troute_type = \"BT_ACTION_MOVETO_FASTEST_ROUTE\"")
        out.append(f"{indent}\t\t\t}},")
        out.append(f"{indent}\t\t\t{{")
        out.append(f"{indent}\t\t\t\ttype = \"action_look_at\"")
        out.append(f"{indent}\t\t\t\tinput_angles = \"{ang}\"")
        out.append(f"{indent}\t\t\t}},")
        out.append(f"{indent}\t\t\t{{")
        out.append(f"{indent}\t\t\t\ttype = \"action_wait\"")
        out.append(f"{indent}\t\t\t\twait_time_min = 14.0")
        out.append(f"{indent}\t\t\t\twait_time_max = 18.0")
        out.append(f"{indent}\t\t\t}}")
        out.append(f"{indent}\t\t]")
        out.append(f"{indent}\t}}")
        out.append(f"{indent}}}{comma}")
    return out

def build_kv3_module(name: str, pos_list: list[tuple[str, str]], doc_comment: str) -> str:
    out = [KV3_HEADER, "{", f"\t// {doc_comment}", "\ttype = \"selector\"", "\tchildren =", "\t["]
    
    # 1. High-priority noise hold branch
    out.append("\t\t// Instant hold when noise/event heard within hearing radius")
    out.append("\t\t{")
    out.append("\t\t\ttype = \"condition_is_empty\"")
    out.append("\t\t\tinput = \"ShortTermInvestigateMemory\"")
    out.append("\t\t\tnegated = 1")
    out.append("\t\t\tchild =")
    out.append("\t\t\t{")
    out.append("\t\t\t\ttype = \"sequencer\"")
    out.append("\t\t\t\tchildren =")
    out.append("\t\t\t\t[")
    out.append("\t\t\t\t\t{")
    out.append("\t\t\t\t\t\ttype = \"action_look_at\"")
    out.append("\t\t\t\t\t\tinput_location = \"ShortTermInvestigateMemory\"")
    out.append("\t\t\t\t\t},")
    out.append("\t\t\t\t\t{")
    out.append("\t\t\t\t\t\ttype = \"action_wait\"")
    out.append("\t\t\t\t\t\twait_time_min = 4")
    out.append("\t\t\t\t\t\twait_time_max = 8")
    out.append("\t\t\t\t\t}")
    out.append("\t\t\t\t]")
    out.append("\t\t\t}")
    out.append("\t\t},")

    # 2. Main position cycling (pick position, move, look_at, and hold 14-18s).
    #    CRITICAL: the random roll must be a BARE sibling of the move inside the
    #    sequencer, NOT a decorator wrapping it. CS2 re-rolls decorator_random_int
    #    while its child runs, so wrapping the move makes the bot re-pick a new
    #    destination every tick -> micro-step / freeze loop in spawn.
    out.append("\t\t// Main position selector (non-interrupting move + hold)")
    out.append("\t\t{")
    out.append("\t\t\ttype = \"decorator_repeat\"")
    out.append("\t\t\tchild =")
    out.append("\t\t\t{")
    out.append("\t\t\t\ttype = \"sequencer\"")
    out.append("\t\t\t\tchildren =")
    out.append("\t\t\t\t[")
    out.append("\t\t\t\t\t{")
    out.append("\t\t\t\t\t\ttype = \"action_equip_weapon\"")
    out.append("\t\t\t\t\t\tweapon = \"BEST\"")
    out.append("\t\t\t\t\t},")
    out.append("\t\t\t\t\t{")
    out.append("\t\t\t\t\t\ttype = \"decorator_random_int\"")
    out.append("\t\t\t\t\t\tmin = 0")
    out.append(f"\t\t\t\t\t\tmax = {len(pos_list) - 1}")
    out.append("\t\t\t\t\t\toutput = \"PosChoice\"")
    out.append("\t\t\t\t\t},")
    out.append("\t\t\t\t\t{")
    out.append("\t\t\t\t\t\ttype = \"selector\"")
    out.append("\t\t\t\t\t\tchildren =")
    out.append("\t\t\t\t\t\t[")
    out.extend(build_position_step(pos_list, "\t\t\t\t\t\t\t"))
    out.append("\t\t\t\t\t\t]")
    out.append("\t\t\t\t\t}")
    out.append("\t\t\t\t]")
    out.append("\t\t\t}")
    out.append("\t\t}")

    out.append("\t]")
    out.append("}")
    return "\n".join(out)

def main():
    print("DEPRECATED: use generate_util_modules.py (keeps the early/cycle-end utility blocks).")
    repo = Path(__file__).resolve().parent
    md = repo / "ln_mirage" / "mirage_b_positions.md"
    sections = parse_positions(md)

    b_anchor_all = sections.get("B Anchor (Role B1)", [])
    b_rotate_aggro = sections.get("B Rotate - Aggro (Role B2)", [])
    b_rotate_passive = sections.get("B Rotate - Passive (Role B2)", [])
    b_rotate_all = b_rotate_aggro + b_rotate_passive

    kv3_anchor = build_kv3_module("bt_b_anchor", b_anchor_all, "B Anchor Defense Module (Role B1)")
    kv3_rotate = build_kv3_module("bt_b_rotate", b_rotate_all, "B Rotate Defense Module (Role B2)")

    base = repo / "ln_mirage" / "modules"
    base.mkdir(parents=True, exist_ok=True)
    (base / "bt_b_anchor.kv3").write_text(kv3_anchor, encoding="utf-8")
    (base / "bt_b_rotate.kv3").write_text(kv3_rotate, encoding="utf-8")

    print("Generated clean B modules for ln_mirage successfully.")

if __name__ == "__main__":
    main()
