from __future__ import print_function  #allows print as function



def parse_profile_data_line(line):
    "returns stuff to right of ="
    #  #set $sp364-value$ = "2014-09|2018-05|UNIV OF TORONTO|BSC H|2.88/4.0|||||||||||||||"; 
    print("rhs",line)
    try:
        rhs = line.split("=")[1]
    except:
        print("failed to split = on ", line)
        exit(3)
    #print("rhs",rhs)
    return rhs
    
def dict_from_profile_data_file(fn):
    with open(fn,"r") as profile_data_file:
        import re
        rec = {}
        for line in profile_data_file:
            if re.search("sp342-value",line):
                #print("SGS#",line)
                rec["SGS_NUM"] = parse_profile_data_line(line)
            elif re.search("sp364-value",line):
                #print("union institution", line)
                #print(parse_profile_data_line(line))
                rec["DCS_UNION_INSTITUTION"] = parse_profile_data_line(line)
            elif re.search("sp363-value",line):
                #print("status", line)
                rec["DCS_STATUS"] = parse_profile_data_line(line)
        return rec

def parse_dir_path_for_app_number(path):
    try:
        l = path.split("public_html/data")
        d = l[1].split("/")
        app_num = d[1]
        print(path,app_num)
        return  app_num
    except:
        print("failed: split on public_html/data of ", path)
        exit(3)
    
def build_dict_of_dicts(fn):
    "read the listed profile.data files and turn the row in each into a dict"
    profile_data_by_app_number = {}
    profile_data_by_sgs_number = {}
    try:
         with open(fn_file_list, "r") as in_file:
             for l in in_file:
                 d = dict_from_profile_data_file(l.strip())
                 app_num = parse_dir_path_for_app_number(l)
                 profile_data_by_app_number[app_num] = d
                 profile_data_by_sgs_number[d["SGS_NUM"]] = d
         #print(profile_data_by_sgs_number)
    except:
         print(fn_file_list, "failed to open for read? really? bail!")
         import traceback
         traceback.print_exc(file=sys.stdout)
         exit(3)
         return None
    return (profile_data_by_app_number, profile_data_by_sgs_number)
    
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
    import re
    #duplicate. sorta. so works on mac and windows laptops
    for dir in ['/Users/mzaleski/git/dcs-gradapps-prefilter/']:
        sys.path.append(dir)
    fn_file_list = parse_positional_args() #eg: /tmp/xxx
    (app_num_to_profile_data,sgs_num_to_profile_data) = build_dict_of_dicts(fn_file_list)
    #print(sgs_num_to_profile_data)
    app_num_list = []
    for app_num in app_num_to_profile_data.keys():
        #print(app_num)
        profile_data = app_num_to_profile_data[app_num]
        institution = profile_data["DCS_UNION_INSTITUTION"]
        if re.search("TORONTO", institution):
            #print(profile_data)
            print(app_num,institution)
            app_num_list.append(app_num)
    print(app_num_list)

    DIR = "/Users/mzaleski/mscac/home/gradbackup/archive/mscac.2020/mscac20/public_html/papers/"

    def fn(n,nn):
        return DIR + n + "/file" + n + "-" + str(nn) + ".pdf"

    def read_query_from_input(prompt):
        "UI read a line from stdin"
        try:
            # readline will do completion on utorid's but can enter any string from grade file too
            query_string = input(prompt)
            if len(query_string) == 0:
                return None
            else:
                return query_string
        except KeyboardInterrupt:
            print("..keyboard interrupt..")
            return '' #empty string
        except EOFError:
            print("..eof..")
            return None

    viewer = "/Users/mzaleski/git/dcs-gradapps-prefilter/view-files.sh"
    for app_num in app_num_list:
        #os.system("ls -l " + DIR + app_num)
        #concoct path of app_num "papers"
        # file-NNN-1.pdf is transcript
        sop_fn =  fn(app_num,1)
        cv_fn =  fn(app_num,2)
        transcript_fn =  fn(app_num,3)
        print(sop_fn,cv_fn,transcript_fn)
        xx = read_query_from_input(app_num)        
        #os.system("open " + sop_fn + " " + cv_fn + " " + transcript_fn)
        os.system(viewer  + " " + sop_fn + " " + cv_fn + " " + transcript_fn)
        
        
                         
                         

        


         
