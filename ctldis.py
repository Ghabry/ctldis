# CTL Assembler/Disassembler
# First Release: 2009-12-07 (by Rob)
# Last Update: 2017-04-25

from itertools import chain
from array import array
import sys
from os import path
from shutil import copyfile
from collections import defaultdict
import sys

if len(sys.argv) > 1:
    base_name = sys.argv[1].upper()
else:
    base_name = "B101"

if len(sys.argv) > 2:
    arg = sys.argv[2]

    try:
        MODE = int(arg)
    except ValueError:
        if arg.lower().startswith("a"):
            MODE = 0
        elif arg.lower().startswith("d"):
            MODE = 1
        else:
            raise ValueError("Bad mode: Must be a or d")
else:
    MODE = 1 # 0 == assemble, 1 == disassemble

original_file_name   = base_name+"_orig.CTL"
disassembled_file_name = base_name+".txt"
assembled_file_name  = base_name+".CTL"


opLengths = {   0x00:1, 0x01:0, 0x02:0, 0x03:0, 0x04:0, 0x05:0,
                0x06:0, 0x07:0, 0x08:0, 0x09:1, 0x0a:0, 0x0b:1,
                0x0c:1, 0x0d:1, 0x0e:1, 0x0f:1, 0x10:1, 0x11:1,
                0x12:0, 0x13:0, 0x14:2, 0x15:0, 0x16:0, 0x17:1,
                0x18:1, 0x19:0, 0x1a:0, 0x1b:1, 0x1c:1, 0x1d:0,
                0x1e:2, 0x1f:2, 0x20:2, 0x21:2, 0x22:1, 0x23:2,
                0x24:2, 0x25:2, 0x26:0, 0x27:0, 0x28:1, 0x29:1,
                0x2a:1, 0x2b:0, 0x2c:1, 0x2d:1, 0x2e:1, 0x2f:1,
                0x30:1, 0x31:1, 0x32:1, 0x33:1, 0x34:1, 0x35:1,
                0x36:1, 0x37:1, 0x38:1, 0x39:1, 0x3a:1, 0x3b:1,
                0x3c:2, 0x3d:1, 0x3e:2, 0x3f:1, 0x40:1, 0x41:1,
                0x42:2, 0x43:0, 0x44:0, 0x45:0, 0x46:1, 0x47:0,
                0x48:0, 0x49:0, 0x4a:0, 0x4b:0, 0x4c:0, 0x4d:0,
                0x4e:1, 0x4f:0, 0x50:0, 0x51:0, 0x52:1, 0x53:1,
                0x54:1, 0x55:0, 0x56:0, 0x57:0, 0x58:0, 0x59:0,
                0x5a:0, 0x5b:0, 0x5c:0, 0x5d:0, 0x5e:0, 0x5f:0,
                0x60:0, 0x61:0, 0x62:0, 0x63:0, 0x64:0, 0x65:0,
                0x66:0, 0x67:0, 0x68:1, 0x69:1, 0x6a:1, 0x6b:1,
                0x6c:0, 0x6d:1, 0x6e:1, 0x6f:1, 0x70:1, 0x71:0,
                0x72:0, 0x73:0, 0x74:1, 0x75:1, 0x76:0, 0x77:0,
                0x78:0, 0x79:0, 0x7a:1, 0x7b:1, 0x7c:1, 0x7d:1,
                0x7e:0, 0x7f:0, 0x80:0, 0x81:1, 0x82:1, 0x83:0,
                0x84:0, 0x85:0, 0x86:0, 0x87:1, 0x88:0, 0x89:0,
                0x8a:1, 0x8b:3, 0x8c:2, 0x8d:1, 0x8e:0, 0x8f:0,
                0x90:1, 0x91:0, 0x92:0, 0x93:1, 0x94:1, 0x95:1,
                0x96:0, 0x97:1, 0x98:3, 0x99:3, 0x9a:1, 0x9b:2,
                0x9c:0, 0x9d:1, 0x9e:2, 0x9f:0, 0xa0:3, 0xa1:1,
                0xa2:3, 0xa3:1, 0xa4:1, 0xa5:1, 0xa6:2, 0xa7:2,
                0xa8:2, 0xa9:2, 0xaa:3, 0xab:3, 0xac:3, 0xad:2,
                0xae:1, 0xaf:2, 0xb0:1, 0xb1:0, 0xb2:0, 0xb3:1,
                0xb4:1, 0xb5:3, 0xb6:2, 0xb7:1, 0xb8:0, 0xb9:0,
                0xba:1, 0xbb:0, 0xbc:0, 0xbd:1, 0xbe:0, 0xbf:4,
                0xc0:1, 0xc1:1, 0xc2:1, 0xc3:1, 0xc4:1, 0xc5:1,
                0xc6:0, 0xc7:0, 0xc8:0, 0xc9:0, 0xca:0, 0xcb:0,
                0xcc:0, 0xcd:1, 0xce:1, 0xcf:1, 0xd0:1, 0xd1:1,
                0xd2:0, 0xd3:1, 0xd4:0, 0xd5:2, 0xd6:1, 0xd7:1,
                0xd8:1, 0xd9:1, 0xda:3, 0xdb:1, 0xdc:1, 0xdd:2,
                0xde:2, 0xdf:2, 0xe0:2, 0xe1:2, 0xe2:1, 0xe3:0,
                0xe4:1, 0xe5:2, 0xe6:0, 0xe7:2, 0xe8:0, 0xe9:2,
                0xea:0, 0xeb:2, 0xec:3, 0xed:0, 0xee:1, 0xef:0,
                0xf0:1 }

opLengths_ext = { 0x00: 1 }

opNames = {
    0x00:"init_unit",
    0x01:"wait_for_deploy",
    0x02:"reset_call_stack",
    0x03:"restore_ip",
    0x04:"save_ip",
    0x05:"do",
    0x06:"always",
    0x07:"while",
    0x08:"whilenot",
    0x09:"for",
    0x0a:"next",
    0x0b:"goto",
    0x0c:"set_return_func",
    0x0d:"set_return_func_iftrue",
    0x0e:"set_return_func_with_restart",
    0x0f:"set_return_func_with_restart_iftrue",
    0x10:"set_return_func_iffalse",
    0x11:"call",
    0x12:"return",
    0x13:"return_from_event_handler",

    0x15:"sleep",
    0x16:"sleep_iftrue",
    0x17:"skip_iftrue",
    0x18:"set_timer",
    0x19:"test_waiting_for_timer",
    0x1a:"wait_for_timer",

    0x1b:"set_x_i",
    0x1c:"add_x_i",
    0x1d:"test_x_eq_0",

    0x1e:"set_unit_r_i",
    0x1f:"add_unit_r_i",
    0x20:"test_unit_r_eq_i",
    0x21:"test_unit_r_eq_r",
    0x22:"set_unit_r_random1to10",

    0x23:"set_global_r_i",
    0x24:"add_global_r_i",
    0x25:"test_global_r_eq_i",
    #0x26 takes other unit uuid
    #0x27 restores ip
    0x28:"move_to_node",
    0x29:"retreat_to_node",

    0x2a:"add_waypoint",
    #0x2b:"block_movement",
    0x2c:"wait_unit_flag1_clear",
    0x2d:"wait_unit_flag1_set",
    0x2e:"test_unit_flag1",
    0x2f:"set_unit_flag1",
    0x30:"clear_unit_flag1",

    0x31:"wait_unit_flag2_clear",
    0x32:"wait_unit_flag2_set",
    0x33:"test_unit_flag2",
    0x34:"set_unit_flag2",
    0x35:"clear_unit_flag2",

    0x36:"wait_unit_flag3_clear",
    0x37:"wait_unit_flag3_set",
    0x38:"test_unit_flag3",

    0x39:"set_ctrl_flag",
    0x3a:"clear_ctrl_flag",
    0x3b:"test_ctrl_flag",

    0x3d:"set_event_handler",
    0x3e:"set_callback",
    0x3f:"set_label",

    0x40:"store_unit_by_label",
    0x41:"test_label_exists",
    0x42:"send_event_to_self_if_label_exists",

    0x44:"test_can_fight_and_sender_does_not_retreat",

    0x4c:"nop_4c",

    0x4e:"goto_iftrue",

    0x52:"move_rand_in_radius",

    0x53:"init_teleport",
    0x54:"teleport_to",
    0x55:"teleport_to2",

    0x58:"test_target_in_charge_range",
    0x59:"charge_and_send_event_to_target",
    0x5a:"charge",
    0x5b:"retreat_from_target",
    0x5c:"retreat",
    0x5d:"retreat_inverted",
    0x65:"hold",

    0x69:"send_event_to_self",
    0x6a:"send_event_to_self_iftrue",
    0x6b:"send_event_to_self_iffalse",
    0x6d:"set_event_id",
    0x6e:"broadcast_event_to_friends",
    0x6f:"broadcast_event_to_enemies",
    0x70:"send_event_to_stored_unit",
    0x71:"teleport_to3",
    0x72:"get_event",
    0x73:"test_more_events",
    0x74:"on_event",
    0x75:"end_event",
    0x76:"iftrue",
    0x77:"iffalse",
    0x78:"else",
    0x79:"endif",

    0x82:"test_unit_flag1_and_close_combat",

    0x86:"test_unit_can_fight",

    0x8d:"test_missile_weapon",

    0x90:"nop_90",
    0x91:"nop_91",
    0x92:"nop_92",

    0x93:"test_magic_points_leq_i",
    0x94:"add_magic_points",

    0x97:"init_teleport_spell",
    0x98:"cast_spell_on_other",
    0x99:"cast_spell_on_self",
    0x9d:"add_spell",

    0x9f:"test_unit_can_fight_2",

    0xa2:"find_enemy_uflag_attrib",
    0xa3:"find_enemy_visible",
    0xa4:"find_enemy_simple",
    0xa5:"find_enemy_simple_visible",
    0xa6:"find_enemy_unittype",
    0xa7:"find_enemy_unittype_2",
    0xa8:"find_enemy_nth",
    0xa9:"find_enemy_nth_visble",
    0xaa:"find_enemy_unittype_nth",
    0xab:"find_enemy_unittype_nth_2",
    0xac:"find_enemy_distance_uflag",

    0xae:"play_self",
    0xaf:"play_other",

    0xb2:"test_self_afraid",
    0xb3:"test_self_at_node",
    0xb4:"test_any_at_node",
    0xb5:"test_any_at_node2",
    0xb6:"send_event_to_unit_with_label",
    0xb7:"send_event_to_source",
    0xb8:"test_event_from_enemy",
    0xb9:"test_event_from_close_combat",
    0xba:"test_unit_class",
    0xbd:"set_unit_class",
    0xbf:"spawn_unit",

    0xc0:"test_members_alive_geq_i",
    0xc1:"test_label_eq_i",
    0xc2:"test_event_source_eq_i",
    0xc3:"test_game_status",
    0xc4:"test_objective",

    0xc7:"clear_event_queue",
    0xc9:"clear_last_event",

    0xcd:"test_attribute_set",
    0xce:"set_attribute",
    0xcf:"clear_attribute",

    0xd0:"find_and_collect_item",
    0xd1:"event_test_distance_and_collect_this_item",
    0xd2:"event_test_unit_collects_this_item",
    0xd3:"event_test_item",
    0xd4:"event_test_any_friend_collects_this_item",

    0xd5:"test_units_alive_le_i",
    0xd7:"test_boss_defeated",
    0xd8:"test_other_unit_alive",
    0xd9:"test_user_action",
    0xda:"ui_indicate",
    0xdd:"set_unit_r_direction",
    0xde:"test_unit_at_node",
    0xdf:"test_unit_attacking",
    0xe0:"test_other_unit_flag2",
    0xe1:"test_other_unit_flag3",

    0xe2:"test_unit_selected",
    0xe3:"test_any_spell_selected",

    0xe6:"test_mapmode",
    0xe7:"test_unit_at_node2",

    0xea:"test_sound_playing",
    0xeb:"test_other_unit_flag1",
    0xec:"test_other_unit_r_eq_i",
    0xed:"end_mission",
    0xee:"test_event_from_unit",
}

opNames_ext = {
    0x00: "set_deployment_limit"
}

Arg_Unused = 0
Arg_Any = 1
Arg_Function = 2
Arg_Event = 3
Arg_Register = 4
Arg_GlobalRegister = 5
Arg_BtbNode = 6 # Incrementing number of BTB-6000
Arg_BtbNodeId = 7 # Real ID of a BTB-6000 node
Arg_UF1 = 8
Arg_UF2 = 9
Arg_UF3 = 10
Arg_CtrlFlag = 11
Arg_Label = 12
Arg_EndEvent = 13
Arg_Missile = 14
Arg_UnitType = 15
Arg_Item = 16
Arg_MagicFlag = 17
Arg_Attribute = 18
Arg_Voice = 19
Arg_Unit = 20 # Incrementing number of Enemy+Friends
Arg_Alignment = 21
Arg_Spawn = 22
Arg_GameStatus = 23
Arg_Objective = 24
Arg_Boss = 25
Arg_UnitId = 26

opTypes = {
    0x00: [Arg_Unused],
    0x09: [Arg_Any],
    0x0b: [Arg_Function],
    0x0c: [Arg_Function],
    0x0d: [Arg_Function],
    0x0e: [Arg_Function],
    0x0f: [Arg_Function],
    0x10: [Arg_Function],
    0x11: [Arg_Function],
    0x14: [Arg_Any, Arg_Event],
    0x17: [Arg_Any],
    0x18: [Arg_Any],
    0x1b: [Arg_Any],
    0x1c: [Arg_Any],
    0x1e: [Arg_Register, Arg_Any],
    0x1f: [Arg_Register, Arg_Any],
    0x20: [Arg_Register, Arg_Any],
    0x21: [Arg_Register, Arg_Register],
    0x22: [Arg_Register],
    0x23: [Arg_GlobalRegister, Arg_Any],
    0x24: [Arg_GlobalRegister, Arg_Any],
    0x25: [Arg_GlobalRegister, Arg_Any],
    0x28: [Arg_BtbNode],
    0x29: [Arg_BtbNode],
    0x2a: [Arg_BtbNodeId],
    0x2c: [Arg_UF1],
    0x2d: [Arg_UF1],
    0x2e: [Arg_UF1],
    0x2f: [Arg_UF1],
    0x30: [Arg_UF1],
    0x31: [Arg_UF2],
    0x32: [Arg_UF2],
    0x33: [Arg_UF2],
    0x34: [Arg_UF2],
    0x35: [Arg_UF2],
    0x36: [Arg_UF3],
    0x37: [Arg_UF3],
    0x38: [Arg_UF3],
    0x39: [Arg_CtrlFlag],
    0x3a: [Arg_CtrlFlag],
    0x3b: [Arg_CtrlFlag],
    0x3c: [Arg_Any, Arg_Unused],
    0x3d: [Arg_Function],
    0x3e: [Arg_Any, Arg_Any],
    0x3f: [Arg_Label],
    0x40: [Arg_Label],
    0x41: [Arg_Label],
    0x42: [Arg_Event, Arg_Label],
    0x46: [Arg_Event],
    0x4e: [Arg_Function],
    0x52: [Arg_BtbNodeId],
    0x53: [Arg_BtbNode],
    0x54: [Arg_BtbNode],
    0x68: [Arg_Any],
    0x69: [Arg_Event],
    0x6a: [Arg_Event],
    0x6b: [Arg_Event],
    0x6d: [Arg_Event],
    0x6e: [Arg_Event],
    0x6f: [Arg_Event],
    0x70: [Arg_Event],
    0x74: [Arg_Event],
    0x75: [Arg_EndEvent],
    0x7a: [Arg_Unused],
    0x7b: [Arg_Unused],
    0x7c: [Arg_Unused],
    0x7d: [Arg_Unused],
    0x81: [Arg_Any],
    0x82: [Arg_UF1],
    0x87: [Arg_Any],
    0x8a: [Arg_Any],
    0x8b: [Arg_Any]*3,
    0x8c: [Arg_Any]*2,
    0x8d: [Arg_Missile],
    0x90: [Arg_Unused],
    0x93: [Arg_Any],
    0x94: [Arg_Any],
    0x95: [Arg_Any],
    0x97: [Arg_BtbNode],
    0x98: [Arg_Event, Arg_MagicFlag, Arg_Any],
    0x99: [Arg_Event, Arg_MagicFlag, Arg_Any],
    0x9a: [Arg_Unused],
    0x9b: [Arg_Unused]*2,
    0x9d: [Arg_Item],
    0x9e: [Arg_Item, Arg_Any],
    0xa0: [Arg_Unused]*3,
    0xa1: [Arg_Any],
    0xa2: [Arg_Event, Arg_UF1, Arg_Attribute],
    0xa3: [Arg_Event],
    0xa4: [Arg_Event],
    0xa5: [Arg_Event],
    0xa6: [Arg_Event, Arg_UnitType],
    0xa7: [Arg_Event, Arg_UnitType],
    0xa8: [Arg_Event, Arg_Any],
    0xa9: [Arg_Event, Arg_Any],
    0xaa: [Arg_Event, Arg_UnitType, Arg_Any],
    0xab: [Arg_Event, Arg_UnitType, Arg_Any],
    0xac: [Arg_Event, Arg_Any, Arg_UF1],
    0xad: [Arg_Any, Arg_Any],
    0xae: [Arg_Voice],
    0xaf: [Arg_Unit, Arg_Voice],
    0xb0: [Arg_Any],
    0xb3: [Arg_BtbNode],
    0xb4: [Arg_BtbNode],
    0xb5: [Arg_Alignment, Arg_BtbNode, Arg_UF1],
    0xb6: [Arg_Label, Arg_Event],
    0xb7: [Arg_Event],
    0xba: [Arg_UnitType],
    0xbd: [Arg_UnitType],
    0xbf: [Arg_Spawn, Arg_Function, Arg_Any, Arg_Any],
    0xc0: [Arg_Any],
    0xc1: [Arg_Label],
    0xc2: [Arg_Unit],
    0xc3: [Arg_GameStatus],
    0xc4: [Arg_Objective],
    0xc5: [Arg_Any],
    0xcd: [Arg_Attribute],
    0xce: [Arg_Attribute],
    0xcf: [Arg_Attribute],
    0xd0: [Arg_Item],
    0xd1: [Arg_Any],
    0xd3: [Arg_Item],
    0xd5: [Arg_Any, Arg_Alignment],
    0xd6: [Arg_Alignment],
    0xd7: [Arg_Boss],
    0xd8: [Arg_Unit],
    0xd9: [Arg_Any],
    0xda: [Arg_Any]*3,
    0xdb: [Arg_Unit],
    0xdc: [Arg_Unit],
    0xdd: [Arg_Unit, Arg_Register],
    0xde: [Arg_Unit, Arg_BtbNode],
    0xdf: [Arg_Unit, Arg_Unit],
    0xe0: [Arg_Unit, Arg_UF2],
    0xe1: [Arg_Unit, Arg_UF3],
    0xe2: [Arg_Unit],
    0xe4: [Arg_Unit],
    0xe5: [Arg_Unit, Arg_UnitId],
    0xe7: [Arg_Unit, Arg_BtbNode],
    0xe9: [Arg_Unit, Arg_Item],
    0xeb: [Arg_Unit, Arg_UF1],
    0xec: [Arg_Unit, Arg_Register],
    0xee: [Arg_Unit],
    0xf0: [Arg_Unused]
}

class Prettifier:
    unit_flag_1 = {
        0x2000: "Retreat"
    }

    unit_flag_2 = {
        0x2: "Casting",
        0x4: "Shooting"
    }

    unit_flag_3 = {
        0x1000: "MovingToTarget",
        0x2000: "CollectingItem"
    }

    ctrl_flag = {

    }

    magic_flag = {

    }

    attributes = {
        0x1: "WillNeverRoute",
        0x2: "Unknown1",
        0x4: "CauseFear",
        0x8: "CauseTerror",
        0x10: "ElfRacialFlag",
        0x20: "GoblinRacialFlag",
        0x40: "HateGreenskins",
        0x80: "DifficultTerrainFast",
        0x100: "ImmuneToFear",
        0x200: "RegeneratesWounds",
        0x400: "NeverRegroup",
        0x800: "AlwaysPursue",
        0x1000: "EngineOfWar",
        0x2000: "Indestructible",
        0x4000: "Unknown2",
        0x8000: "SufferExtra",
        0x10000: "InflictCasualtyFear",
        0x20000: "Coward",
        0x40000: "DestroyIfRoute",
        0x80000: "Flammable",
        0x100000: "360",
        0x200000: "ContainFanatics",
        0x400000: "WraithsFlag",
        0x800000: "Giant",
        0x1000000: "GoblinFlagTradingPost",
        0x2000000: "ImmuneToMagic",
        0x4000000: "NeverRetreats",
        0x8000000: "NoItemSlots",
        0x10000000: "FanaticsFlag",
        0x20000000: "FearElves",
        0x40000000: "Unknown3",
        0x80000000: "Unknown4"
    }

    event = {
        -1: "No_Event"
    }

    items = {
        1: "Grudgebringer_Sword",
        2: "Skabskrath",
        3: "Runefang",
        4: "Hellfire_Sword",
        5: "Storm_Sword",
        6: "Lighning_Bolt",
        7: "Spelleater_Shield",
        8: "Dragon_Helm",
        9: "Shield_of_Ptolos",
        10: "Enchanted_Shield",
        11: "Heart_of_Woe",
        12: "Potion_of_Strength",
        13: "Horn_of_Urgok",
        14: "Ring_of_Volans",
        15: "Banner_of_Arcane_Warding",
        16: "Banner_of_Wrath",
        17: "Banner_of_Defiance",
        18: "Morks_War_Banner",
        19: "Staff_of_Osiris",
        20: "Wand_of_Jet",
        21: "Book_of_Ashur",
        22: "Bright_Book",
        23: "Ice_Book",
        24: "Waaagh_Book",
        25: "Dark_Book",
        26: "Fireball",
        27: "Sanguine_Swords",
        28: "Blast",
        29: "Burning_Head",
        30: "Conflagration_of_Doom",
        31: "Flamestorm",
        32: "Crimson_Bands",
        33: "Wings_of_Fire",
        34: "Death_Frost",
        35: "Chill_Blast",
        36: "Ice_Shards",
        37: "Wind_of_Cold",
        38: "Shield_of_Cold",
        39: "Hawks_of_Miska",
        40: "Snow_Blizzard",
        41: "Crystal_Cloak",
        42: "Brain_Bursta",
        43: "Gaze_of_Mork",
        44: "Da_Krunch",
        45: "Fists_of_Gork",
        46: "Mork_Save_Uz",
        47: "Ere_We_Go",
        48: "Gaze_Of_Nagash",
        49: "Raise_the_Dead",
        50: "Doombolt",
        51: "Death_Spasm",
        52: "Blade_Wind",
        53: "Arnizipal_Black_Horror",
        54: "Soul_Drain",
        55: "Witch_Flight",
        56: "Dispel_Magic",
        57: "Treasure_Chest_50gc",
        58: "Treasure_Chest_100gc",
        59: "Treasure_Chest_150gc",
        60: "Treasure_Chest_200gc",
        61: "Treasure_Chest_250gc",
        62: "Treasure_Chest_300gc",
    }

    missiles = {
        -1: "No_Missile",
        7: "Short_Bow",
        8: "Normal_Bow",
        9: "Elven Bow",
        10: "Crossbow",
        11: "Pistole",
        12: "Cannon",
        13: "Mortar",
        14: "Steam_Tank",
        15: "Rock_Lobber",
        16: "Ballista",
        17: "Screaming_Skull"
    }

    unit_type = {
        8: "Infantry",
        16: "Cavalry",
        24: "Archer",
        32: "Artillery",
        40: "Wizard",
        48: "Monster",
        56: "Chariot",
        64: "Misc"
    }

    alignment = {

    }

    voice = {

    }

    spawn = {
        1: "Fanatic",
        2: "Zombie"
    }

    game_status = {

    }

    objective = {
        1: "Objective_A",
        2: "Objective_B",
        3: "Objective_C",
        4: "Objective_D",
        5: "Objective_E",
        6: "Objective_F",
        7: "Objective_G",
        8: "Objective_H",
        9: "Objective_I",
        10: "Objective_J",
        11: "Objective_K",
        12: "Objective_L",
        13: "Objective_M",
        14: "Objective_N",
        15: "Objective_O",
        16: "Objective_P",
        17: "Objective_Q",
        18: "Objective_R",
        19: "Objective_S",
        20: "Objective_T",
        21: "Objective_U",
        22: "Objective_V",
        23: "Objective_W",
        24: "Objective_X",
        25: "Objective_Y",
        26: "Objective_Z"
    }

    boss = {
        1: "Carstein",
        2: "Nagash",
        3: "Black_Grail"
    }

    @staticmethod
    def get_bits_set(x):
        bits = []

        for y in range(32):
            z = x & (0 | 1 << y)
            if z:
                bits.append(z)

        return bits

    @staticmethod
    def flag_prettifier(flag, lookup_dict, prefix):
        s = " | ".join(
            map(lambda x: lookup_dict.get(x, hex(x)), Prettifier.get_bits_set(int(flag)))
        )
        return Prettifier.wrap(prefix, s) if len(s) > 0 else Prettifier.wrap(prefix, "0")

    @staticmethod
    def flag_prettifier_back(flag, lookup_dict):
        beg = flag.find("(")
        end = flag.find(")")

        if beg > -1 and end > -1:
            flag = flag[beg+1:end]

        flags = map(lambda x: x.strip(), flag.split("|"))

        flags_back = []
        for f in flags:
            try:
                flags_back.append(int(f, 0))
            except ValueError:
                for k, v in lookup_dict.items():
                    if v == f:
                        flags_back.append(k)
                        break
        return sum([int(x) for x in flags_back])

    @staticmethod
    def substitute(val, lookup_dict, name):
        v = lookup_dict.get(int(val))

        if v:
            return v

        return Prettifier.wrap(name, val)

    @staticmethod
    def substitute_back(val, lookup_dict):
        for k, v in lookup_dict.items():
            if v == val:
                return int(k)

        return Prettifier.wrap_back(val)

    @staticmethod
    def wrap(name, val):
        return name + "(" + val + ")"

    @staticmethod
    def wrap_back(val):
        beg = None
        end = 0
        minus = ""

        for e, s in enumerate(val):
            if s.isdigit():
                if beg is None:
                    beg = e
            else:
                if beg is not None:
                    end = e
                    break

        if beg:
            minus = "-" if val[beg - 1] == "-" else ""

        return int(minus + val[beg:end])

    @staticmethod
    def end_event(val):
        if val == "6844":
            return "Filter"
        elif val == "3567":
            return "Propagate"
        else:
            return hex(int(val))

    @staticmethod
    def end_event_back(val):
        if val == "Filter":
            return 6844
        elif val == "Propagate":
            return 3567
        else:
            return int(val, 0)

    label_dict = {

    }

    prettifier = {
        Arg_Unused: [
            lambda a: Prettifier.wrap("X", a),
            lambda a: Prettifier.wrap_back(a)
        ],
        # Arg_Any
        Arg_Function: [
            lambda a: Prettifier.wrap("F", a),
            lambda a: Prettifier.wrap_back(a)
        ],
        Arg_Event: [
            lambda a: Prettifier.substitute(a, Prettifier.event, "E"),
            lambda a: Prettifier.substitute_back(a, Prettifier.event)
        ],
        Arg_Register: [
            lambda a: Prettifier.wrap("R", a),
            lambda a: Prettifier.wrap_back(a)
        ],
        Arg_GlobalRegister: [
            lambda a: Prettifier.wrap("G", a),
            lambda a: Prettifier.wrap_back(a)
        ],
        Arg_BtbNode: [
            lambda a: Prettifier.wrap("BTB", a),
            lambda a: Prettifier.wrap_back(a)
        ],
        Arg_BtbNodeId: [
            lambda a: Prettifier.wrap("BTBId", a),
            lambda a: Prettifier.wrap_back(a)
        ],
        Arg_UF1: [
            lambda flag: Prettifier.flag_prettifier(flag, Prettifier.unit_flag_1, "UF1"),
            lambda flag: Prettifier.flag_prettifier_back(flag, Prettifier.unit_flag_1)
        ],
        Arg_UF2: [
            lambda flag: Prettifier.flag_prettifier(flag, Prettifier.unit_flag_2, "UF2"),
            lambda flag: Prettifier.flag_prettifier_back(flag, Prettifier.unit_flag_2)
        ],
        Arg_UF3: [
            lambda flag: Prettifier.flag_prettifier(flag, Prettifier.unit_flag_3, "UF3"),
            lambda flag: Prettifier.flag_prettifier_back(flag, Prettifier.unit_flag_3)
        ],
        Arg_CtrlFlag: [
            lambda flag: Prettifier.flag_prettifier(flag, Prettifier.ctrl_flag, "CF"),
            lambda flag: Prettifier.flag_prettifier_back(flag, Prettifier.ctrl_flag)
        ],
        Arg_Label: [
            lambda a: hex(int(a)),
            lambda a: int(a, 0)
        ],
        Arg_EndEvent: [
            lambda a: Prettifier.end_event(a),
            lambda a: Prettifier.end_event_back(a)
        ],
        Arg_Missile: [
            lambda flag: Prettifier.substitute(flag, Prettifier.missiles, "Missile"),
            lambda flag: Prettifier.substitute_back(flag, Prettifier.missiles)
        ],
        Arg_UnitType: [
            lambda flag: Prettifier.substitute(flag, Prettifier.unit_type, "Type"),
            lambda flag: Prettifier.substitute_back(flag, Prettifier.unit_type)
        ],
        Arg_Item: [
            lambda a: Prettifier.substitute(a, Prettifier.items, "Magic"),
            lambda a: Prettifier.substitute_back(a, Prettifier.items)
        ],
        Arg_MagicFlag: [
            lambda flag: Prettifier.flag_prettifier(flag, Prettifier.magic_flag, "MF"),
            lambda flag: Prettifier.flag_prettifier_back(flag, Prettifier.magic_flag)
        ],
        Arg_Attribute: [
            lambda flag: Prettifier.flag_prettifier(flag, Prettifier.attributes, "Attrib"),
            lambda flag: Prettifier.flag_prettifier_back(flag, Prettifier.attributes)
        ],
        Arg_Voice: [
            lambda a: Prettifier.substitute(a, Prettifier.voice, "Voice"),
            lambda a: Prettifier.substitute_back(a, Prettifier.voice)
        ],
        Arg_Unit: [
            lambda a: Prettifier.wrap("ID", a),
            lambda a: Prettifier.wrap_back(a)
        ],
        Arg_Alignment: [
            lambda a: Prettifier.substitute(a, Prettifier.alignment, "Alignment"),
            lambda a: Prettifier.substitute_back(a, Prettifier.alignment)
        ],
        Arg_Spawn: [
            lambda a: Prettifier.substitute(a, Prettifier.spawn, "Spawn"),
            lambda a: Prettifier.substitute_back(a, Prettifier.spawn)
        ],
        Arg_GameStatus: [
            lambda a: Prettifier.substitute(a, Prettifier.game_status, "GameStatus"),
            lambda a: Prettifier.substitute_back(a, Prettifier.game_status)
        ],
        Arg_Objective: [
            lambda a: Prettifier.substitute(a, Prettifier.objective, "Objective"),
            lambda a: Prettifier.substitute_back(a, Prettifier.objective)
        ],
        Arg_Boss: [
            lambda a: Prettifier.substitute(a, Prettifier.boss, "Boss"),
            lambda a: Prettifier.substitute_back(a, Prettifier.boss, "Boss")
        ],
        Arg_UnitId: [
            lambda a: Prettifier.wrap("UID", a),
            lambda a: Prettifier.wrap_back(a)
        ]
    }

revOpNames = {}
for opCode in opNames:
    revOpNames[opNames[opCode]] = opCode
revOpNames_ext = {}
for opCode in opNames_ext:
    revOpNames_ext[opNames_ext[opCode]] = opCode

class CTLFileReader(object):
    def __init__(self, path):
        self.__LoadFile(path)
        self.__ConstructOffs()
        self.__ConstructEndList()

    def __LoadFile(self, path):
        F = open(path, "rb")
        self.data = array("i")
        self.data.fromstring(F.read())
        F.close()

    def __ConstructOffs(self):
        stdCount = self.data[0]
        self.stdOff = self.data[1:stdCount]
        extCount = self.stdOff[0] - stdCount
        self.extOff = self.data[stdCount:stdCount+extCount]

    def __ConstructEndList(self):
        self.endList = []
        for off in self.stdOff + self.extOff:
            self.endList.append(off)
        self.endList.pop(0)
        self.endList.append(len(self.data))
        self.endList.sort()

    def __GetFunctionEnd(self, beginFuncOff):
        for i in self.endList:
            if beginFuncOff < i: return i
        raise Exception("ERROR: can't find end of function")

    def __GetFunctionStart(self, ordinal):
        if (ordinal < len(self.stdOff)):
            if (ordinal < len(self.extOff)):
                return self.extOff[ordinal]
        elif (ordinal >= 100):
            if (ordinal < (len(self.stdOff)+100)):
                return self.stdOff[ordinal-100]
        raise Exception("ERROR: function not found")

    def GetFunction(self, ordinal):
        start = self.__GetFunctionStart(ordinal)
        end = self.__GetFunctionEnd(start)
        return AssembledFunction(str(ordinal), src = self.data[start:end])


class DisassembledFunction(object):
    def __init__(self):
        self.lines = []

    def Print(self, stream=None):
        indent = 1

        for tokens in self.lines:
            op = tokens[0]
            args = tokens[1:]

            if (op in ["else", "endif", "while", "whilenot", "always", "next", "test_more_events",".func"]):
                indent -= 1

            stream.write("    "*indent + op)
            if len(args) > 0:
                stream.write(" " + ", ".join(args))
            stream.write("\n")

            if (op in [".func", "iftrue", "iffalse", "else", "on_event", "do", "for", "get_event"]):
                indent+=1

            if (op in ["end_event"]):
                indent -= 1

        stream.write("\n\n")

    def Assemble(self):
        trimmed = [i for i in self.lines if i!='']
        ordinal = None
        while 1:
            line = trimmed.pop(0)
            if ".func" in line:
                ordinal = line.split()[1]
                break

        assFunc = AssembledFunction(ordinal)
        while len(trimmed) > 0:
            line = trimmed.pop(0)
            spLine = line.strip().split(" ", 1)
            spLine = [spLine[0]] + (list(map(lambda x: x.strip(), spLine[1].split(","))) if len(spLine) > 1 else [])
            process_args = False

            if (spLine[0][0] == "@"):
                opcode = spLine[0].replace("@","")
                if opcode == "Filter":
                    opcode = 0xabc
                else:
                    opcode = int(opcode,16)
            elif (spLine[0][0] != "#"):
                if spLine[0] in revOpNames_ext:
                    assFunc.data.append(0x8000 + 0xf1)
                    opnum = revOpNames_ext[spLine[0]]
                    opcode = opnum
                    # todo process_args
                else:
                    opnum = revOpNames[spLine[0]]
                    opcode = opnum + 0x8000
                    process_args = True
            else:
                opcode = int(spLine[0].replace("#","0x80"),16)
                process_args = True
            assFunc.data.append(opcode)

            for i, arg in enumerate(spLine[1:]):
                if process_args:
                    shortOp = opcode - 0x8000

                    if shortOp in opTypes:
                        argTypes = opTypes[shortOp]
                        if argTypes[i] in Prettifier.prettifier:
                            arg = Prettifier.prettifier[argTypes[i]][1](arg)

                assFunc.data.append(int(arg))
        return assFunc

class AssembledFunction(object):
    def __init__(self, name, src=None):
        self.name = name
        if (src != None):
            self.data = list(src)
        else:
            self.data = []

    def Disassemble(self):
        opList = self.data[:]
        decompiledFunc = DisassembledFunction()
        decompiledFunc.lines.append([".func", self.name])

        while len(opList) > 0:
            opcode = opList.pop(0)
            sopcode = opcode
            if (sopcode & 0x8000):
                sopcode = (~sopcode + 1)

            if sopcode >= 0:
                if opcode == 0xabc:
                    decompiledFunc.lines.append(["@Filter"])
                elif opcode == 0x0:
                    decompiledFunc.lines.append(["@0x0"])
                else:
                    decompiledFunc.Print()
                    raise Exception("WARNING: unknown token %x" % opcode)
            else:
                shortOp = (opcode & 0x7FFF)
                if shortOp == 0xf1:
                    subop = opList.pop(0)
                    argCount = opLengths_ext[subop]
                    opName = opNames_ext[subop]
                else:
                    argCount = opLengths[shortOp]
                    opName = opNames.get(shortOp, "#%.2x"%shortOp)

                newLine = []

                if argCount > 0:
                    argTypes = opTypes.get(shortOp)

                    add_label_annotation = None

                    for i in range(argCount):
                        if shortOp != 0xf1 and argTypes[i] in Prettifier.prettifier:
                            if argTypes[i] == Arg_Label:
                                if shortOp == 0x3f and opList[0] not in Prettifier.label_dict:
                                    Prettifier.label_dict[opList[0]] = self.name
                                else:
                                    add_label_annotation = Prettifier.label_dict.get(opList[0])

                            newLine.append(Prettifier.prettifier[argTypes[i]][0](str(opList.pop(0))))
                        else:
                            newLine.append(str(opList.pop(0)))

                    if add_label_annotation is not None:
                        newLine[-1] = newLine[-1] + " ; label assigned in func {}".format(add_label_annotation)

                decompiledFunc.lines.append([opName] + newLine)

        return decompiledFunc

class DisctlFileReader(object):
    def __init__(self, path):
        F = open(path, "rt")
        lines = F.readlines()
        F.close()

        self.funcs = []
        curFunc = None
        while (len(lines) > 0):
            line = lines.pop(0)
            if (".func" in line):
                if curFunc != None: self.funcs.append(curFunc)
                curFunc = DisassembledFunction()
            line = line.partition(";")[0]
            line = line.strip()
            curFunc.lines.append(line)
        self.funcs.append(curFunc)


class CTLFileWriter(object):
    def __init__(self, path):
        self.F = open(path, "wb")
        self.funcs = {}

    def AddFunc(self, func):
        ordinal = int(func.name)
        self.funcs[ordinal] = func

    def close(self):
        from struct import pack

        extOrds = []
        stdOrds = []
        for ordinal in self.funcs:
            if (ordinal < 100): extOrds.append(ordinal)
            else: stdOrds.append(ordinal)
        extOrds.sort()
        stdOrds.sort()

        self.F.write(pack("<I", len(stdOrds)+1))
        cuml = 1 + len(stdOrds) + len(extOrds)
        for i in stdOrds+extOrds:
            datasize = len(self.funcs[i].data)
            self.F.write(pack("<I",cuml))
            cuml += datasize

        for i in stdOrds+extOrds:
            func = self.funcs[i]
            for it in func.data:
                self.F.write(pack("<i",it))

        self.F.close()


if MODE == 1:
    if path.exists(disassembled_file_name):
        if sys.version_info[0] < 3:
           input = raw_input

        ans = input("A decompiled script already exists. Overwrite? [y/n] ")

        if ans != "y":
            exit(1)

    print("DISASSEMBLING")

    F = open(disassembled_file_name,"wt")

    if not path.exists(original_file_name):
        copyfile(assembled_file_name, original_file_name)

    C = CTLFileReader(original_file_name)
    for i in chain(range(0, len(C.extOff)), range(100, len(C.stdOff)+100)):
        compFunc = C.GetFunction(i)
        decompFunc = compFunc.Disassemble()
        decompFunc.Print(stream=F)
    F.close()

else:
    print("ASSEMBLING")
    D = DisctlFileReader(disassembled_file_name)
    W = CTLFileWriter(assembled_file_name)
    for func in D.funcs:
        W.AddFunc( func.Assemble() )
    W.close()
