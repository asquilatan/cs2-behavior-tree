#!/usr/bin/env python3
"""Generate the 5 CT defense modules for ln_mirage from the md sources of truth.

Sources:
- ln_mirage/mirage_a_mid_positions.md  (A Anchor, A Rotate, Mid Player positions)
- ln_mirage/mirage_b_positions.md      (B Anchor, B Rotate positions)
- ln_mirage/mirage_utility_lineups.md  (utility lineups tagged [Early], [Chain], or untagged)

Each module sequence inside decorator_repeat:
  equip BEST -> early utility block (if any) -> pick position -> move & hold angle (14-18s) -> 75% post-hold util block (if any).
"""
import re
import subprocess
import sys
from pathlib import Path

KV3_HEADER = "<!-- kv3 encoding:text:version{e21c7f3c-8a33-41c5-9977-a76d3a32aa0d} format:generic:version{7412167c-06e9-4698-aff2-e63eb59037e7} -->"

ITEM_BY_KIND = {
    "Smoke": "weapon_smokegrenade",
    "Molly": "weapon_molotov",
    "Nade": "weapon_hegrenade",
    "Flash": "weapon_flashbang",
}

UTILITY_MD = "ln_mirage/mirage_utility_lineups.md"
POS_A_MD = "ln_mirage/mirage_a_mid_positions.md"
POS_B_MD = "ln_mirage/mirage_b_positions.md"

MODULES = [
    ("bt_b_anchor",  "B Anchor", POS_B_MD,
     ["B Anchor (Role B1)"], "B Anchor Defense Module (Role B1)"),
    ("bt_b_rotate",  "B Rotate", POS_B_MD,
     ["B Rotate - Aggro (Role B2)", "B Rotate - Passive (Role B2)"], "B Rotate Defense Module (Role B2)"),
    ("bt_a_anchor",  "A Anchor", POS_A_MD,
     ["A Anchor - Passive (Role A1)", "A Anchor - Aggro (Role A1)"], "A Anchor Defense Module (Role A1)"),
    ("bt_a_rotate",  "A Rotate", POS_A_MD,
     ["A Rotate - Passive (Role A2)", "A Rotate - Aggro (Role A2)"], "A Rotate Defense Module (Role A2)"),
    ("bt_mid_player", "Mid", POS_A_MD,
     ["Mid Player (Role Mid)"], "Mid Player Defense Module (Role Mid)"),
]


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


def parse_utility(md_path: Path):
    """Returns {section: [ {tags, kind, pos, ang, label} ]} preserving md order."""
    content = md_path.read_text(encoding="utf-8")
    sections = {}
    current_sec = None
    for line in content.splitlines():
        if line.startswith("## "):
            current_sec = line[3:].strip()
            sections[current_sec] = []
        elif current_sec and "setpos " in line and "setang " in line:
            lm = re.match(r'^\s*\d+\.\s*`([^`]+)`\s*:', line)
            sm = re.search(r"setpos\s+([-\d\.\s]+);setang\s+([-\d\.\s]+)", line)
            if not (lm and sm):
                continue
            label = lm.group(1)
            tags = []
            if label.startswith("["):
                end = label.find("]")
                tags = [t.strip() for t in label[1:end].split(",")]
                label = label[end + 1:].strip()
            kind = None
            for k in ("Smoke", "Molly", "Nade", "Flash"):
                if k in label:
                    kind = k
                    break
            if kind is None:
                print(f"  [WARN] {current_sec}: unrecognized utility in '{label}' - skipped")
                continue
            if "LJ" in label:
                print(f"  [SKIP] {current_sec}: '{label}' is a jump throw (LJ), not generated")
                continue
            pos_str = sm.group(1).strip()
            ang_str = sm.group(2).strip()
            ang_parts = ang_str.split()
            if len(ang_parts) == 2:
                ang_str += " 0.000000"
            sections[current_sec].append({
                "tags": tags, "kind": kind, "pos": pos_str, "ang": ang_str, "label": label,
            })
    return sections


def build_owns_condition(kind, indent):
    """Support both weapon_incgrenade (CT) and weapon_molotov (T) for Molly."""
    if kind == "Molly":
        return [
            f"{indent}{{",
            f"{indent}\ttype = \"selector\"",
            f"{indent}\tchildren =",
            f"{indent}\t[",
            f"{indent}\t\t{{",
            f"{indent}\t\t\ttype = \"condition_owns_item\"",
            f"{indent}\t\t\titem = \"weapon_incgrenade\"",
            f"{indent}\t\t}},",
            f"{indent}\t\t{{",
            f"{indent}\t\t\ttype = \"condition_owns_item\"",
            f"{indent}\t\t\titem = \"weapon_molotov\"",
            f"{indent}\t\t}}",
            f"{indent}\t]",
            f"{indent}}}"
        ]
    else:
        item = ITEM_BY_KIND[kind]
        return [
            f"{indent}{{",
            f"{indent}\ttype = \"condition_owns_item\"",
            f"{indent}\titem = \"{item}\"",
            f"{indent}}}"
        ]


def build_equip_step(kind, indent):
    """Equip weapon_incgrenade or weapon_molotov if Molly, else single item."""
    if kind == "Molly":
        return [
            f"{indent}{{",
            f"{indent}\ttype = \"selector\"",
            f"{indent}\tchildren =",
            f"{indent}\t[",
            f"{indent}\t\t{{",
            f"{indent}\t\t\ttype = \"sequencer\"",
            f"{indent}\t\t\tchildren =",
            f"{indent}\t\t\t[",
            f"{indent}\t\t\t\t{{",
            f"{indent}\t\t\t\t\ttype = \"condition_owns_item\"",
            f"{indent}\t\t\t\t\titem = \"weapon_incgrenade\"",
            f"{indent}\t\t\t\t}},",
            f"{indent}\t\t\t\t{{",
            f"{indent}\t\t\t\t\ttype = \"action_equip_item\"",
            f"{indent}\t\t\t\t\titem = \"weapon_incgrenade\"",
            f"{indent}\t\t\t\t}}",
            f"{indent}\t\t\t]",
            f"{indent}\t\t}},",
            f"{indent}\t\t{{",
            f"{indent}\t\t\ttype = \"sequencer\"",
            f"{indent}\t\t\tchildren =",
            f"{indent}\t\t\t[",
            f"{indent}\t\t\t\t{{",
            f"{indent}\t\t\t\t\ttype = \"condition_owns_item\"",
            f"{indent}\t\t\t\t\titem = \"weapon_molotov\"",
            f"{indent}\t\t\t\t}},",
            f"{indent}\t\t\t\t{{",
            f"{indent}\t\t\t\t\ttype = \"action_equip_item\"",
            f"{indent}\t\t\t\t\titem = \"weapon_molotov\"",
            f"{indent}\t\t\t\t}}",
            f"{indent}\t\t\t]",
            f"{indent}\t\t}}",
            f"{indent}\t]",
            f"{indent}}}"
        ]
    else:
        item = ITEM_BY_KIND[kind]
        return [
            f"{indent}{{",
            f"{indent}\ttype = \"action_equip_item\"",
            f"{indent}\titem = \"{item}\"",
            f"{indent}}}"
        ]


def build_throw_core(entry, indent):
    """equip item -> move to spot -> look at lineup -> wait .3 -> trigger -> wait .4 -> re-equip BEST."""
    out = []
    out.extend(build_equip_step(entry["kind"], indent))
    out[-1] += ","
    out.extend([
        f"{indent}{{",
        f"{indent}\ttype = \"action_move_to\"",
        f"{indent}\tdestination = \"{entry['pos']}\"",
        f"{indent}\tmovement_type = \"BT_ACTION_MOVETO_RUN\"",
        f"{indent}\troute_type = \"BT_ACTION_MOVETO_FASTEST_ROUTE\"",
        f"{indent}}},",
        f"{indent}{{",
        f"{indent}\ttype = \"action_look_at\"",
        f"{indent}\tinput_angles = \"{entry['ang']}\"",
        f"{indent}}},",
        f"{indent}{{",
        f"{indent}\ttype = \"action_wait\"",
        f"{indent}\twait_time_min = 0.3",
        f"{indent}\twait_time_max = 0.3",
        f"{indent}}},",
        f"{indent}{{",
        f"{indent}\ttype = \"action_pull_trigger\"",
        f"{indent}}},",
        f"{indent}{{",
        f"{indent}\ttype = \"action_wait\"",
        f"{indent}\twait_time_min = 0.4",
        f"{indent}\twait_time_max = 0.4",
        f"{indent}}},",
        f"{indent}{{",
        f"{indent}\ttype = \"action_equip_weapon\"",
        f"{indent}\tweapon = \"BEST\"",
        f"{indent}}}"
    ])
    return out


def build_throw_option(entry, indent, maybe=None, comma=True):
    """sequencer [ owns_item, (maybe), sequencer [ throw core ] ]"""
    out = [f"{indent}{{", f"{indent}\ttype = \"sequencer\"", f"{indent}\tchildren =", f"{indent}\t["]
    owns_lines = build_owns_condition(entry["kind"], f"{indent}\t\t")
    owns_lines[-1] += ","
    out.extend(owns_lines)

    if maybe is not None:
        out.append(f"{indent}\t\t{{")
        out.append(f"{indent}\t\t\ttype = \"decorator_maybe\"")
        out.append(f"{indent}\t\t\tchance = {maybe}")
        out.append(f"{indent}\t\t\tchild =")
        out.append(f"{indent}\t\t\t{{")
        out.append(f"{indent}\t\t\t\ttype = \"sequencer\"")
        out.append(f"{indent}\t\t\t\tchildren =")
        out.append(f"{indent}\t\t\t\t[")
        out.extend(build_throw_core(entry, f"{indent}\t\t\t\t\t"))
        out.append(f"{indent}\t\t\t\t]")
        out.append(f"{indent}\t\t\t}}")
        out.append(f"{indent}\t\t}}")
    else:
        out.append(f"{indent}\t\t{{")
        out.append(f"{indent}\t\t\ttype = \"sequencer\"")
        out.append(f"{indent}\t\t\tchildren =")
        out.append(f"{indent}\t\t\t[")
        out.extend(build_throw_core(entry, f"{indent}\t\t\t\t"))
        out.append(f"{indent}\t\t\t]")
        out.append(f"{indent}\t\t}}")
    out.append(f"{indent}\t]")
    out.append(f"{indent}}}{',' if comma else ''}")
    return out


def build_chain_throw_option(chain_entries, indent, maybe=None, comma=True):
    """Executes multiple chain throws in sequence if owned."""
    out = [f"{indent}{{", f"{indent}\ttype = \"sequencer\"", f"{indent}\tchildren =", f"{indent}\t["]
    if maybe is not None:
        out.append(f"{indent}\t\t{{")
        out.append(f"{indent}\t\t\ttype = \"decorator_maybe\"")
        out.append(f"{indent}\t\t\tchance = {maybe}")
        out.append(f"{indent}\t\t\tchild =")
        out.append(f"{indent}\t\t\t{{")
        out.append(f"{indent}\t\t\t\ttype = \"sequencer\"")
        out.append(f"{indent}\t\t\t\tchildren =")
        out.append(f"{indent}\t\t\t\t[")
        for j, entry in enumerate(chain_entries):
            out.append(f"{indent}\t\t\t\t\t{{")
            out.append(f"{indent}\t\t\t\t\t\ttype = \"decorator_succeed\"")
            out.append(f"{indent}\t\t\t\t\t\tchild =")
            out.append(f"{indent}\t\t\t\t\t\t{{")
            out.append(f"{indent}\t\t\t\t\t\t\ttype = \"sequencer\"")
            out.append(f"{indent}\t\t\t\t\t\t\tchildren =")
            out.append(f"{indent}\t\t\t\t\t\t\t[")
            owns_lines = build_owns_condition(entry["kind"], f"{indent}\t\t\t\t\t\t\t\t")
            owns_lines[-1] += ","
            out.extend(owns_lines)
            out.extend(build_throw_core(entry, f"{indent}\t\t\t\t\t\t\t\t"))
            out.append(f"{indent}\t\t\t\t\t\t\t]")
            out.append(f"{indent}\t\t\t\t\t\t}}")
            out.append(f"{indent}\t\t\t\t\t}}{',' if j < len(chain_entries) - 1 else ''}")
        out.append(f"{indent}\t\t\t\t]")
        out.append(f"{indent}\t\t\t}}")
        out.append(f"{indent}\t\t}}")
    else:
        for j, entry in enumerate(chain_entries):
            out.append(f"{indent}\t\t{{")
            out.append(f"{indent}\t\t\ttype = \"decorator_succeed\"")
            out.append(f"{indent}\t\t\tchild =")
            out.append(f"{indent}\t\t\t{{")
            out.append(f"{indent}\t\t\t\ttype = \"sequencer\"")
            out.append(f"{indent}\t\t\t\tchildren =")
            out.append(f"{indent}\t\t\t\t[")
            owns_lines = build_owns_condition(entry["kind"], f"{indent}\t\t\t\t\t")
            owns_lines[-1] += ","
            out.extend(owns_lines)
            out.extend(build_throw_core(entry, f"{indent}\t\t\t\t\t"))
            out.append(f"{indent}\t\t\t\t]")
            out.append(f"{indent}\t\t\t}}")
            out.append(f"{indent}\t\t}}{',' if j < len(chain_entries) - 1 else ''}")
    out.append(f"{indent}\t]")
    out.append(f"{indent}}}{',' if comma else ''}")
    return out


def build_early_block(entries, indent):
    """decorator_succeed > selector of throw options (~6-10s into round, before angle hold)."""
    out = [f"{indent}// Early utility throw (~6-10s into the round, before holding angle)"]
    out.append(f"{indent}{{")
    out.append(f"{indent}\ttype = \"decorator_succeed\"")
    out.append(f"{indent}\tchild =")
    out.append(f"{indent}\t{{")
    out.append(f"{indent}\t\ttype = \"selector\"")
    out.append(f"{indent}\t\tchildren =")
    out.append(f"{indent}\t\t[")
    for i, entry in enumerate(entries):
        maybe = 0.5 if i == 0 and len(entries) > 1 else None
        out.extend(build_throw_option(entry, f"{indent}\t\t\t", maybe=maybe,
                                      comma=i < len(entries) - 1))
    out.append(f"{indent}\t\t]")
    out.append(f"{indent}\t}}")
    out.append(f"{indent}}}")
    return out


def build_post_block(entries, indent):
    """decorator_succeed > decorator_maybe (0.75) > selector of post-hold throw options.
    75% chance of throwing post-hold utility after holding an angle, 25% chance of skipping."""
    if not entries:
        return []

    out = [f"{indent}// Post-hold utility throw (75% chance after holding angle)"]
    out.append(f"{indent}{{")
    out.append(f"{indent}\ttype = \"decorator_succeed\"")
    out.append(f"{indent}\tchild =")
    out.append(f"{indent}\t{{")
    out.append(f"{indent}\t\ttype = \"decorator_maybe\"")
    out.append(f"{indent}\t\tchance = 0.75")
    out.append(f"{indent}\t\tchild =")
    out.append(f"{indent}\t\t{{")
    out.append(f"{indent}\t\t\ttype = \"selector\"")
    out.append(f"{indent}\t\t\tchildren =")
    out.append(f"{indent}\t\t\t[")

    items_to_render = []
    i = 0
    while i < len(entries):
        if "Chain" in entries[i]["tags"]:
            chain_group = []
            while i < len(entries) and "Chain" in entries[i]["tags"]:
                chain_group.append(entries[i])
                i += 1
            items_to_render.append(("chain", chain_group))
        else:
            items_to_render.append(("single", entries[i]))
            i += 1

    n = len(items_to_render)
    for idx, (kind_type, item) in enumerate(items_to_render):
        is_last = (idx == n - 1)
        maybe = 0.5 if (n > 1 and not is_last) else None
        
        if kind_type == "single":
            out.extend(build_throw_option(item, f"{indent}\t\t\t\t", maybe=maybe, comma=not is_last))
        elif kind_type == "chain":
            out.extend(build_chain_throw_option(item, f"{indent}\t\t\t\t", maybe=maybe, comma=not is_last))

    out.append(f"{indent}\t\t\t]")
    out.append(f"{indent}\t\t}}")
    out.append(f"{indent}\t}}")
    out.append(f"{indent}}}")
    return out


def build_position_step(pos_list, indent):
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


def build_kv3_module(doc_comment, pos_list, early_entries, post_entries):
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
    if early_entries:
        early_lines = build_early_block(early_entries, "\t\t\t\t\t")
        early_lines[-1] += ","  # mid-array sibling: needs a trailing comma
        out.extend(early_lines)
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
    if post_entries:
        out[-1] += ","
        post_lines = build_post_block(post_entries, "\t\t\t\t\t")
        out.extend(post_lines)
    out.append("\t\t\t\t]")
    out.append("\t\t\t}")
    out.append("\t\t}")

    out.append("\t]")
    out.append("}")
    return "\n".join(out)


def main():
    repo = Path(__file__).resolve().parent
    util_sections = parse_utility(repo / UTILITY_MD)
    pos_sections = {**parse_positions(repo / POS_A_MD), **parse_positions(repo / POS_B_MD)}

    base = repo / "ln_mirage" / "modules"
    base.mkdir(parents=True, exist_ok=True)

    for name, util_sec, pos_md, pos_sections_names, doc in MODULES:
        pos_list = []
        for sec in pos_sections_names:
            pos_list += pos_sections.get(sec, [])
        all_utils = util_sections.get(util_sec, [])
        early_entries = [e for e in all_utils if "Early" in e["tags"]]
        post_entries = [e for e in all_utils if "Early" not in e["tags"]]

        if not pos_list:
            print(f"  [FAIL] {name}: no positions found for {pos_sections_names}")
            continue
        kv3 = build_kv3_module(doc, pos_list, early_entries, post_entries)
        (base / f"{name}.kv3").write_text(kv3, encoding="utf-8")

        early_labels = ", ".join(e["label"] for e in early_entries) or "none"
        post_labels = ", ".join(e["label"] for e in post_entries) or "none"
        print(f"  [OK]   {name}: {len(pos_list)} positions, early=[{early_labels}], post=[{post_labels}]")

    print("\nRunning validator...")
    subprocess.run([sys.executable, "check_kv3.py"], cwd=repo, check=False)


if __name__ == "__main__":
    main()
