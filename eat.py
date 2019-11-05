from __future__ import print_function  #allows print as function
import os.path

HOME_DIR="/Users/mzaleski"
assert os.path.exists(HOME_DIR)

TOOLS_DIR = os.path.join(HOME_DIR,"git/dcs-gradapps-prefilter/")
assert os.path.exists(TOOLS_DIR)

MASC_UNZIP_DIR = os.path.join(HOME_DIR,"mscac/home/gradbackup/archive/mscac.2020/mscac20")
assert os.path.exists(MASC_UNZIP_DIR)
    
MASC_PAPERS_DIR = os.path.join(MASC_UNZIP_DIR,"public_html/papers/")
assert os.path.exists(MASC_PAPERS_DIR)

VIEWER = os.path.join(TOOLS_DIR,"view-files.sh")
assert os.path.exists(VIEWER)

VERBOSE = False

def parse_profile_data_line(line):
    "returns stuff to right of ="
    #  #set $sp364-value$ = "2014-09|2018-05|UNIV OF TORONTO|BSC H|2.88/4.0|||||||||||||||"; 
    if VERBOSE: print("rhs",line)
    try:
        rhs = line.split("=")[1]
    except:
        print("failed to split = on ", line)
        exit(3)
    #print("rhs",rhs)
    return rhs.strip()
    
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
    parser.add_argument(
        "uni_filter_regexp", help="university to filter by"
        )

    args = parser.parse_args()
    return (args.fn_of_list_of_profile_data, args.uni_filter_regexp)

def fn(n,nn):
    return MASC_PAPERS_DIR + n + "/file" + n + "-" + str(nn) + ".pdf"

if __name__ == '__main__': 
    import sys
    import os
    import re
    #duplicate. sorta. so works on mac and windows laptops
    for dir in [TOOLS_DIR]:
        sys.path.append(dir)
    (fn_file_list,uni_filter_regexp) = parse_positional_args()
    
    (app_num_to_profile_data,sgs_num_to_profile_data) = build_dict_of_dicts(fn_file_list)
    #print(sgs_num_to_profile_data)
    
    app_num_list = []
    for app_num in app_num_to_profile_data.keys():
        #print(app_num)
        profile_data = app_num_to_profile_data[app_num]
        institution = profile_data["DCS_UNION_INSTITUTION"]
        if not re.search(uni_filter_regexp, institution):
            if VERBOSE: print("skip", app_num, "because", institution, "not matched by", uni_filter_regexp)
        else:
            sop_fn =  fn(app_num,1)
            cv_fn =  fn(app_num,2)
            transcript_fn =  fn(app_num,3)
            if not os.path.exists(transcript_fn):
                print("skip", app_num, "because transcript does not exist")
            elif not os.path.exists(sop_fn):
                print("skip", app_num, "because SOP does not exist")
            if not os.path.exists(cv_fn):
                print("skip", app_num, "because CV does not exist")
            else:
                app_num_list.append(app_num)

                
    print("\n\n===============================\nAPPS matching: ",uni_filter_regexp)
    for app_num in app_num_list:
        profile_data = app_num_to_profile_data[app_num]
        profile_data["DCS_UNION_INSTITUTION"]
        print(profile_data["SGS_NUM"],profile_data["DCS_UNION_INSTITUTION"])

    #make sure this list makes some kind of sense
    response = input("prefilter above " + str(len(app_num_list)) + " applications? matching " +
                         uni_filter_regexp + " (enter any char to continue)> ")
    if len(response) == 0 :
        print("wanted you to enter something to continue.. outa here")
        exit(0)
        


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

    def write_to_new_file(fn,dict):
        """write all lines out to a new file name"""
        with open(fn,'w') as new_file:
            for k in dict.keys():
                line = str(k)+","+str(dict[k])
                print(line,file=new_file)

    decisions = {}
    for app_num in app_num_list:
        #concoct path of app_num "papers"
        # file-NNN-1.pdf is transcript
        sop_fn =  fn(app_num,1)
        cv_fn =  fn(app_num,2)
        transcript_fn =  fn(app_num,3)
        print(os.path.basename(sop_fn),os.path.basename(cv_fn),os.path.basename(transcript_fn))
        os.system(VIEWER  + " " + sop_fn + " " + cv_fn + " " + transcript_fn)
        resp = ""
        while True:
            #here matzmenu..
            resp = read_query_from_input("decision code for applicant number " + app_num + " (enter to continue)> ")
            if len(resp) == 0:
                print("gotta say something")
                continue
            print(resp)
            profile_data = app_num_to_profile_data[app_num]
            decisions[profile_data["SGS_NUM"]] = resp
            try:
                #copy fn to backup
                write_to_new_file("/tmp/out", decisions) # yeah, write every time
            except:
                print("something when wrong writing.. please try enter", resp,"again")
                resp = ""
                continue
            break

    print(decisions)
            
        
        
                         
                         

        


         
