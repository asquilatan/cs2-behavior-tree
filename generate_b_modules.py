#!/usr/bin/env python3
"""Generate KV3 subtrees for B Anchor (Role B1) and B Rotate (Role B2) from mirage_positions.md."""
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
                sections[current_sec].append((pos_str, ang_str))
    return sections

def build_kv3_module(name: str, pos_list: list[tuple[str, str]], doc_comment: str) -> str:
    n = len(pos_list)
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

    # 2. Main position selector (pick random position from pool & hold for ~16s)
    out.append("\t\t// Pick a random position from pool and hold with setang angle")
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
    out.append(f"\t\t\t\t\t\tmin = 0")
    out.append(f"\t\t\t\t\t\tmax = {n - 1}")
    out.append("\t\t\t\t\t\toutput = \"PosChoice\"")
    out.append("\t\t\t\t\t},")
    out.append("\t\t\t\t\t{")
    out.append("\t\t\t\t\t\ttype = \"selector\"")
    out.append("\t\t\t\t\t\tchildren =")
    out.append("\t\t\t\t\t\t[")
    
    for i, (pos, ang) in enumerate(pos_list):
        comma = "," if i < n - 1 else ""
        out.append("\t\t\t\t\t\t\t{")
        out.append("\t\t\t\t\t\t\t\ttype = \"condition_is_equal\"")
        out.append("\t\t\t\t\t\t\t\tsource = \"PosChoice\"")
        out.append(f"\t\t\t\t\t\t\t\tdestination = {i}")
        out.append("\t\t\t\t\t\t\t\tchild =")
        out.append("\t\t\t\t\t\t\t\t{")
        out.append("\t\t\t\t\t\t\t\t\ttype = \"sequencer\"")
        out.append("\t\t\t\t\t\t\t\t\tchildren =")
        out.append("\t\t\t\t\t\t\t\t\t[")
        out.append("\t\t\t\t\t\t\t\t\t\t{")
        out.append("\t\t\t\t\t\t\t\t\t\t\ttype = \"action_move_to\"")
        out.append(f"\t\t\t\t\t\t\t\t\t\t\tdestination = \"{pos}\"")
        out.append("\t\t\t\t\t\t\t\t\t\t\tmovement_type = \"BT_ACTION_MOVETO_RUN\"")
        out.append("\t\t\t\t\t\t\t\t\t\t\troute_type = \"BT_ACTION_MOVETO_FASTEST_ROUTE\"")
        out.append("\t\t\t\t\t\t\t\t\t\t},")
        out.append("\t\t\t\t\t\t\t\t\t\t{")
        out.append("\t\t\t\t\t\t\t\t\t\t\ttype = \"action_look_at\"")
        out.append(f"\t\t\t\t\t\t\t\t\t\t\tinput_angles = \"{ang}\"")
        out.append("\t\t\t\t\t\t\t\t\t\t},")
        out.append("\t\t\t\t\t\t\t\t\t\t{")
        out.append("\t\t\t\t\t\t\t\t\t\t\ttype = \"action_wait\"")
        out.append("\t\t\t\t\t\t\t\t\t\t\twait_time_min = 14.0")
        out.append("\t\t\t\t\t\t\t\t\t\t\twait_time_max = 18.0")
        out.append("\t\t\t\t\t\t\t\t\t\t}")
        out.append("\t\t\t\t\t\t\t\t\t]")
        out.append("\t\t\t\t\t\t\t\t}")
        out.append(f"\t\t\t\t\t\t\t}}{comma}")

    out.append("\t\t\t\t\t\t]")
    out.append("\t\t\t\t\t}")
    out.append("\t\t\t\t]")
    out.append("\t\t\t}")
    out.append("\t\t}")
    out.append("\t]")
    out.append("}")
    return "\n".join(out)

def main():
    repo = Path(__file__).resolve().parent
    md = repo / "ln" / "mirage_b_positions.md"
    sections = parse_positions(md)

    b_anchor = sections.get("B Anchor (Role B1)", [])
    b_rotate_aggro = sections.get("B Rotate - Aggro (Role B2)", [])
    b_rotate_passive = sections.get("B Rotate - Passive (Role B2)", [])
    b_rotate_all = b_rotate_aggro + b_rotate_passive

    print(f"Parsed {len(b_anchor)} B Anchor positions.")
    print(f"Parsed {len(b_rotate_all)} B Rotate positions ({len(b_rotate_aggro)} aggro, {len(b_rotate_passive)} passive).")

    kv3_anchor = build_kv3_module("bt_b_anchor", b_anchor, "B Anchor Defense Module (Role B1) using scripted setpos/setang")
    kv3_rotate = build_kv3_module("bt_b_rotate", b_rotate_all, "B Rotate Defense Module (Role B2) using scripted setpos/setang")

    (repo / "ln" / "modules" / "bt_b_anchor.kv3").write_text(kv3_anchor, encoding="utf-8")
    (repo / "ln" / "modules" / "bt_b_rotate.kv3").write_text(kv3_rotate, encoding="utf-8")
    print("Generated bt_b_anchor.kv3 and bt_b_rotate.kv3 successfully.")

if __name__ == "__main__":
    main()
