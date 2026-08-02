# Bot Behavior Trees

In  [Counter-Strike: Global Offensive](https://developer.valvesoftware.com/wiki/Counter-Strike:_Global_Offensive), [bots](https://developer.valvesoftware.com/wiki/Bot) can be given a **Behavior Tree** to follow. A behavior tree dictates how the bot senses things (vision, hearing, damage sensing), moves, attacks, and does other actions.

Behavior trees are text files which use [Valve](https://developer.valvesoftware.com/wiki/Valve)'s proprietary [KeyValues3](https://developer.valvesoftware.com/wiki/KeyValues3) format (`.kv3`), which is a text-based format with somewhat strict syntax. They typically use the `bt_` prefix, to signify that file is a Behavior Tree. They are stored in `csgo/scripts/ai`. One can create and use their own behavior trees, see below.

Officially, behavior trees are used for the game modes  [Co-op Strike](https://developer.valvesoftware.com/wiki/Counter-Strike:_Global_Offensive/Game_Modes/Co-op_Strike),  [Guardian](https://developer.valvesoftware.com/wiki/Counter-Strike:_Global_Offensive/Game_Modes/Guardian) and  [Deathmatch](https://developer.valvesoftware.com/wiki/Counter-Strike:_Global_Offensive/Game_Modes/Deathmatch).

Behavior trees were first [added to the game](https://blog.counter-strike.net/index.php/2019/09/25510/) on September 16, 2019. Since September 1, 2020, [behavior trees can be packed into BSP files](https://blog.counter-strike.net/index.php/2020/09/31532/).

## Using Behavior Trees

There are some ways to use behavior tree files in-game.

* The [ConVar](https://developer.valvesoftware.com/wiki/ConVar) `mp_bot_ai_bt` determines a behavior tree that all respawning bots on the server (both T and CT!) will use. Its value is a string representing the path to a .kv3 file, starting from `csgo/`. If there are player respawns, killing a bot is sufficient to make them use a newly set file, otherwise restarting the game or round with `mp_restartgame 1` or `endround` should also do it. If a behavior tree file has been modified and if a bot had already loaded it, it is also necessary to flush the loaded files using `mp_bot_ai_bt_clear_cache` to make changes apply. As soon as a bot (re)spawns, there will be error messages containing `[AI BT]` if any used file has errors and the bot does not use any behavior tree. Example:The following line is used for official Deathmatch and can be found in `csgo/cfg/gamemode_deathmatch.cfg`: mp_bot_ai_bt "scripts/ai/deathmatch/bt_default.kv3"
* For  [Co-op Strike](https://developer.valvesoftware.com/wiki/Counter-Strike:_Global_Offensive/Game_Modes/Co-op_Strike), [info_enemy_terrorist_spawn](https://developer.valvesoftware.com/wiki/Info_enemy_terrorist_spawn) entities have the KeyValue `behavior_tree_file` that can be used to specify a behavior tree file only for bots spawning at this entity.

### Related Console Commands

| ConVar | Default Value | Description |
| --- | --- | --- |
| `cv_bot_ai_bt_debug_target` | -1 | Draw the behavior tree of the given bot. |
| `cv_bot_ai_bt_hiding_spot_show` | 0 | Draw hiding spots. |
| `cv_bot_ai_bt_moveto_show_next_hiding_spot` | 0 | Draw the hiding spot the bot will check next. |
| `mp_bot_ai_bt` | "" | Use the specified behavior tree file to drive the bot behavior (see [above](https://developer.valvesoftware.com/wiki/Counter-Strike:_Global_Offensive/Bot_Behavior_Trees#Using_Behavior_Trees)). |
| `mp_bot_ai_bt_clear_cache` | *ConCommand* | Clears the cache for behavior tree files. |

## File Format

To briefly summarize the file syntax:

* The game ignores consecutive whitespace characters and does not differentiate between them, so a file can be written in one line, but please don't. Newlines are used to increase readability, see the examples below.
* *KeyValues* are limited by curly brackets `{ }` and contain key-value pairs with the format `key = value key = value ...` where values can have different data types, such as [integer](https://developer.valvesoftware.com/wiki/Integer) (`1`), [float](https://developer.valvesoftware.com/wiki/Float) (`1.0`), [string](https://developer.valvesoftware.com/wiki/String) (`"1"`) and especially KeyValues themselves.
* *Arrays* are limited by squared brackets `[ ]` and their elements (no matter the data type) are separated by commas `,`, for example: `[ {...}, {...}, {...} ]`
* Inline comments start with `//`, multiline comments start with `/*` and end with `*/`.

The first line of a `.kv3` file is always a header specifying the KV3 version. For , use this header:

```kv3
<!-- kv3 encoding:text:version{e21c7f3c-8a33-41c5-9977-a76d3a32aa0d} format:generic:version{7412167c-06e9-4698-aff2-e63eb59037e7} -->
```

The rest of the file is one KeyValues, enclosed by curly brackets `{ }`. For Behavior Tree files, this KeyValues contains the keys `config` and `root`.
The `config` key determines a general bot configuration with the bot's "skill". Its value should contain the full path to such a file, including the file extension.
Valve has already provided three such config files, namely

* `"scripts/ai/deathmatch/bt_config.kv3"`,
* `"scripts/ai/guardian/bt_config.kv3"` and
* `"scripts/ai/coop/bt_config.kv3"`.

Generally speaking, we must add the following:

```kv3
<!-- kv3 encoding:text:version{e21c7f3c-8a33-41c5-9977-a76d3a32aa0d} format:generic:version{7412167c-06e9-4698-aff2-e63eb59037e7} -->
{
	config = "scripts/ai/<path to bt_config>/<bt_config_name>.kv3"
}
```

Next, add the `root` key with a Behavior Node as value. The game "executes" the root node regularly.[*Clarify*]

```kv3
<!-- kv3 encoding:text:version{e21c7f3c-8a33-41c5-9977-a76d3a32aa0d} format:generic:version{7412167c-06e9-4698-aff2-e63eb59037e7} -->
{
	config = "scripts/ai/<path to bt_config>/<bt_config_name>.kv3"
	root = 
	{
		<Behavior Node>
	}
}
```

Behavior Nodes are once again KeyValues but with a `type` key whose value determines its node type. There are different types of nodes, namely

* direct [#Actions](https://developer.valvesoftware.com/wiki/Counter-Strike:_Global_Offensive/Bot_Behavior_Trees#Actions) that the bot will perform, such as `type = "action_pull_trigger", "action_use", "action_jump"` or `"action_wait"`,
* four [#Combinators](https://developer.valvesoftware.com/wiki/Counter-Strike:_Global_Offensive/Bot_Behavior_Trees#Combinators) that determine how multiple nodes are executed, for example in a `sequence` or `parallel`,
* [#Decorators](https://developer.valvesoftware.com/wiki/Counter-Strike:_Global_Offensive/Bot_Behavior_Trees#Decorators) mostly for generating/getting/storing data, such as `decorator_sensor`, `decorator_random_int` or `decorator_memory`.
* [#Conditions](https://developer.valvesoftware.com/wiki/Counter-Strike:_Global_Offensive/Bot_Behavior_Trees#Conditions) for comparing data and branching.

```kv3
<!-- kv3 encoding:text:version{e21c7f3c-8a33-41c5-9977-a76d3a32aa0d} format:generic:version{7412167c-06e9-4698-aff2-e63eb59037e7} -->
{
	config = "scripts/ai/<path to bt_config>/<bt_config_name>.kv3"
	root = 
	{
		type = <Node Type>
		<parameter> = <value>
		...
		child = 
		{
			<Behavior Node>
		}
	}
}
```

The format of each Behavior Node depends on its type, because most Behavior Nodes use their specific parameter names, value types and uses.

Some nodes allow to define new global variables. Their input names should contain both double and single quotes:

```kv3
type = "action_set_global_counter"
input_name = "'Test'" // Note those quotation marks.
input_value = 1
```

Some nodes support convars as input. Their names should start with `@` symbol:

```kv3
type = "action_choose_bomb_site_area"
input = "@mp_guardian_target_site"
output = "BombSiteArea"
```

## Bot Configuration

These parameters define general bot reaction and combat behavior for every bot skill ( *low, fair, normal, tough, hard, very_hard, expert, elite, default* ), like a botprofile.db.

Default format is:

```kv3
<!-- kv3 encoding:text:version{e21c7f3c-8a33-41c5-9977-a76d3a32aa0d} format:generic:version{7412167c-06e9-4698-aff2-e63eb59037e7} -->
{
	<skill level>
	{
		<Variables from table below>
		attack = <Attack table>
	}
}
```

### List of Parameters

| Variable | Description |
| --- | --- |
| `aim_target_acquisition_lerp_time` |  |
| `aim_target_acquisition_lerp_time_deviation` |  |
| `aim_target_acquisition_angle_penalty` |  |
| `aim_target_acquisition_angle_penalty_deviation` |  |
| `aim_target_acquisition_angle_penalty_reduction_ratio` |  |
| `aim_target_acquisition_angle_tolerance` |  |
| `aim_target_acquisition_angle_lerp_bias` |  |
| `aim_target_tracking_lerp_time` |  |
| `aim_target_tracking_lerp_time_deviation` |  |
| `aim_target_tracking_focus_interval` |  |
| `aim_target_tracking_focus_interval_deviation` |  |
| `aim_target_tracking_angle_lerp_bias` |  |
| `aim_new_target_angle_tolerance` |  |
| `aim_max_duration` |  |
| `aim_max_duration_deviation` |  |
| `aim_punch_angle_reaction_chance` |  |
| `look_around_awareness_yaw_range` | Max angle to horizontal rotate viewcamera from this viewpoint. |
| `look_around_awareness_pitch_range` | Max angle to vertical rotate viewcamera from this viewpoint. |
| `look_around_focus_interval` | Delay between next viewcamera rotation. |
| `look_around_focus_interval_deviation` |  |
| `look_around_lerp_time` | Time to rotate viewcamera to next position. |
| `look_around_lerp_time_deviation` |  |
| `look_around_lerp_bias` | Smooths viewcamera movement. |
| `reaction_time` | Delay before reaction on event. |
| `combat_crouch_chance` |  |
| `combat_dodge_command_duration` |  |
| `combat_dodge_command_duration_deviation` |  |

### Attack Table

Attack table defines handling of different weapon types.

Example:

```kv3
attack =
[
	// duration, duration deviation, cadence, cooldown, cooldown deviation

	// KNIFE						PISTOL							SUBMACHINEGUN
	[ -1.0, -1.0, -1.0, -1.0, -1.0 ],[ 0.95, 0.25, 0.5, 0.15, 0.05 ],[ 0.42, 0.07, 0.0, 0.15, 0.05 ],
	// RIFLE						SHOTGUN							SNIPER_RIFLE
	[ 0.22, 0.07, 0.0, 0.45, 0.15 ],[ 0.3, 0.0, 0.0, 0.95, 0.25 ],[ 0.22, 0.07, 0.0, 2.0, 0.0 ],
	// MACHINEGUN					C4								TASER
	[ 0.75, 0.15, 0.0, 0.3, 0.1 ],[ -1.0, -1.0, -1.0, -1.0, -1.0 ],	[ -1.0, -1.0, -1.0, -1.0, -1.0 ],
	// GRENADE						EQUIPMENT						STACKABLEITEM
	[ -1.0, -1.0, -1.0, -1.0, -1.0 ],[ -1.0, -1.0, -1.0, -1.0, -1.0 ],[ -1.0, -1.0, -1.0, -1.0, -1.0 ],
	// FISTS						BREACHCHARGE					BUMPMINE
	[ -1.0, -1.0, -1.0, -1.0, -1.0 ],[ -1.0, -1.0, -1.0, -1.0, -1.0 ],[ -1.0, -1.0, -1.0, -1.0, -1.0 ],
	// TABLET						MELEE							SHIELD
	[ -1.0, -1.0, -1.0, -1.0, -1.0 ],[ -1.0, -1.0, -1.0, -1.0, -1.0 ],[ -1.0, -1.0, -1.0, -1.0, -1.0 ],
	// WEAPONTYPE_ZONE_REPULSOR		UNKNOWN
	[ -1.0, -1.0, -1.0, -1.0, -1.0 ],[ -1.0, -1.0, -1.0, -1.0, -1.0 ]
]
```

## Nodes

This is a list of all nodes on November 9, 2021.

Every node has a `type` parameter which determines its functionality and which other parameters it considers. Parameters might have a default value, in which case it is optional to specify them; if a parameter doesn't have a default value and if it is not specified, there will be an error message in the console.

Most nodes can have the following parameters that are omitted in the following lists:

* `child` - Supported by [#Decorators](https://developer.valvesoftware.com/wiki/Counter-Strike:_Global_Offensive/Bot_Behavior_Trees#Decorators) and [#Conditions](https://developer.valvesoftware.com/wiki/Counter-Strike:_Global_Offensive/Bot_Behavior_Trees#Conditions). Its value should be another node which will or will not be executed, depending on node type and context. By default most decorators execute their child function automatically, unless otherwise specified.
* `children` - Supported by [#Combinators](https://developer.valvesoftware.com/wiki/Counter-Strike:_Global_Offensive/Bot_Behavior_Trees#Combinators) (Except `subtree`!). Its value should be an array of nodes, similar to `child`.
* `negated` - Supported by [#Decorators](https://developer.valvesoftware.com/wiki/Counter-Strike:_Global_Offensive/Bot_Behavior_Trees#Decorators) and [#Conditions](https://developer.valvesoftware.com/wiki/Counter-Strike:_Global_Offensive/Bot_Behavior_Trees#Conditions). Set to 1 to invert its return value (success or not), for example a node of the type `condition_is_empty` will succeed if something does not exist; If this node has the parameter `negated = 1`, it will instead succeed if something does exist.

* Complete node parameters and descriptions, check for inaccuracies.
* Define variable types for parameters.
* Explain all parameters.

### Combinators

| Type | Parameters | Description |
| --- | --- | --- |
| `parallel` | `int_flag? succeed_after_first` | Executes all child functions in one script tick until a child function returns false condition or until all child functions return true condition. "succeed_after_first" ends execution after first child function returns true condition. |
| `selector` |  | Executes child functions as sequence until meeting child with true condition. |
| `sequencer` |  | Executes child functions as sequence until meeting child with false condition. |
| `subtree` | `string file, string name, array params` | Executes behavior tree from file. "params" array goes in "key", "value" format in brackets. e.g.`<br>{<br>key = "ThrowUtility"<br>value = 1<br>},` |

### Decorators

| Type | Parameters | Description |
| --- | --- | --- |
| `decorator_bot_service` | `array memory_to_expire(variable? domain (GroupID or AllBots), flag key (ShortTermAttackMemory, ShortTermDamageMemory, ShortTermAreaDamageMemory, ShortTermInvestigateMemory, LongTermMemory, DamageThroughSmokeMemory, Threats), int time, int distance), array tagged_entities_to_expire, int_flag? basic_chatter_enable, vector? input_chatter_enemies, int chatter_outnumbered_threshold` | Kinda main bot behavior function? Usually contains all subtree routines. |
| `decorator_buy_service` | `array output` | Returns array of items that bot will buy. |
| `decorator_dec_global_counter` | `variable input_name` | Decreases input variable by 1. |
| `decorator_find_utility_strat` | `vector input_location, int distance_threshold, vector output_location, vector output_angles, string output_weapon` | Unused. |
| `decorator_game_event` |  | Warning: Release Notes for 21/10/2021 say about it but it doesn't exist in code? |
| `decorator_hiding_spot_service` | `variable? domain (GroupID or AllBots), vector output_hiding_spot, int distance_threshold, int expiration_time` | Keeps track of visible hiding spots. Used in conjunction with `action_move_to` to make a bot check hiding spots as they move throughout the level. Note: Also keeps track of checked hiding spots in `domain`. Bots sharing the same domain will not check hiding spots for some time if another bot has already checked them. |
| `decorator_invert` |  | Unused. Valve scripts usually use `negated = 1` flag in node parameters. However, `action` nodes don't support `negated`, so this node can be used as a workaround. |
| `decorator_maybe` | `float chance` | Executes child function with specified `chance` (1 - 100%, 0.7 - 70% etc). |
| `decorator_memory` | `vector? input, memory? output, string output_domain` | Saves entities in the `input` array to `output` array. |
| `decorator_need_healing` | `int health_threshold` | Executes child function if bot health is lower than `health_threshold`. |
| `decorator_picker_blocked_by_smoke` | `vector? input, int distance_threshold` | Removes entities from the `input` array that are not covered by smokes. |
| `decorator_picker_dedup` | `vector? input, memory? against, int distance_threshold` | Removes entities from the `input` array that are within `distance_threshold` to entities in `against` array. |
| `decorator_picker_grenade_type` | `array input, array types (EXPLOSIVE, FLASH, FIRE, DECOY, SMOKE, SENSOR, SNOWBALL)` | Removes grenade entities from the `input` array that are not in `types` array. |
| `decorator_picker_max_score` | `array input` | Picks the first entity in the `input` array. By default entities are sorted by the order they appear on the server. Note: `decorator_ranker_dist` can be used before this node to pick the closest entity instead. |
| `decorator_picker_nearby` | `array input, int cutoff_distance` | Removes entities from the `input` array that are beyond the `cutoff_distance`. |
| `decorator_picker_random_by_distance` | `array input, int distance_min, int distance_max` | Removes entities from the `input` array based on the distance distribution. Entities closer to `distance_min` are less likely to get removed, while entities closer to `distance_max` are more likely to get removed. |
| `decorator_picker_reaction_time` | `variable? input_domain (GroupID or AllBots), memory? input, vector? output` | Executes child function after delay, that depends of bot skill reaction time? |
| `decorator_picker_visible` | `array input, int_flag? check_fov` | Removes obscured entities from `input` array. Will check bot FOV only, unless `check_fov` is set to 0. |
| `decorator_picker_weight_as_distance` | `array input` | Removes the entities whose distance to the bot running the tree is greater than the entities "weight". "weight" is an internal notion mostly used for hearing sounds. It should only be used when sensing "NOISE". |
| `decorator_random_approach_point` | `vector output` | Returns a random visible point in navmesh that's ideally an "entrance" to the area the bot is currently in. Tip: Can be used to make a bot look around randomly, as seen in `"...\modules\bt_look_around.kv3"`. |
| `decorator_random_int` | `int min, int max, int output` | Returns a random int in the range of `min` to `max`. |
| `decorator_ranker_dist` | `array input` | Sorts entities in the `input` array based on distance. |
| `decorator_remove` | `variable? input_domain (GroupID or AllBots), memory? input, array? remove` | Removes selected entities from `input` memory. |
| `decorator_remove_key` | `variable? input` | Removes `input` variable from script scope. |
| `decorator_repeat` |  | Executes child function in loop. Stops looping if child function fails. |
| `decorator_route_service` | `array config (array routes, array strategies), vector? output_waypoint, string output_waypoint_name, string output_domain` | Unused. |
| `decorator_run_once` | `int max_attempts = 1, variable? domain (e.g. domain = "'CoordinatedBuy'")` | Executes child function limited amount of times. `domain` can be set to make only one bot run it. |
| `decorator_sensor` | `flag entity_type_filter (ALL, PLAYERS, HUMAN_PLAYERS, NOISE, DAMAGE, AREA_DAMAGE, CLASSNAME, GRENADE), function? shape(flag type (sensor_shape_fov, sensor_shape_sphere), int radius), flag team_filter (ANY, CT, TERRORIST, SAME, OPPOSITE, ENEMY), int_flag orphan_only, int_flag priority, string class_name, vector? output` | Returns entities detected by sensor. Bug:When sensing grenades with `team_filter` set to "ENEMY" it incorrectly returns terrorist grenades, regardless of team the bot is on. "OPPOSITE" filter can be used as a workaround. |
| `decorator_set_barrier` | `domain input_domain, variable input_name, navzone? input_location` | Unused. |
| `decorator_set_reaction_time` | `array? input` | Executes child function after delay, that depends of bot skill reaction time? |
| `decorator_succeed` |  | Node succeeds (returns true condition) even if child function failed. |
| `decorator_tag_entity` | `array input, array output, flag operation_type (BT_DECORATOR_TAG_ENTITY_CLEAR, BT_DECORATOR_TAG_ENTITY_SET), int expiration_time` | Adds or removes the first entity in `input` array to `output` array for specified amount of seconds. `input` entity will be tagged as long as the child function is being executed. |
| `decorator_tag_threshold` | `array entity_input, array tagged_entities_input, int amount, flag check_type (BT_DECORATOR_TAG_THRESHOLD_AT_MOST, BT_DECORATOR_TAG_THRESHOLD_AT_LEAST)` | Compares entities in `entity_input` against entities in `tagged_entities_input` using `check_type`. If it passes, executes child function. (If at least/most `x` entities from `entity_input` are in `tagged_entities_input`, execute child function) |
| `decorator_token_service` | `variable? domain, string output_token_name, string output_token_domain, function config(array tokens, array assignments)` | In  [Guardian](https://developer.valvesoftware.com/wiki/Counter-Strike:_Global_Offensive/Game_Modes/Guardian) Mode: defines bot GroupID, then executes child functions. |
| `decorator_try_lock` | `variable? domain (e.g. domain = "'DefuseIfCovered'")` | Locks the `domain` for the duration of executing the child function, meaning only one bot at a time will be executing this. |
| `decorator_wait_success` | `int timeout` | Waits for child to return true or finish executing. If child never returns true, stops waiting after `timeout` seconds. |

### Conditions

| Type | Parameters | Description |
| --- | --- | --- |
| `condition_barrier` | `domain input_domain, variable input_name, navzone? input_location` | Unused. |
| `condition_distance_less` | `vector input, int distance_threshold_min, int distance_threshold_max` | Returns true, if distance to `input` position is less than somewhere between the `distance_threshold_min` and `distance_threshold_max`. |
| `condition_has_parachute` |  | Returns true, if bot has parachute in inventory. |
| `condition_inactive` | `array input(memory? key), int round_start_threshold_seconds, int sensor_inactivity_threshold_seconds` | Returns true, if bot doesn't have any memory and sensor input within timing. |
| `condition_is_airborne` |  | Returns true, if bot is mid-air. |
| `condition_is_at_bomb_site` |  | Returns true, if bot is at bombsite zone. |
| `condition_is_empty` | `int_flag? global, any input` | Returns true, if `input` variable is empty or doesn't exist. |
| `condition_is_equal` | `any source, any destination` | Returns true, if source variable is equal to `destination` input. |
| `condition_is_greater` | `any source, any destination` | Unused. Returns true, if source variable is greater than `destination` input. |
| `condition_is_greater_equal` | `any source, any destination` | Unused. Returns true, if source variable is equal or greater than `destination` input. |
| `condition_is_inv_slot_empty` | `flag slot (KNIFE, PISTOL, RIFLE, GRENADES)` | Returns true, if input equipment slot is empty. |
| `condition_is_less` | `any source, any destination` | Unused. Returns true, if source variable is less than `destination` input. |
| `condition_is_less_equal` | `any source, any destination` | Unused. Returns true, if source variable is equal or less than `destination` input. |
| `condition_is_reloading` |  | Unused. Returns true, if active weapon is in reloading state. |
| `condition_is_weapon_equipped` | `string weapon` | Returns true, if bot has active weapon with `weapon` classname. |
| `condition_is_weapon_suitable` | `vector input, string weapon` | Unused. Returns true, if weapon with `weapon` classname is suitable at the range to the `input` entity. Snipers are not considered suitable below 160.0 units, while shotguns are not considered suitable past 600.0 units. Bug:Works exactly the same as `condition_is_weapon_equipped`.[*confirm*] |
| `condition_out_of_ammo` |  | Returns true, if active weapon is out of ammo. |
| `condition_owns_item` | `string item, array items_one_of` | Returns true, if bot has item with `input` classname. |

### Actions

| Type | Parameters | Description |
| --- | --- | --- |
| `action_acquire_items` | `array items, int_flag? remove_all_items` | Equips bot with items from array, e.g. `{ type = "action_acquire_items" items = [ "weapon_awp" ] }`. |
| `action_aim` | `vector input, int_flag? acquire_only, flag? ready` | Rotates bot towards input point. Uses aim penalties set in the bot config. Can overshoot the target. Forces the bot to scope with scoped weapons. Note: `acquire_only` should be set to 1 if you don't intend to track your target. Warning: Bot will never unscope unless they switch weapons. Equipping the same weapon as the one bot is currently holding will also reset the scope. |
| `action_aim_projectile` | `vector input, vector output` | Calculates angles for throwing at input position? Bug:Doesn't actually take the grenade trajectory into account. |
| `action_assign_guardian_loadout` | `string input_token_name, array assignments(string token, array loadout(array items, array wave_numbers, int wave_numbers_min, int wave_numbers_max, int weight))` | In  [Guardian](https://developer.valvesoftware.com/wiki/Counter-Strike:_Global_Offensive/Game_Modes/Guardian) mode: Chooses bot spawn loadout. |
| `action_attack` | `vector input, flag? output (e.g. output = "Attacking"), flag? ready (e.g. ready = "AimReady")` | Forces bot to fire. Uses spray duration settings from bot config. Note: `ready` flag usually should be controlled automatically with `action_aim` node. |
| `action_buy` |  | Bot buys random weapons. |
| `action_choose_bomb_site_area` | `int input, navzone? output` | Gets bombzone nav position from index. Supports convars. |
| `action_choose_guardian_bomb_plant_location` | `vector? output` | Chooses plant position in navmesh? Guardian mode only? |
| `action_choose_random_waypoint` | `navzone? input, vector output` | Chooses a random navmesh tile from the input navzones and returns its center as a vector position. |
| `action_choose_random_waypoint_within_radius` | `vector origin, vector output, float radius` | Chooses a random navmesh tile within specified origin and radius and returns a random point within it as a vector position. |
| `action_choose_team_spawn_area` | `navzone? output` | Gets all navzones with spawnpoints? |
| `action_combat_positioning` | `vector input, flag? is_attacking` | Bot side steps to dodge attacks or closes distance on the enemy. Uses settings from the bot config. Note: `is_attacking` flag usually should be controlled automatically with `action_attack` node. |
| `action_commit_suicide` |  | Kills bot. |
| `action_compare_global_counter` | `variable? input_name (e.g. input_name = "'Test'"), int input_value` | Compares value from variable `input_name` to `input_value`. |
| `action_coordinated_buy` | `flag team_filter (ANY, CT, TERRORIST, SAME, OPPOSITE, ENEMY),<br>int save_threshold,<br>flag? id_no_purchase (e.g. id_no_purchase = "DidNotPurchase"),<br>array purchases(array items, string id)` | Forces all of the bots that match the `team_filter` to buy items from `purchases` array and assigns appropriate `id` to them. Node will return false and be skipped if there's not enough bots in the specified team to fulfill all `purchases`. Bots that do not make a purchase are assigned with `id_no_purchase`. You can check what `id` bots are assigned with by using `condition_is_empty`. Warning: One bot using this node will make all of the bots that match the specified `team_filter` make purchases! Use in conjunction with `decorator_run_once` and `domain` set to something.  Bug:Bots that did not match the `team_filter` are still assigned "id_no_purchase" erroneously. Bug:Bots further down the `purchases` array inherit items to purchase from bots before them. See [#Coordinated Buy (Alternative Buying Method)](https://developer.valvesoftware.com/wiki/Counter-Strike:_Global_Offensive/Bot_Behavior_Trees#Coordinated_Buy_(Alternative_Buying_Method)) |
| `action_crouch` |  | Forces bot to crouch. |
| `action_custom_buy` | `array item_aliases` | Unused. |
| `action_drop_active_weapon` |  | Unused. Forces bot to drop active weapon. |
| `action_equip_item` | `string item, array items_one_of` | Forces bot to select item with classname from input. |
| `action_equip_weapon` | `string weapon (classname or BEST)` | Force bot to select item with classname from input or "best" weapon in inventory. |
| `action_flee_area_damage` | `vector? input, vector output, int max_search_range, int threat_min_keep_distance` | Returns safe spot from that position within search radius. |
| `action_hide` | `float max_range, vector output` | Unused. Returns a random hiding spot within search radius. Warning: Does NOT check if it's already occupied! |
| `action_inspect_current_weapon` |  | Unused. Forces bot to play inspect animation. |
| `action_jump` |  | Forces bot to jump. |
| `action_look_at` | `vector input_angles, vector input_location` | Rotates the bot to specified `input_[angle](https://developer.valvesoftware.com/wiki/Angle)`, like [setang](https://developer.valvesoftware.com/wiki/Setang). If omitted, rotates the bot so that it looks to the coordinates `input_location`. Otherwise, an error occurs. |
| `action_move_to` | `vector destination,<br>flag movement_type (BT_ACTION_MOVETO_RUN, BT_ACTION_MOVETO_WALK),<br>flag route_type (BT_ACTION_MOVETO_FASTEST_ROUTE,BT_ACTION_MOVETO_SAFEST_ROUTE),<br>vector? hiding_spot,<br>vector? threat,<br>int damaging_areas_penalty_cost,<br>int nearest_area_distance_threshold,<br>int hiding_spot_check_distance_threshold,<br>int arrival_epsilon,<br>float additional_arrival_epsilon_2d,<br>int_flag? auto_look_adjust` | Forces bot to move at destination point. Bug:Move type will reset to running after jumping. Bug:When teammate collision is on, bots will not try to repath around their teammates if they block their way. Instead they'll constantly try to path through their teammate until they move out of their way. |
| `action_parachute_positioning` |  | Forces bot to move diagonally ignoring the navmesh. Changes direction every few seconds. |
| `action_pull_trigger` | `int ratio` | Forces bot primary attack. |
| `action_reload` |  | Forces bot to reload weapon. |
| `action_say` | `string phrase, flag? high_priority` | Forces bot to say radio command phrase. List of phrases is located in `botchatter.db` |
| `action_secondary_attack` |  | Unused. Forces bot secondary attack. |
| `action_select_areas_within_radius` | `vector input, float radius, navzone? output` | Returns navzones within specified origin and radius? |
| `action_set_global_counter` | `variable? input_name, int input_value` | Sets input value to variable `input_name`. |
| `action_set_global_flag` | `variable? name, int expiration_time_min, int expiration_time_max` | Sets global variable `name` to 1 for specified time? |
| `action_set_value_float` | `variable? key, float value` | Sets float value to variable `key`. |
| `action_set_value_vector` | `variable? key, vector value` | Sets vector value to variable `key`. |
| `action_standup` |  | Unused. Forces bot to uncrouch. |
| `action_teleport` | `vector destination` | Teleports bot to destination position. |
| `action_use` |  | Forces bot "+use" |
| `action_wait` | `float wait_time_min, float wait_time_max` | Freezes bot AI and script execution for defined amount of time. |

### Reserved Variables

Those variables are defined in game code. They can be used to get some information about game mode and bot and as conditions.

| Variable | Description |
| --- | --- |
| `int NumberOfTerrorists` | Number of players in T team. |
| `int NumberOfAliveTerrorists` | Number of alive players in T team. |
| `int NumberOfCounterTerrorists` | Number of players in CT team. |
| `int NumberOfAliveCounterTerrorists` | Number of alive players in CT team. |
| `int GuardianWaveNumber` | Wave number in  [Guardian](https://developer.valvesoftware.com/wiki/Counter-Strike:_Global_Offensive/Game_Modes/Guardian) Mode. |
| `int AccountBalance` | Amount of player money. |
| `float? BlindnessPercentage` | Amount of blindness applied by flash grenade. |
| `??? BombIsBeingDefused` | Returns ??? when bomb is being defused. |
| `variable? LastCoopSpawnPointName` | Targetname of last spawn point spawned that bot in  [Co-op Strike](https://developer.valvesoftware.com/wiki/Counter-Strike:_Global_Offensive/Game_Modes/Co-op_Strike). |
| `Vector LastCoopSpawnPointLocation` | Origin point of last spawn point spawned that bot in  [Co-op Strike](https://developer.valvesoftware.com/wiki/Counter-Strike:_Global_Offensive/Game_Modes/Co-op_Strike). |
| `int AmmoCount/weapon_name` | Remained amount of ammo in weapon with classname "weapon_name" (clip + reserve). |
| `int AmmoCount/current` | Remained amount of ammo in active weapon (clip + reserve). |

