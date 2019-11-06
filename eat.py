from __future__ import print_function  #allows print as function
import sys, os.path

def die(*objs):
    print("ERROR: ", *objs, file=sys.stderr)
    exit(42)

HOME_DIR="/Users/mzaleski"
assert os.path.exists(HOME_DIR)

TOOLS_DIR = os.path.join(HOME_DIR,"git/dcs-gradapps-prefilter/")
assert os.path.exists(TOOLS_DIR)

#root of unzipped archive of gradapps files
MASC_UNZIP_DIR = os.path.join(HOME_DIR,"mscac/home/gradbackup/archive/mscac.2020/mscac20")
if not os.path.exists(MASC_UNZIP_DIR): die(MASC_UNZIP_DIR, "does not exist")

#dir where transcripts, sop, cv live
MASC_PAPERS_DIR = os.path.join(MASC_UNZIP_DIR,"public_html/papers/")
assert os.path.exists(MASC_PAPERS_DIR)

#shell script to fire up viewers on PDF files
VIEWER = os.path.join(TOOLS_DIR,"view-files.sh")
assert os.path.exists(VIEWER)

#file listing which apps are complete
COMPLETE_FILE = os.path.join(MASC_UNZIP_DIR,"public_html/admin/applicationStatus")
assert os.path.exists(COMPLETE_FILE)


VERBOSE = False

#output file directory
MASC_PREFILTER_DIR_NAME = "masc-prefilter"
OFN_DIR=os.path.join(HOME_DIR,MASC_PREFILTER_DIR_NAME)
if not os.path.exists(OFN_DIR): die("OFN_DIR", OFN_DIR, "does not exist")

# where to rsync output file for gradapps
CSLAB_USERID = 'matz@apps1.cs.toronto.edu'
    
#obscure python way of deleting chars from unicode strings..
translation_table_to_delete_chars = dict.fromkeys(map(ord, '!@#$;"'), None)

def parse_profile_data_line(line):
    "returns stuff to right of = found in gradapps profile.data files"
    # EG: #set $sp364-value$ = "2014-09|2018-05|UNIV OF TORONTO|BSC H|2.88/4.0|||||||||||||||"; 
    if VERBOSE: print("rhs",line)
    try:
        rhs = line.split("=")[1]
    except:
        print("failed to split = on ", line)
        exit(3)
    return rhs.strip().translate(translation_table_to_delete_chars)


def completed_dict_from_applicationStatus_file(fn):
    "reads applicationStatus files and stashes away which apps are complete"
    with open(fn,"r") as apf:
        import re
        map = {}
        for line in apf:
            fields = line.split(" ")
            assert len(fields) == 2
            if re.search("complete",fields[1]):
                assert re.search("complete",line)
                map[fields[0]] = True
            else:
                map[fields[0]] = False
    return map

def dict_from_profile_data_file(fn):
    "turn a profile.data file into a dictionary with only a few fields"
    #TODO: this is ugly brute force. I'm sure there are fancy libs to do this pretty
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
    "we figure out the app number by cracking open the dir path to the profile.data file"
    try:
        l = path.split("public_html/data")
        d = l[1].split("/")
        app_num = d[1]
        return  app_num
    except:
        print("failed: split on public_html/data of ", path)
        exit(3)
    
def build_dict_of_dicts(fn):
    """read the listed profile.data files and turn the row in each into a dict
    the file name passed in fn was written by doing a find . -name profile.data"""
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

    completed_app_dict = completed_dict_from_applicationStatus_file(COMPLETE_FILE)
    
    (app_num_to_profile_data,sgs_num_to_profile_data) = build_dict_of_dicts(fn_file_list)

    app_num_list = []
    for app_num in app_num_to_profile_data.keys():
        profile_data = app_num_to_profile_data[app_num]
        institution = profile_data["DCS_UNION_INSTITUTION"]
        if not re.search(uni_filter_regexp, institution):
            if VERBOSE: print("skip", app_num, "because", institution, "not matched by", uni_filter_regexp)
        else:
            sop_fn =  fn(app_num,1)
            cv_fn =  fn(app_num,2)
            transcript_fn =  fn(app_num,3)
            if not app_num in completed_app_dict.keys():
                continue
                print("skip", app_num, "because not complete")
            elif not os.path.exists(transcript_fn):
                print("skip", app_num, "because transcript does not exist")
            elif not os.path.exists(sop_fn):
                print("skip", app_num, "because SOP does not exist")
            elif not os.path.exists(cv_fn):
                print("skip", app_num, "because CV does not exist")
            else:
                app_num_list.append(app_num)

    #try and sort app_num_list by GPA
    def extract_gpa(app_num):
        profile_data = app_num_to_profile_data[app_num]
        inst = profile_data["DCS_UNION_INSTITUTION"]
        fields = inst.split('|')
        #dreadful hack to get around 3.85/4 business
        gpa_str = fields[4].split("/")[0] 
        try:
            return float(gpa_str)
        except:
            return 0.0

    app_num_list = sorted(app_num_list,key=extract_gpa,reverse=True)
            
                
    print("\n\n===============================\nAPPS matching: ",uni_filter_regexp)
    for app_num in app_num_list:
        profile_data = app_num_to_profile_data[app_num]
        profile_data["DCS_UNION_INSTITUTION"]
        print(app_num, profile_data["SGS_NUM"],profile_data["DCS_UNION_INSTITUTION"])
    print("===============================\n")

    try:
        response = input("prefilter above " + str(len(app_num_list)) + " applications? matching " +
                         uni_filter_regexp + " (enter any char to BAIL OUT)> ")
    except:
        response = None
        
    if response == None or (len(response) > 0 and not response.lower().startswith("y")):
        print("entering something bails out.. just enter to continue")
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
        if os.path.exists(fn):
            os.system("mv %s %s" % (fn, "/tmp"))
        print("existing %s moved to /tmp" % fn)
        with open(fn,'w') as new_file:
            for k in dict.keys():
                line = k + "," + str(dict[k])
                print(line)
                print(line,file=new_file)

    from menu import PrefilterMenu

    # what to display in menu
    menu_line_dict = { 's' : "Pass-Star:    Star applicant pass prefilter. maybe early admission",
                           'v' : "Pass-VGE:     Very Good applicant. pass prefilter",
                           'g' : "Pass-G:       Good applicant. pass prefilter",
                           'u' : "Unsure:       whether this applicant should pass prefilter",
                           'r' : "Reject:       Reject application. fails prefilter",
                           'x' : "NCS-Reject:   not enough CS. Fails prefilter",
                           'y' : "NCS-Pass:     not enough CS but stellar enough to pass prefilter"
                        }
    #order to display menu items in 
    response_code_list = ['r', 's','v','g','u','x','y']

    #map responses to gradapps prefilter status column values
    gradapps_response_map = { 's' : "Pass-Star",
                           'v' : "Pass-VGE",
                           'g' : "Pass-G",
                           'u' : "Unsure",
                           'r' : "Reject",
                           'x' : "NCS-Reject",
                           'y' : "NCS-Pass",
                        }
    
    menu = PrefilterMenu(response_code_list, menu_line_dict ,"enter a letter followed by enter> ")

    import uuid #universal unique resource naming thingy
    OFN_basename = "dcs-prefilter" + str(uuid.uuid4()) + ".csv"
    OFN = os.path.join(OFN_DIR,OFN_basename)
    assert not os.path.exists(OFN)
    write_to_new_file(OFN,{}) #test write junk to OFN to make sure have perms and all that
    
    #########
    # main loop asking for decisions and writing them (paranoidly) away
    #########
    decisions = {}
    for app_num in app_num_list:
        #concoct path of app_num "papers"
        # file-NNN-1.pdf is transcript
        sop_fn =  fn(app_num,1)
        cv_fn =  fn(app_num,2)
        transcript_fn =  fn(app_num,3)
        print(os.path.basename(sop_fn),os.path.basename(cv_fn),os.path.basename(transcript_fn))
        os.system(VIEWER  + " " + sop_fn + " " + cv_fn + " " + transcript_fn)
        #in a different shell: echo "MAIB103GMIRPJGAX92E1RZT1Z65P900P" > /tmp/user_ref
        print('user_ref=$(cat /tmp/user_ref) && open "https://confs.precisionconference.com/~mscac20/submissionProfile?paperNumber=' + app_num +'&userRef=$user_ref"')
        resp = ""
        while True:
            print("choose dcs prefilter status for application",app_num,"from menu below")
            print(app_num_to_profile_data[app_num]["DCS_UNION_INSTITUTION"])
            
            ########## menu for actual decision 
            resp = menu.menu()
            if resp == None:
                print("\n\nwonky reponse (interrupt key pressed?) from menu",resp)
                continue
            gradapps_response = gradapps_response_map[resp]
            #print("resp:", resp, gradapps_response)

            if gradapps_response == None:
                print("gotta choose something here. looping around")
                continue
            print(resp)
            try:
                profile_data = app_num_to_profile_data[app_num]
                decisions[profile_data["SGS_NUM"]] = gradapps_response
            
                ########## paranoidly, write every time
                # megaparanoid would be to copy file each time to tmp
                write_to_new_file(OFN, decisions) # 
            #except:
            except Exception as e:
                print(e)
                import traceback
                traceback.print_exc(file=sys.stderr)
                print(OFN, "something when wrong writing.. please try enter", resp,"again")
                print("""Note: if you get stuck looping in here only way out is to control-z and kill this job""")
                resp = ""
                continue
            break

    #########
    # rest of script largely BS for convenience putting the output somewhere useful
    #########
    print(decisions)
    os.system("cat " + OFN)
    os.system("ls -l " + OFN)
    print("""to import these prefilter decisions into the gradapps system:
    1. copy to file on apps1 
    2. curl to gradapps server""")
    print("\n=========================\n...and execute following commands:\n")
    dest = "%s:%s/" % (CSLAB_USERID, MASC_PREFILTER_DIR_NAME)
    rsync_cmd = "rsync  %s %s" %  (OFN, dest)
    curl_cmd =  'curl -F appsFile="%s" "%s"' % (
        OFN_basename,
        'https://confs.precisionconference.com/~mscac20/uploadApps?config=prefilter&pass=StayorGo'
        )

    # probably will need ssh config support or will prompt for password
    print(rsync_cmd)
    print(curl_cmd)
    print("\n=========================\n")
    resp = input("hit Enter to exec rsync above (control-c only way to skip rsync) > ")
    os.system(rsync_cmd)

    print("now check file arrived by remote ls -ltr of dest dir")
    os.system("ssh %s ls -ltr %s" % (CSLAB_USERID, MASC_PREFILTER_DIR_NAME))
    print("\nlast file of above ls -ltr should have be:   ", OFN_basename)

    print("\nnow ssh to", CSLAB_USERID, "and curl file to gradapps\n")
    print(curl_cmd)
    
