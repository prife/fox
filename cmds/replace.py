#!/usr/bin/python

# encoding: UTF-8
import sys
import re

services={
        "fingerprint":"FINGERPRINT_SERVICE",
        "activity": "ACTIVITY_SERVICE",
        "power":"POWER_SERVICE",
        "layout_inflater":"LAYOUT_INFLATER_SERVICE",
        "audio": "AUDIO_SERVICE",
        "window": "WINDOW_SERVICE",
        "keyguard": "KEYGUARD_SERVICE",
        "device_policy": "DEVICE_POLICY_SERVICE",
        "input_method": "INPUT_METHOD_SERVICE",
        "telecom": "TELECOM_SERVICE",
        }

PREIFX = "/Users/prife/tools/fox/cmds"
INTENT_FLAG_TXT = PREIFX+"/intent_flag.txt"
VISIBILITY_FLAG_TXT = PREIFX+"/visibility_flag.txt"
WINDOW_LP_FLAG_TXT = PREIFX+"/window_lp_flag.txt"

intent_map={}
intent_flag_map={}
visibility_flag_map={}
window_lp_flag_map={}

def load_intent_maps():
    with open(PREIFX+"/intent.txt") as f:
        for line in f:
            line_kv = line.split(":")
            intent_map[line_kv[0]] = line_kv[1][:-1]

def load_flag(flag_file, out_map):
    with open(flag_file) as f:
        for line in f:
            if line.startswith("#"):
                continue
            line_kv = line.split(":")
            flag_bit = int(line_kv[0], 16)
            out_map[flag_bit] = line_kv[1][:-1]

def gen_string_from_flag_map(flag, inmap):
    flag_backup = flag
    flag_str = None
    for k, v in inmap.items():
        if flag & k == k:
            if flag_str is None:
                flag_str = v
            else:
                flag_str = flag_str  + " | " + v
            # clear the bit
            flag &= ~k
    if flag == 0:
        return "%s /* 0x%08x */" %(flag_str, flag_backup)
    return "%s | 0x%08x /* 0x%08x */" %(flag_str, flag, flag_backup)

def gen_string_from_flag_table(flag, inmap):
    return inmap[flag]

def convent2hex(number):
    hex = 0xFFFFFFFF+(-328966) +1 if number < 0 else  number

def replace_flags(text, pattern, cust_map, mode=None):
    def dashrepl(matchobj):
        flag = int(matchobj.group(1), 0)
        if mode == "T":
            flag_gen = gen_string_from_flag_table(flag, cust_map)
        else:
            flag_gen = gen_string_from_flag_map(flag, cust_map)

        print("%s --> %s" %(flag, flag_gen))
        return r".%s(%s)" %(pattern, flag_gen)

    p_pattern = r"\.%s\((\d+)\)"%pattern
    return re.sub(p_pattern, dashrepl, text)

def replace(fsrc):
    fd = open(fsrc, 'rb+')
    s = fd.read()
    for k, v in intent_map.items():
        s = re.sub(k, v, s);

    for k, v in services.items():
        s = re.sub("getSystemService\(\"%s\"\)" %k, "getSystemService(Context.%s)" %v, s);

    s = replace_flags(s, "setVisibility", visibility_flag_map, "T")

    fd.close()
    fd = open(fsrc, 'w')
    fd.write(s)

def replace_files(file_lists):
    for i in file_lists:
        print("--> replace %s" %i)
        replace(i)

def help(name):
    print("Usage: %s f_i <flag>" %name)
    print("       %s r <file1, file2, ...>" %name)

def main(argv):
    if (len(argv) < 3):
        help("replace.py")
        return

    option = argv[1]
    if option == "f_i" or option == "intent" :
        flag = int(argv[2], 0)
        print(gen_string_from_flag_map(flag, intent_flag_map))
    elif option == "f_lp":
        flag = int(argv[2], 0)
        print(gen_string_from_flag_map(flag, window_lp_flag_map))
    elif option == "r":
        replace_files(argv[1:])
    else:
        help("replace.py")

if __name__ == "__main__":
    load_intent_maps()
    load_flag(INTENT_FLAG_TXT, intent_flag_map)
    load_flag(VISIBILITY_FLAG_TXT, visibility_flag_map)
    load_flag(WINDOW_LP_FLAG_TXT, window_lp_flag_map)
    main(sys.argv)
