# CTL Assembler/Disassembler
# First Release: 2009-12-07 (by Rob)
# Last Update: 2012-05-05

from array import array

base_name = "b101"

original_file_name   = base_name+"_orig.ctl"
disassembled_file_name = base_name+".txt"
assembled_file_name  = base_name+".ctl"

MODE = 1 # 0 == assemble, 1 == disassemble


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

    0x2a:"patrol_to_waypoint",
    0x2b:"block_movement",
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
    0x3f:"set_label",
	
    0x40:"store_unit_by_label",
    0x41:"test_label_exists",
    0x42:"send_event_to_self_if_label_exists",
    
    0x4c:"nop_4c",

    0x4e:"goto_iftrue",
	
    0x52:"move_rand_in_radius",

    0x53:"init_teleport",
    0x54:"teleport_to",
    0x55:"teleport_to2",
    
	0x5a:"charge",
    0x5c:"retreat",
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

    0x8d:"test_missile_weapon",

    0x90:"nop_90",
    0x91:"nop_91",
    0x92:"nop_92",

    0x93:"test_magic_points_leq_i",
    0x94:"add_magic_points",
	
    0x97:"init_teleport_spell",
    0x98:"cast_spell",
    0x99:"cast_spell2",
    0x9d:"add_spell",

    0xa2:"search_and_attack_enemy",
    0xac:"search_and_shoot_enemy",
    
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

    0xd3:"test_event_arg3",

    0xd5:"test_units_alive_le_i",
    0xd7:"test_boss_defeated",
	0xd8:"test_unit_alive",
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

revOpNames = {}
for opCode in opNames:
    revOpNames[opNames[opCode]] = opCode

class CTLFileReader(object):
    def __init__(self, path):
        self.__LoadFile(path)
        self.__ConstructOffs()
        self.__ConstructEndList()
                
    def __LoadFile(self, path):
        F = file(path, "rb")
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
        
        for line in self.lines:
            tokens = line.replace(",","").split()
            op = tokens[0]
            args = tokens[1:]
            

            if (op in ["else", "endif", "while", "whilenot", "always", "next", "test_more_events",".func"]): indent -= 1
            print >> stream, "    "*indent + op + " " + ", ".join(args)
            if (op in [".func", "iftrue", "iffalse", "else", "on_event", "do", "for", "get_event"]): indent+=1
            if (op in ["end_event"]): indent -= 1

        print >> stream, "\n\n\n"

    def Assemble(self):
        trimmed = [i for i in self.lines if i!='']
        ordinal = None
        while 1:
            line = trimmed.pop(0)
            if (".func" in line):
                ordinal = line.split()[1]
                break

        assFunc = AssembledFunction(ordinal)
        while len(trimmed) > 0:
            line = trimmed.pop(0)
            spLine = line.replace(",","").split()
            opcode = None
            if (spLine[0][0] == "@"):
                opcode = spLine[0].replace("@","")
                opcode = int(opcode,16)
            elif (spLine[0][0] != "#"):
                opnum = revOpNames[spLine[0]]
                opcode = opnum + 0x8000
            else:
                opcode = int(spLine[0].replace("#","0x80"),16)
            assFunc.data.append(opcode)
            for arg in spLine[1:]:
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
        decompiledFunc.lines.append(".func %s" % self.name)
        
        while (len(opList)>0):
            opcode = opList.pop(0)
            sopcode = opcode
            if (sopcode & 0x8000): sopcode = (~sopcode + 1)
                
            if (sopcode >= 0):
                if opcode == 0xabc:
                    decompiledFunc.lines.append("@0xABC")
                elif opcode == 0x0:
                    decompiledFunc.lines.append("@0x0")
                else:
                    decompiledFunc.Print()
                    raise Exception("WARNING: unknown token %x" % opcode)
            else:
                shortOp = (opcode & 0x7FFF)
                argCount = opLengths[shortOp]
                opName = opNames.get(shortOp, "#%.2x"%shortOp)
                
                newLine = []
                for i in xrange(argCount):
                    newLine.append( str(opList.pop(0)) )
                formLine = "%s %s" % (opName, ", ".join(newLine))
                decompiledFunc.lines.append(formLine)

        return decompiledFunc
            
class DisctlFileReader(object):
    def __init__(self, path):
        F = file(path, "rt")
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
        self.F = file(path, "wb")
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
    print "DISASSEMBLING"
    F = file(disassembled_file_name,"wt")
    C = CTLFileReader(original_file_name)
    for i in range(0, len(C.extOff)) + range(100, len(C.stdOff)+100) :
        compFunc = C.GetFunction(i)
        decompFunc = compFunc.Disassemble()
        decompFunc.Print(stream=F)
    F.close()

else:
    print "ASSEMBLING"
    D = DisctlFileReader(disassembled_file_name)
    W = CTLFileWriter(assembled_file_name)
    for func in D.funcs:
        W.AddFunc( func.Assemble() )
    W.close()