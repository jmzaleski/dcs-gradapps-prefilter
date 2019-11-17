from __future__ import print_function  #allows print as function
import sys, os.path

VERBOSE = False

def die(*objs):
    print("ERROR: ", *objs, file=sys.stderr)
    exit(42)

HOME_DIR = os.environ['HOME'] 
if not os.path.exists(HOME_DIR): die("HOME_DIR", HOME_DIR, "does not exist")
assert os.path.exists(HOME_DIR)

TOOLS_DIR = os.path.join(HOME_DIR,"git","dcs-gradapps-prefilter")
if not os.path.exists(TOOLS_DIR): die("TOOLS_DIR", TOOLS_DIR, "does not exist")

#root of unzipped archive of gradapps files
MSCAC_UNZIP_DIR = os.path.join(HOME_DIR,"mscac")
if not os.path.exists(MSCAC_UNZIP_DIR): die(MSCAC_UNZIP_DIR, "does not exist")

#dir where transcripts, sop, cv live
MSCAC_PAPERS_DIR = os.path.join(MSCAC_UNZIP_DIR,"public_html","papers")
if not os.path.exists(MSCAC_PAPERS_DIR): die(MSCAC_PAPERS_DIR, "does not exist")

#dir where application dirs containing profile.data live
MSCAC_PROFILE_DATA_ROOT_DIR = os.path.join(MSCAC_UNZIP_DIR,"public_html","data")
if not os.path.exists(MSCAC_PROFILE_DATA_ROOT_DIR): die(MSCAC_PROFILE_DATA_ROOT_DIR, "does not exist")

#shell script to fire up viewers on PDF files
VIEWER = os.path.join(TOOLS_DIR,"view-files.sh")
assert os.path.exists(VIEWER)

#file listing which apps are complete
COMPLETE_FILE = os.path.join(MSCAC_UNZIP_DIR,"public_html/admin/applicationStatus")
if not os.path.exists(COMPLETE_FILE): die(COMPLETE_FILE, "does not exist")

VERBOSE = False

#output file directory
MSCAC_PREFILTER_DIR_NAME = "mscac-prefilter"
OFN_DIR=os.path.join(HOME_DIR,MSCAC_PREFILTER_DIR_NAME)
if not os.path.exists(OFN_DIR): die("OFN_DIR", OFN_DIR, "does not exist")

# where to rsync output file for gradapps
CSLAB_USERID = 'matz@apps1.cs.toronto.edu'
    
#obscure python way of deleting chars from unicode strings..
translation_table_to_delete_chars = dict.fromkeys(map(ord, '!@#$;"'), None)

def parse_rhs_profile_data_line(line):
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
                map[fields[0]] = True
            else:
                map[fields[0]] = False
    return map

from enum import IntEnum
class GradAppsField(IntEnum):
    "enum reverse engineering internal gradapps data fields"
    # danger this depends on knowledge of internal gradapps data layout
    UNI_1   = 29       # in UI: Academic History: University 1 Name and Location
    UNI_2   = 87
    UNI_3   = 97
    OVERALL_AVG_1 = 36 # Academic History: University 1 Overall Average
    OVERALL_AVG_2 = 92
    OVERALL_AVG_3 = 102
    GENDER = 338
    SGS_NUM = 342
    DCS_STATUS  = 363
    DCS_UNION_INSTITUTION = 364
    PREFILTER_STATUS = 418
    #GPA_1   = 35      # Academic History: University 2 Final Year Average
    #GPA_2   = 92   

def dict_from_profile_data_file(fn):
    "turn a profile.data file into a dictionary with only a few fields"
    #TODO: using a dict is ugly. I'm sure there are fancy libs to do this pretty
    #VERBOSE = True
    if VERBOSE: print(fn)
    with open(fn,"r") as profile_data_file:
        import re
        rec = {}
        for line in profile_data_file:
            for gf in GradAppsField:
                if re.search("sp" + str(int(gf)) + "-value", line):
                    rhs = parse_rhs_profile_data_line(line)
                    rec[gf] = rhs
                    if VERBOSE: print("line: ", line.strip(),"matches:",gf,rhs)
        return rec

def parse_dir_path_for_app_number(path):
    "we grub out the app number by cracking open the dir path to the profile.data file"
    try:
        l = path.split("public_html/data")
        d = l[1].split("/")
        app_num = d[1]
        return  app_num
    except:
        print("failed: split on public_html/data of ", path)
        exit(3)

def concoct_profile_data_file_name_from_app_number(app_num):
    """concoct full path of profile.data file from app_num.
       Depends on inside knowledge of how gradapps stores its stuff"""
    profile_data_fn = os.path.join(MSCAC_PROFILE_DATA_ROOT_DIR,app_num,"profile.data")
    assert os.path.exists(profile_data_fn)
    return profile_data_fn

def build_dict_of_dicts(list_of_app_numbers):
    """read the listed app_num's, concoct the path to the profile.data file and turn the data there into a dict"""
    profile_data_by_app_number = {}
    for app_num in list_of_app_numbers:
        d = dict_from_profile_data_file(concoct_profile_data_file_name_from_app_number(app_num))
        profile_data_by_app_number[app_num] = d
    return profile_data_by_app_number

def list_of_app_numbers(fn_of_app_numbers):
    """read the listed app_num's, concoct the path to the profile.data file and turn the data there into a dict"""
    list_of_app_numbers  = []
    try:
         with open(fn_of_app_numbers, "r") as in_file:
             for l in in_file:
                 app_num = l.strip()
                 list_of_app_numbers.append(app_num)
    except:
         print(fn_file_list, "failed to open for read? really? bail!")
         import traceback
         traceback.print_exc(file=sys.stdout)
         exit(3)
         return None
    return list_of_app_numbers

def parse_positional_args():
    "parse the command line parameters of this program"
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "fn_of_list_of_app_nums",
        help="""likely fn containing find . -name profile.data | sed for numbers.
        See find-profile-data-app-numbers.sh
        Note if fn given is -NNN it means app_number NNN, if just - prompts for number        
        """
        )
    parser.add_argument(
        "uni_filter_regexp", help="university to filter by"
        )
    parser.add_argument(
        "dcs_app_status_stem", help="stem of name that non-rejected applications will have ``dcs application status'' gradapps field"
        )

    args = parser.parse_args()
    return (args.fn_of_list_of_app_nums, args.uni_filter_regexp,args.dcs_app_status_stem)

def fn(n,nn):
    "concoct full path to transcript, cv, sop files in papers dir"
    return os.path.join(MSCAC_PAPERS_DIR, str(n), "file" + n + "-" + str(nn) + ".pdf")

if __name__ == '__main__': 
    import sys
    import os
    import re
    #duplicate. sorta. so works on mac and windows laptops
    for dir in [TOOLS_DIR]:
        sys.path.append(dir)
    (fn_app_num_list,uni_filter_regexp,dcs_app_status_stem) = parse_positional_args()

    completed_app_dict = completed_dict_from_applicationStatus_file(COMPLETE_FILE)

    import datetime
    now = datetime.datetime.now()
    fn_suffix = "-%s-%s-%s_%s:%s" % ( now.year, now.month, now.day, now.hour, now.minute)
    # DCS application status field of non-rejected apps will be set to this
    dcs_app_status = dcs_app_status_stem + fn_suffix

    #out of control parm parsing. can do - or -123 or -"123 456"
    if fn_app_num_list.startswith('-'):
        if len(fn_app_num_list)>1:
            fields = fn_app_num_list[1:].split(" ")
            if len(fields) == 1:
                app_num = fn_app_num_list[1:]
                app_num_list = [ app_num]
            else:
                app_num_list = fields
        else:
            app_num = input("enter app_number to filter > ")
            app_num_list = [ app_num]
    else:
        app_num_list = list_of_app_numbers(fn_app_num_list)
        
    app_num_to_profile_data = build_dict_of_dicts(app_num_list)

    if VERBOSE: print("app_num_to_profile_data",app_num_to_profile_data)

    #TODO this re-sorts by GPA. bug? maybe should leave sort by app_num_list as above
    app_num_list = []
    for app_num in app_num_to_profile_data.keys():
        profile_data = app_num_to_profile_data[app_num]
        institution = profile_data[GradAppsField.DCS_UNION_INSTITUTION]
        if VERBOSE: print(uni_filter_regexp, institution)
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
                print("skip", app_num, "because transcript does not exist",transcript_fn)
            elif not os.path.exists(sop_fn):
                print("skip", app_num, "because SOP does not exist")
            elif not os.path.exists(cv_fn):
                print("skip", app_num, "because CV does not exist")
            else:
                app_num_list.append(app_num)

    def extract_gpa(profile_data, u_field_name,gpa_field_name):
        if not u_field_name in profile_data.keys():
            return None
        uni = profile_data[u_field_name]
        if not re.search(uni_filter_regexp, uni): 
            return None
        if not gpa_field_name in profile_data:
            return None
        gpa_str = profile_data[gpa_field_name]
        try:
            return float(gpa_str)
        except:
            return None

    def extract_gpa_from_multiple_fields(profile_data):
        gpa1 = extract_gpa(profile_data, GradAppsField.UNI_1,GradAppsField.OVERALL_AVG_1)
        if gpa1:
            return gpa1
        gpa2 = extract_gpa(profile_data, GradAppsField.UNI_2,GradAppsField.OVERALL_AVG_2)
        if gpa2:
            return gpa2
        gpa3 = extract_gpa(profile_data, GradAppsField.UNI_3,GradAppsField.OVERALL_AVG_3)
        if gpa3:
            return gpa3
        
        return None
        
    #try and sort app_num_list by GPA
    def extract_gpa_for_sorted(profile_data):
        gpa = extract_gpa_from_multiple_fields(profile_data)
        if gpa:
            return gpa
        else:
            print("grade field parsing failed, using zero")
            return 0.0

    # warning, this depends on secret knowledge of gradapps status codes
    # (the int values depend on the order of some radio button that Lloyd set up)
    # TODO: build this from enum
    prefilter_status_map = {
        1: "Reject",
        2: "Pass-Star",
        3: "Pass-VGE",
        4: "NCS-Reject",
        5: "NCS-Pass",
        6: "Pass-Unsure",
        7: "Pass-Good",
        8: "NCS-Star",
        }
        
    def extract_prefilter_status(profile_data):
        "map the prefilter status value extracted from gradapps to its string name"
        try:
            return prefilter_status_map[int(profile_data[GradAppsField.PREFILTER_STATUS])]
        except:
            return "-"

    def pretty_print_app_list(app_num_to_profile_data_dict,num_list,after_map):
        "print the list of applicants to filter, or just after filtering"
        # TODO: figure out better way to do nasty after_map thing (needed to reuse this code to pretty print after menu)
        print("\n\n===============================\nAPPS matching: ",uni_filter_regexp)
        for app_num in num_list:
            profile_data = app_num_to_profile_data_dict[app_num]
            if after_map:
                sgs_num = profile_data[GradAppsField.SGS_NUM]
                if sgs_num in after_map:
                    prefilter_status = after_map[profile_data[GradAppsField.SGS_NUM]]
                else:
                    prefilter_status = "Skip" #skipped making decision, so nothing in map
            else:
                prefilter_status = extract_prefilter_status(profile_data)
            print(app_num,
                      profile_data[GradAppsField.GENDER],
                      "%11s"   % prefilter_status,
                      "%5.1f" % extract_gpa_for_sorted(profile_data),
                      profile_data[GradAppsField.SGS_NUM],
                      profile_data[GradAppsField.DCS_UNION_INSTITUTION].rstrip('|')
                      )
            
        print("===============================\n")
        
    def write_to_new_file(header_line, fn,dict):
        """write all lines out to a new file name"""
        #TODO: rename new_csv_file
        if os.path.exists(fn):
            os.system("mv %s %s" % (fn, "/tmp"))
        #print("existing %s moved to /tmp" % fn)
        with open(fn,'w') as new_file:
            print(header_line,file=new_file)
            for k in dict.keys():
                line = k + "," + str(dict[k])
                #print(line)
                print(line,file=new_file)

    app_num_list = sorted(app_num_list,
                          key=lambda app_num: extract_gpa_for_sorted(app_num_to_profile_data[app_num]),
                          reverse=True
                          )
    pretty_print_app_list(app_num_to_profile_data,app_num_list,None)

    try:
        print("prefilter above " + str(len(app_num_list)) + " applications?")
        print("matching filter:", uni_filter_regexp)
        print("setting DCS application status field stem: " + dcs_app_status )
        response = input("enter to continue, q to exit > ")
    except:
        response = None
        import traceback
        traceback.print_exc(file=sys.stderr)
        die("oops")
        
    if response == None or (len(response) > 0 and not response.lower().startswith("y")):
        die("actually entering any char bails out.. only hitting enter alone continues.. :)")

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


    from menu import PrefilterMenu

    # what to display in menu
    menu_line_dict = { 's' : "Pass-Star:    Star applicant pass prefilter. maybe early admission",
                           'v' : "Pass-VGE:     Very Good applicant. pass prefilter",
                           'g' : "Pass-G:       Good applicant. pass prefilter",
                           'u' : "Unsure:       whether this applicant should pass prefilter",
                           'r' : "Reject:       Reject application. fails prefilter",
                           'x' : "NCS-Reject:   not enough CS. Fails prefilter",
                           'y' : "NCS-Pass:     not enough CS but stellar enough to pass prefilter",
                           'z' : "NCS-Star:     not enough CS.. yet stellar",
                           'S' : "SKIP setting Prefilter_Status"
                        }
    #order to display menu items in 
    response_code_list = ['r', 's','v','g','u','x','y','z','S']

    #map responses to gradapps prefilter status column values
    gradapps_response_map = { 's' : "Pass-Star",
                           'v' : "Pass-VGE",
                           'g' : "Pass-G",
                           'u' : "Unsure",
                           'r' : "Reject",
                           'x' : "NCS-Reject",
                           'y' : "NCS-Pass",
                           'z' : "NCS-Star",
                        }
    

    import uuid #universal unique resource naming thingy
    s = str(uuid.uuid4())
    OFN_basename = "dcs-prefilter-" + s + ".csv"
    OFN = os.path.join(OFN_DIR,OFN_basename)
    BFN_basename = dcs_app_status + s + ".csv"
    BFN = os.path.join(OFN_DIR,BFN_basename)
    if os.path.exists(BFN):
        die("Sorry, " + BFN_basename + " file already exists")

    assert not os.path.exists(OFN)
    write_to_new_file("testwrite",OFN,{}) #test write junk to OFN to make sure have perms and all that
    write_to_new_file("testwrite",BFN,{}) #test write junk to OFN to make sure have perms and all that
    
    #########
    # main loop asking for decisions and writing them (paranoidly) away
    #########
    decisions = {}
    dcs_status_map = {}
    dcs_status_map_ix = 0
    for app_num in app_num_list:
        #concoct path of app_num "papers"
        # file-NNN-1.pdf is transcript
        sop_fn =  fn(app_num,1)
        cv_fn =  fn(app_num,2)
        transcript_fn =  fn(app_num,3)
        print(os.path.basename(sop_fn),os.path.basename(cv_fn),os.path.basename(transcript_fn))
        os.system(VIEWER  + " " + sop_fn + " " + cv_fn + " " + transcript_fn)
        print('user_ref=$(cat /tmp/user_ref) && open "https://confs.precisionconference.com/~mscac20/submissionProfile?paperNumber=' + app_num +'&userRef=$user_ref"')
        resp = ""
        while True:
            print("choose dcs prefilter status for application >>>",app_num,"<<< from menu below")
                        
            ########## menu for actual decision 
            prompt = "%s)% 5.2f enter a letter > " % (str(app_num), extract_gpa_for_sorted(app_num_to_profile_data[app_num]))
            menu = PrefilterMenu(response_code_list, menu_line_dict , prompt)
            
            resp = menu.menu()
            if resp == None:
                print("\n\nwonky reponse (interrupt key pressed?) from menu",resp)
                continue
            
            if resp.startswith('S'):
                print("okay, skipping", app_num)
                break ######### goto next application (or once did) 
            
            gradapps_response = gradapps_response_map[resp]
            #print("resp:", resp, gradapps_response)

            if gradapps_response == None:
                print("gotta choose something here. looping back to same application")
                continue

            try:
                profile_data = app_num_to_profile_data[app_num]
                decisions[profile_data[GradAppsField.SGS_NUM]] = gradapps_response
                #TODO: fix this searching through string value for state
                if re.search("Reject", gradapps_response):
                    print("skip adding", app_num, "to dcs_status_map because rejected")
                else:
                    status = "%s-%02d" % (dcs_app_status, dcs_status_map_ix)
                    dcs_status_map[profile_data[GradAppsField.SGS_NUM]] = status
                    write_to_new_file(dcs_app_status_stem,BFN, dcs_status_map)
                    dcs_status_map_ix += 1
                                
                ########## paranoidly, write every time
                # megaparanoid would be to copy file each time to tmp
                write_to_new_file(uni_filter_regexp,OFN, decisions) # 
            #except:
            except Exception as e:
                input("hello2")
                print(e)
                import traceback
                traceback.print_exc(file=sys.stderr)
                print(OFN, "something when wrong writing.. please try enter", resp,"again")
                print("""Note: if you get stuck looping in here only way out is to control-z and kill this job""")
                resp = ""
                continue
            break

    pretty_print_app_list(app_num_to_profile_data,app_num_list,decisions)

    #########
    # rest of script largely BS for convenience putting the output somewhere useful
    #########
    print("\n=========================")
    os.system("cat " + OFN)
    os.system("ls -l " + OFN)
    print("""next import these prefilter decisions into the gradapps system:
    1. copy/rsync files to apps1 
    2. run curl commands to gradapps server to update dcs application status and prefilter status columns""")
    
    dest = "%s:%s/" % (CSLAB_USERID, MSCAC_PREFILTER_DIR_NAME)
    rsync_cmd = "rsync  %s %s %s" %  (OFN, BFN, dest)

    #magic URL's configured into gradapps to upload data into fields
    URL_TEMPL='https://confs.precisionconference.com/~mscac20/uploadApps?config=%s&pass=StayorGo'
    CURL_TEMPL = 'curl -F appsFile="@mscac-prefilter/%s" "%s"'
    curl_cmd =  CURL_TEMPL % ( OFN_basename, URL_TEMPL % "prefilter" )
    curl_dcsstatus_cmd =  CURL_TEMPL % ( BFN_basename, URL_TEMPL % "dcsstatus" )

    # probably will need ssh config support or will prompt for password
    print(rsync_cmd)
    #print("ssh qew", "'" + curl_cmd + "'") #gross quoting, sorry
    print("=========================\n")
    resp = input("hit Enter to exec rsync above (control-c only way to skip rsync) > ")
    if not resp.startswith('s'):
        os.system(rsync_cmd)

    print("check that rsync'd files made it..")
    os.system("ssh %s ls -ltr %s/" % (CSLAB_USERID, MSCAC_PREFILTER_DIR_NAME))

    #print("\nnow ssh to", CSLAB_USERID, "and curl file to gradapps\n\n")
    ssh_cmd = "ssh -tt %s '%s'" % (CSLAB_USERID, curl_cmd )
    ssh_dcsstatus_cmd = "ssh -tt %s '%s'" % (CSLAB_USERID, curl_dcsstatus_cmd)
    print(ssh_cmd)
    print(ssh_dcsstatus_cmd)
    resp = input("hit enter to curl the prefilter choices to gradapps server.. > ")
    os.system(ssh_cmd)
    os.system(ssh_dcsstatus_cmd)

    # something missing i think it must be the form id. fiddle more later
    # print("..or probably better if you are on a unix machine..")
    # # ssh -tt forces allocation of "pseudo terminal" so that curl's nattering makes it back
    # print('\n\ncat ~/mscac-prefilter/%s | ssh -tt qew curl -F - "%s"' % (OFN_basename,URL))
