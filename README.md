# CS2 Behavior Tree Scripts

This repo contains my CS2 behavior tree scripts for pro-esque bots.

## Installation

### General Setup
Simply place this repository in your CS2 scripts folder:
`.../game/csgo/scripts/ai`

### Map-Specific Scripts
For map-specific logic, you need to embed the script into the map's VPK file.

1.  Download a VPK editor, such as [VPKEdit](https://github.com/craftablescience/VPKEdit).
2.  Open the map's `.vpk` file.
3.  Place your script file inside the VPK.
4.  Save the VPK.

## Usage

To load a specific behavior tree script in-game, use the console command:

```
mp_bot_ai_bt <script_name>
```

Example: `mp_bot_ai_bt scripts/ai/ln/bt_default.kv3`

## Credits

Special thanks to u/Beeplsla for making it possible, as I never knew that god bots beyond botprofile.db mods were possible (and performed better). 

https://www.reddit.com/r/GlobalOffensive/comments/1ehbktk/comment/lfyy07j/



(Honestly, I just wanted bots that peeked like XANTARES, awped like s1mple, and whatever else pros could do)