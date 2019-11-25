from __future__ import print_function  #allows print as function
import sys, os.path

VERBOSE = False

def die(*objs):
    print("ERROR: ", *objs, file=sys.stderr)
    exit(42)

HOME_DIR = os.environ['HOME'] 
if not os.path.exists(HOME_DIR): die("HOME_DIR", HOME_DIR, "does not exist")

TOOLS_DIR = os.path.join(HOME_DIR,"git","dcs-gradapps-prefilter")
if not os.path.exists(TOOLS_DIR): die("TOOLS_DIR", TOOLS_DIR, "does not exist")

#where we rsync gradapps backup server to
MSCAC_DIR = os.path.join(HOME_DIR,"mscac")
if not os.path.exists(MSCAC_DIR): die(MSCAC_DIR, "does not exist")

#dir where transcripts, sop, cv live
MSCAC_PAPERS_DIR = os.path.join(MSCAC_DIR,"public_html","papers")
if not os.path.exists(MSCAC_PAPERS_DIR): die(MSCAC_PAPERS_DIR, "does not exist")

#dir where application dirs containing profile.data live
MSCAC_PROFILE_DATA_ROOT_DIR = os.path.join(MSCAC_DIR,"public_html","data")
if not os.path.exists(MSCAC_PROFILE_DATA_ROOT_DIR): die(MSCAC_PROFILE_DATA_ROOT_DIR, "does not exist")

#CSV file university rankings are read from
UNI_RANKING_CSV=os.path.join(MSCAC_DIR,"uni-ranking.csv")
if not os.path.exists(UNI_RANKING_CSV): die(UNI_RANKING_CSV, "university ranking file does not exist")

#shell script to fire up viewers on PDF files
VIEWER = os.path.join(TOOLS_DIR,"view-files.sh")
if not os.path.exists(VIEWER): die(VIEWER, "does not exist")

GREP_SGS_NUM = os.path.join(TOOLS_DIR,"grep-sgs-num.sh")
if not os.path.exists(GREP_SGS_NUM): die(GREP_SGS_NUM, "does not exist")
    
#file listing which apps are complete
COMPLETE_FILE = os.path.join(MSCAC_DIR,"public_html/admin/applicationStatus")
if not os.path.exists(COMPLETE_FILE): die(COMPLETE_FILE, "does not exist")

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


def uni_ranking_dict_from_csv_file(fn,has_header):
    "reads csv file mapping university name to (claire's) ranking"
    import functools, csv
    #example line in CSV file:
    #UNIV OF TORONTO,1,top rank (canada),Canada,
    with open(fn) as csv_file:
        csv_file_reader = csv.reader(csv_file, delimiter=',', quotechar='"',dialect=csv.excel_tab)
        if has_header:
            next(csv_file_reader)
        def acc(d, fields):
            d[fields[0]] = fields[1] 
            return d
        return  functools.reduce(acc, csv_file_reader, {})


def completed_dict_from_applicationStatus_file(fn):
    "reads applicationStatus files and stashes away which apps are complete"
    with open(fn,"r") as apf:
        import re
        map = {}
        for line in apf:
            fields = line.split(" ")
            assert len(fields) == 2
            #TODO: re.compile ?
            if re.search("complete",fields[1]):
                map[fields[0]] = True
            else:
                map[fields[0]] = False
    return map

from enum import IntEnum
class GradAppsField(IntEnum):
    "enum records reverse engineering of internal gradapps data fields"
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
    #TODO: maybe types.SimpleNamespace(**d)
    #TODO: maybe csv.DictReader ?
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

def concoct_profile_data_file_name_from_app_number(app_num):
    """concoct full path of profile.data file from app_num.
       Depends on inside knowledge of how gradapps stores its stuff"""
    profile_data_fn = os.path.join(MSCAC_PROFILE_DATA_ROOT_DIR,app_num,"profile.data")
    if not os.path.exists(profile_data_fn):
        die("cannot find", profile_data_fn)
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

def parse_args():
    "parse the command line parameters of this program"
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument( "uni_filter_regexp", help="university to filter by" )
    #TODO: change to --skip-sort with default true
    parser.add_argument( "--sort", action="store_false",
                         help="without option menu sorted by grade. --sort leaves menu in order app_nums listed")
    parser.add_argument( "--skip-prefiltered", action="store_true",
                         help="without option already prefiltered applications appeard. --prefiltered leaves out already prefiltered applications")
    parser.add_argument("--app_num_list", action="append", nargs="+", type=str, help="list of app numbers to prefilter")
    
    ns = parser.parse_args() # returns a namespace.
    #butcher app_num_list. (this hackery proves I don't understand the use of add_argument)
    if ns.app_num_list:
        assert len(ns.app_num_list) == 1
        s = ns.app_num_list[0][0]
        print(s)
        ns.app_num_list = s.split()
    if VERBOSE: print(ns)
    return ns

def pdf_file_no_for_app(app_number,nn):
    "concoct full path to transcript, cv, sop files for an app_num in papers dir"
    return os.path.join(MSCAC_PAPERS_DIR, str(app_number), "file" + app_num + "-" + str(nn) + ".pdf")

def shorten_uni_name(uni_name):
    "take a few common substrings out of institution name"
    return ( uni_name.replace("UNIVERSITY","")
            .replace("UNIV","")
            .replace("university","")
            .replace("University","") 
            .replace("INST","").replace("INSTITUTE","").replace("Institute","").replace("institute","")
            .replace("INST","").replace("INSTITUTION","").replace("Institution","").replace("institution","")
            .replace(" of","").replace(" OF","")
            .replace("Science","Sci").replace("science","sci")
            .replace("Technology","Tech").replace("technology","tech")
            .lstrip(" ")
            .rstrip(" ")
            .replace(" ","_") )

    

def extract_gpa(profile_data, u_field_name,gpa_field_name):
    "WIP extract gpa from text field attempting to work around common applicant mistakes"
    if not u_field_name in profile_data.keys():
        return None
    uni = profile_data[u_field_name]
    # if not re.search(uni_filter_regexp, uni): 
    #     return None
    if not gpa_field_name in profile_data:
        return None
    gpa_str = profile_data[gpa_field_name]
    try:
        return float(gpa_str)
    except:
        #some students take it into their heads to enter "3.999/4", or "89% (first class honours)"
        fields = re.compile("[%/]").split(gpa_str)
        if len(fields) == 2:
            try:
                return float(fields[0])
            except:
                return None
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

def extract_uni(profile_data, u_field_name):
    "WIP "
    if not u_field_name in profile_data.keys():
        return None
    return profile_data[u_field_name]
    
def extract_uni_name_from_multiple_fields(profile_data):
    #TODO: make this into map
    uni1 = extract_uni(profile_data, GradAppsField.UNI_1)
    if uni1:
        return uni1
    uni2 = extract_uni(profile_data, GradAppsField.UNI_2)
    if uni2:
        return uni2
    uni3 = extract_uni(profile_data, GradAppsField.UNI_3)
    if uni3:
        return uni3
    return "-"
    
#try and sort app_num_list by GPA
def extract_gpa_for_sorted(profile_data):
    gpa = extract_gpa_from_multiple_fields(profile_data)
    if gpa:
        return gpa
    else:
        #print("grade field parsing failed, using zero")
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

def pretty_print_app_list(app_num_to_profile_data_dict,num_list,file_whatsit,session_prefilter_decision_map):
    "print the list of applicants to filter, or just after filtering"
    # TODO: figure out better way to do nasty session_prefilter_decision_map thing (needed to reuse this code to pretty print after menu)
    #TODO: rename file_whatsit
    print("\n\n===============================\nAPPS matching: ",uni_filter_regexp)
    for app_num in num_list:
        profile_data = app_num_to_profile_data_dict[app_num]
        sgs_num = profile_data[GradAppsField.SGS_NUM]
        if session_prefilter_decision_map:
            # run after decisions have been made this session
            if sgs_num in session_prefilter_decision_map:
                prefilter_status = session_prefilter_decision_map[sgs_num]
            else:
                prefilter_status = "Skip" #skipped making decision, so nothing in map
        else:
            # being run before starting the session, no decisions yet
            prefilter_status = extract_prefilter_status(profile_data)

        print(app_num,
                  profile_data[GradAppsField.GENDER],
                  "%11s"   % prefilter_status,
                  "%5.1f" % extract_gpa_for_sorted(profile_data),
                  sgs_num,
                  profile_data[GradAppsField.DCS_UNION_INSTITUTION].rstrip('|'),
                  file=file_whatsit
                  )
            
    print("===============================\n")
        
def write_to_new_file(header_line, fn,dict):
    """write all lines out to a new file name"""
    #TODO: use csv.writer ?
    #TODO: rename new_csv_file
    if VERBOSE: print("write_to_new_file:",fn,dict)
    if os.path.exists(fn):
        os.system("mv %s %s" % (fn, "/tmp"))
        if VERBOSE: print("existing %s moved to /tmp" % fn)
    with open(fn,'w') as new_file:
        print(header_line,file=new_file)
        for k in dict.keys():
            line = k + "," + str(dict[k])
            if VERBOSE: print("write_to_new_file:",line)
            print(line,file=new_file)


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

def prefilter_status_field(profile_data):
    "the prefilter status field we will set for the application has school and gpa"
    uni_name = extract_uni_name_from_multiple_fields(profile_data)
    gpa = extract_gpa_from_multiple_fields(profile_data)
    if gpa == None:
        gpa = 0.0
    status = "%s-%.1f" % (shorten_uni_name(uni_name),gpa)
    return status

def prefilter_prompt(app_num,profile_data,ix,n):
    "prompt line with a bunch of very compressed info. gender, school, rank, gpa "
    uni_name = extract_uni_name_from_multiple_fields(profile_data)
    try:
        ranking = int(uni_ranking[uni_name])
    except:
        ranking = 1001
    gpa = extract_gpa_from_multiple_fields(profile_data)
    if gpa == None:
        gpa = 0.0
    prompt = "%d)%d/%d %s %s-%03d-%.1f" % (app_num, ix, n, profile_data[GradAppsField.GENDER],
                                                  shorten_uni_name(uni_name),
                                                  ranking, gpa)
    #print("prompt", prompt)
    return prompt

    
def prefilter_info_panel(app_num,profile_data,ix,n):
    "compact, few line, application history"
    def extract_uni_info_tuple( which_uni, which_mark):
        "return tuple fetching info about app's schooling "
        uni_name = extract_uni(profile_data, which_uni)
        gpa  = None
        rank = None
        if uni_name:
            gpa = extract_gpa(profile_data, which_uni, which_mark)
        try:
            rank = int(uni_ranking[uni_name])
        except:
            return (uni_name, gpa, 1001) #ie sentinel (bogus) rank
        return (uni_name,gpa,rank)
    def append_to_panel(ix,tuple,fmt):
        "refactor format code until it looks like this"
        (uni1,gpa1,rank1) = tuple
        if uni1:
            return fmt  % (ix, uni1,gpa1,rank1)
        else:
            return "%-5d-\n" % ix
    
    HDR_FMT = "%-5s%-40s %5s %5s\n"
    FMT     = "%-5d%-40s %5s %5s\n"
    
    panel = "institution info from app %d:\n" % (int(app_num))
    panel += append_to_panel( "="*4, ("="*40, "="*5, "="*5), HDR_FMT)
    panel += append_to_panel( "#", ("Institution", "GPA", "rank"), HDR_FMT)
    panel += append_to_panel( "-"*4, ("-"*40, "-"*5, "-"*5), HDR_FMT)
    panel += append_to_panel(1, extract_uni_info_tuple(GradAppsField.UNI_1, GradAppsField.OVERALL_AVG_1),FMT)
    panel += append_to_panel(2, extract_uni_info_tuple(GradAppsField.UNI_2, GradAppsField.OVERALL_AVG_2),FMT)
    panel += append_to_panel(3, extract_uni_info_tuple(GradAppsField.UNI_3, GradAppsField.OVERALL_AVG_3),FMT)
    panel += append_to_panel( "="*4, ("="*40, "="*5, "="*5), HDR_FMT)
    return panel

def  batch_hack(app_num_to_profile_data, completed_app_dict):
    "this printed out a csv file which we used to clean up the dcs application status fields"
    app_num_list = []
    for app_num in app_num_to_profile_data.keys():
        profile_data = app_num_to_profile_data[app_num]
        institution = profile_data[GradAppsField.DCS_UNION_INSTITUTION]
        if VERBOSE: print("institution",uni_filter_regexp, institution)
        if not app_num in completed_app_dict.keys():
            if VERBOSE:print("skip", app_num, "because not complete")
            continue
        elif len(profile_data[GradAppsField.PREFILTER_STATUS]) == 0:
            if VERBOSE: print("skip", app_num, "because prefilter_status not set")
            continue
        app_num_list.append(app_num)
    #print(app_num_list)
    #print(prefilter_status_map[1])
    for app_num in app_num_list:
        profile_data = app_num_to_profile_data[app_num]
        prefilter_dec = int(profile_data[GradAppsField.PREFILTER_STATUS])
        if prefilter_dec == 1 or prefilter_dec == 4:
            continue #skip reject
        sgs_num = profile_data[GradAppsField.SGS_NUM]
        #print(sgs_num, prefilter_status_map[prefilter_dec],prefilter_status_field(profile_data))
        print("%s,%s" % (sgs_num, prefilter_status_field(profile_data)))
        
    exit(0)
    
def find_app_numbers_in_filesystem(public_html_data_dir):
    """find all the app numbers in the system by recursing the tree. each dir containing
    a file called profile.data identifies an application"""
    import os
    app_nums = []
    for root, dirs, files in os.walk(public_html_data_dir):
        for file in files:
            if file == "profile.data":
                if VERBOSE:
                    print(root,dirs,os.path.join(root, file))
                    print(os.path.basename(root))
                app_nums.append(str(os.path.basename(root)))
    return app_nums

if __name__ == '__main__': 
    import sys,os,re,functools
    #duplicate. sorta. so works on mac and windows laptops
    for dir in [TOOLS_DIR]:
        sys.path.append(dir)
        
    cmd_line_parm_ns = parse_args()
    cmdline_app_num_list = cmd_line_parm_ns.app_num_list
    uni_filter_regexp = cmd_line_parm_ns.uni_filter_regexp

    #read csv file ranking universities
    uni_ranking = uni_ranking_dict_from_csv_file(UNI_RANKING_CSV,has_header=False)
    
    completed_app_dict = completed_dict_from_applicationStatus_file(COMPLETE_FILE)

    import datetime
    now = datetime.datetime.now()
    fn_suffix = "-%s-%s-%s_%s:%s" % ( now.year, now.month, now.day, now.hour, now.minute)

    if cmd_line_parm_ns.app_num_list:
        #just the apps that were passed on command line
        app_num_list = cmd_line_parm_ns.app_num_list
    else:
        #go find them all
        app_num_list = find_app_numbers_in_filesystem("./public_html/data")

    if VERBOSE: print("app_num_list",app_num_list)
        
    #build a dict for each profile.data directory
    app_num_to_profile_data = build_dict_of_dicts(app_num_list)

    if VERBOSE: print("app_num_to_profile_data",app_num_to_profile_data)

    # this is the spot to write hacky scripts that see all the data..
    ## batch_hack(app_num_to_profile_data, completed_app_dict)
    
    # now that have read all the data, filter per command line options into app_num_list
    app_num_list = []
    for app_num in app_num_to_profile_data.keys():
        profile_data = app_num_to_profile_data[app_num]
        institution = profile_data[GradAppsField.DCS_UNION_INSTITUTION]
        if VERBOSE: print("institution",uni_filter_regexp, institution)
        #TODO: re.compile ?
        if not re.search(uni_filter_regexp, institution):
            if VERBOSE: print("skip", app_num, "because", institution, "not matched by", uni_filter_regexp)
        else:
            sop_fn =  pdf_file_no_for_app(app_num,1)
            cv_fn =  pdf_file_no_for_app(app_num,2)
            transcript_fn =  pdf_file_no_for_app(app_num,3)
            if not app_num in completed_app_dict.keys():
                if VERBOSE:print("skip", app_num, "because not complete")
                continue
            elif cmd_line_parm_ns.skip_prefiltered and len(profile_data[GradAppsField.PREFILTER_STATUS]) > 0:
                if VERBOSE: print("skip", app_num, "because prefilter_status already set")
                continue
            elif not os.path.exists(transcript_fn):
                print("skip", app_num, "because transcript does not exist",transcript_fn)
            elif not os.path.exists(sop_fn):
                print("skip", app_num, "because SOP does not exist")
            elif not os.path.exists(cv_fn):
                print("skip", app_num, "because CV does not exist")
            else:
                app_num_list.append(app_num)


    if cmd_line_parm_ns.sort:
        #TODO this re-sorts by GPA. bug? maybe should leave sort by app_num_list as above
        app_num_list = sorted(app_num_list,
                          key=lambda app_num: extract_gpa_for_sorted(app_num_to_profile_data[app_num]),
                          reverse=True
                          )
    
    # check for repeat prefiltering. grep for app_nums in OFN_DIR
    buf = " "
    for app_num in app_num_list:
        buf += str(app_num_to_profile_data[app_num][GradAppsField.SGS_NUM]) + " "
    os.system(GREP_SGS_NUM + buf)
    
    pretty_print_app_list(app_num_to_profile_data,app_num_list,sys.stdout,None)

    try:
        print("prefilter above " + str(len(app_num_list)) + " applications?")
        print("matching filter:", uni_filter_regexp)
        response = input("enter to continue, q to exit > ")
    except:
        response = None
        import traceback
        traceback.print_exc(file=sys.stderr)
        die("oops")
        
    if response == None or (len(response) > 0 and not response.lower().startswith("y")):
        die("actually entering any char bails out.. only hitting enter alone continues.. :)")

    


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
    BFN_basename = "dcs-app-status-"+ s + ".csv"
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
        sop_fn =  pdf_file_no_for_app(app_num,1)
        cv_fn =  pdf_file_no_for_app(app_num,2)
        transcript_fn =  pdf_file_no_for_app(app_num,3)
        print(os.path.basename(sop_fn),os.path.basename(cv_fn),os.path.basename(transcript_fn))
        os.system(VIEWER  + " " + sop_fn + " " + cv_fn + " " + transcript_fn)
        print('user_ref=$(cat /tmp/user_ref) && open "https://confs.precisionconference.com/~mscac20/submissionProfile?paperNumber=' + app_num +'&userRef=$user_ref"')
        resp = ""
        while True:
            profile_data = app_num_to_profile_data[app_num]
                        
            ########## menu for actual decision
            print(prefilter_info_panel( app_num, profile_data,dcs_status_map_ix, len(app_num_list)),end='')
            
            prompt = "%s enter letter indicating prefilter_status > " % (
                prefilter_prompt(int(app_num), profile_data, dcs_status_map_ix, len(app_num_list)) )
            
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
                decisions[profile_data[GradAppsField.SGS_NUM]] = gradapps_response
                #TODO: fix this searching through string value for state
                if re.search("Reject", gradapps_response):
                    print("skip adding", app_num, "to dcs_status_map because rejected")
                else:
                    dcs_status_map[profile_data[GradAppsField.SGS_NUM]] = prefilter_status_field(profile_data)
                    write_to_new_file("dcs app status",BFN, dcs_status_map)
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

    if len(decisions) == 0:
        print("you skipped all applicants. no decisions made. exiting..")
        exit(0)

    pretty_print_app_list(app_num_to_profile_data,app_num_list,sys.stdout,decisions)

    #########
    # rest of script largely for sending decisions back to gradapps
    #########
    print("\n=========================")
    os.system("ls -l " + OFN)
    os.system("cat " + OFN)
    print("=========================\n")
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

    print(OFN,BFN)
    resp = input("hit Enter rsync to %s  > " % CSLAB_USERID)
    if resp.startswith('s'):
        os.system("ls -l %s %s" % (OFN,BFN))
        die("prefilter decisions not uploaded to gradapps")

    os.system(rsync_cmd)
    print("ls -ltr | tail -2 to see if rsync'd files made it..")
    os.system("ssh %s ls -ltr %s/ | tail -2" % (CSLAB_USERID, MSCAC_PREFILTER_DIR_NAME))

    ssh_cmd = "ssh -tt %s '%s'" % (CSLAB_USERID, curl_cmd )
    ssh_dcsstatus_cmd = "ssh -tt %s '%s'" % (CSLAB_USERID, curl_dcsstatus_cmd)

    os.system(ssh_cmd)
    os.system(ssh_dcsstatus_cmd)

    with open("log","a") as a_file_whatsit:
        import datetime
        print(datetime.datetime.now(),file=file_whatsit)
        pretty_print_app_list(app_num_to_profile_data,app_num_list,a_file_whatsit,decisions)
        print("==================================", file=file_whatsit)

