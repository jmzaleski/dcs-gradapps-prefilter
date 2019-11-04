from __future__ import print_function  #allows print as function


dl_dir = "/home/matz/mscac/home/gradbackup/archive/mscac.2020/mscac20/"

def parse_profile_data_line(line):
    "returns stuff to right of ="
    #  #set $sp364-value$ = "2014-09|2018-05|UNIV OF TORONTO|BSC H|2.88/4.0|||||||||||||||"; 
    print("rhs",line)
    rhs = line.split("=")[1]
    print("rhs",rhs)
    return rhs
    
def eat_profile_data_file(fn):
    with open(fn,"r") as profile_data_file:
        import re
        rec = {}
        for line in profile_data_file:
            if re.search("342",line):
                print("SGS#",line)
                rec["SGS_NUM"] = line
            elif re.search("364",line):
                print("union institution", line)
                print(parse_profile_data_line(line))
                rec["DCS_UNION_INSTITUTION"] = parse_profile_data_line(line)
            elif re.search("363",line):
                print("status", line)
                rec["DCS_STATUS"] = line
        print(rec)

def parse_positional_args():
    "parse the command line parameters of this program"
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "fn_of_list_of_profile_data", help="likely fn containing find . -name profile.data"
        )
    args = parser.parse_args()
    return args.fn_of_list_of_profile_data

if __name__ == '__main__': 
    import sys
    import os
    #duplicate. sorta. so works on mac and windows laptops
    for dir in ['/Users/mzaleski/git/dcs-gradapps-prefilter/']:
        sys.path.append(dir)

        
    fn_file_list = parse_positional_args() #eg: /tmp/xxx
    try:
         with open(fn_file_list, "r") as in_file:
             for l in in_file:
                 eat_profile_data_file(l.strip())
    except:
         print(fn_file_list, "failed to open for read? really? bail!")
         import traceback
         traceback.print_exc(file=sys.stdout)
         exit(3)


         
