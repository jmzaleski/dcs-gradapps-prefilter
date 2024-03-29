VERBOSE=False

def die(*objs):
    "outa here. too broken to continue"
    print("FATAL ERROR: ", *objs, file=sys.stderr)
    exit(42)

def err_msg(*objs):
    print("ERROR: ", *objs, file=sys.stderr)

import PyPDF3 #note weird name. obtained by pip3 install pypdf3
import types # for SimpleNamespace
import os,sys

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

MSCAC_PROFILE_DATA_ROOT_DIR = os.path.join(MSCAC_DIR,"public_html","data")
if not os.path.exists(MSCAC_PROFILE_DATA_ROOT_DIR): die(MSCAC_PROFILE_DATA_ROOT_DIR, "does not exist")
    
def get_info_ns(path):
    "look at the pdf metadata in path and return a type.SimpleNamespace containing author, creator, creationdate"

    def pdf_warning(*objs):
        "wrapper that closes over path"
        if VERBOSE: print("PDF WARNING:", *objs, path, file=sys.stderr)
        
    def get_creation_date(info):
        "look for creation date in PDF metadata"
        #from https://stackoverflow.com/questions/16503075/convert-creationtime-of-pdf-to-a-readable-format-in-python
        try:
            if '/CreationDate' in info:
                datestring = info['/CreationDate'][2:-7]
            elif 'CreationDate' in info:
                datestring = info['CreationDate'][2:-7]
            elif '/ModDate' in info:
                datestring = info['/ModDate'][2:-7]
            elif 'ModDate' in info:
                datestring = info['ModDate'][2:-7]
            else:
                pdf_warning("no creation date in info??", info)
                return None
        except:
            pdf_warning("info[CreationDate] deref throws?", info)
            return None
        if VERBOSE: print("datestring from info['/CreationDate'][2:-7]", datestring)
        from time import mktime, strptime
        from datetime import datetime
        #TODO: import style
        try:
            ts = strptime(datestring, "%Y%m%d%H%M%S")
            dt = datetime.fromtimestamp(mktime(ts))
            return dt.date()
        except:
            pdf_warning("date conversion throws on", datestring)
            return None
        
    def get_creator(info):
        "look for creator (program that wrote the file) data in PDF metadata"
        try:
            if '/Creator' in info:
                name = info['/Creator']
            elif 'Creator' in info and len(info["Creator"])>0:
                name = info['Creator']
            elif 'Producer' in info:
                name = info['Producer']
            elif '/Producer' in info:
                name = info['/Producer']
            else:
                name = None
            if not name:
                pdf_warning("no Creator found in", info)
                return None
            else:
                return name
        except:
            pdf_warning("info[Creator] deref throws?", info)
            return None

    def get_author(info):
        "look for author data in PDF metadata"
        try:
            if '/Author' in info:
                name = info['/Author']
            elif 'Author' in info:
                name = info['Author']
            else:
                name = None
            if not name:
                pdf_warning("no Author found in", info)
                return None
            else:
                #print("Author",name)
                return name
        except:
            pdf_warning("info[Author] deref throws?", info)
            return None
        
    ######### get the metadata ######
    if VERBOSE: print("about to look for PDF metadata in", path)
    with open(path, 'rb') as f:
        try:
            my_pdf_file_reader = PyPDF3.pdf.PdfFileReader(f)
            info = my_pdf_file_reader.getDocumentInfo()
            if VERBOSE:
                print(type(info).__name__)
                print(info)
        except:
            err_msg("get_info_ns failed to open PDF file:", path)
            ns = types.SimpleNamespace()
            ns.creator = None
            ns.author = None
            ns.creationdate = None
            ns.path = path
            return ns

    dict = {}
    dict["author"] = get_author(info)
    dict["creator"] = get_creator(info)
    dict["creationdate"] = get_creation_date(info)
    ns = types.SimpleNamespace(**dict)
    ns.path = path
    if VERBOSE:
        print("ns.creator:", ns.creator)
        print("ns.author:", ns.author)
        print("ns.creationdate:", ns.creationdate)        
        print("ns.path:", ns.path)        
    return ns

def pretty_print(app_num, file_list):
    print("app_num", app_num)
    for fn in file_list:
        print("%5s,%020s,%30s,%30s" % (
                app_num,
                os.path.basename(fn),
                pdf_meta_data_for_fn[fn].author,
                pdf_meta_data_for_fn[fn].creator
                ))

def print_as_csv(app_num, file_list):
    for fn in file_list:
        print("%s,%s,%s,%s" % (
                app_num,
                os.path.basename(fn),
                pdf_meta_data_for_fn[fn].author,
                pdf_meta_data_for_fn[fn].creator
                ))

if __name__ == '__main__':
    path = os.path.join(MSCAC_PAPERS_DIR,'326','file326-3.pdf')
    
    if False:
        print(path)
        print(get_info_ns(path))
        exit(0)

    # traverse the directory tree and collect all the PDF files under each app
    # gradapps keeps the review letters for a applicant in the data/app_num/reviews directory
    # scan the files in each app and stash the PDF meta information for each one
    
    fn_for_app_num       = {} # maps app_num to list of files in app_num/reviews
    pdf_meta_data_for_fn = {} # SimpleNamespace containing PDF metadata from file
    for root, dirs, files in os.walk(MSCAC_PROFILE_DATA_ROOT_DIR):
        for file in files:
            if file.endswith('pdf') or file.endswith('PDF'): 
                (dir,fn) = os.path.split(root)
                (dir2,app_num) =os.path.split(dir)
                if not app_num in fn_for_app_num:
                    fn_for_app_num[app_num] = []
                ffn = os.path.join(root, file)
                fn_for_app_num[app_num].append(ffn)
                pdf_meta_data_for_fn[ffn] = get_info_ns(ffn)
                
    if VERBOSE:
        print("dump pdf_meta_data_for_fn{")
        for fn in pdf_meta_data_for_fn:
            print(os.path.basename(fn), pdf_meta_data_for_fn[fn])
        print("}end dump pdf_meta_data_for_fn")
        
    def write_as_csv_file(filtered_dict_of_app_num, csv_file_name):
        "use csv package to write suspect applications to csv file excel"
        import csv
        with open(csv_file_name, mode='w') as csv_file:
            csv_writer = csv.writer(csv_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            for app_num in filtered_dict_of_app_num:
                for fn in fn_for_app_num[app_num]:
                    csv_writer.writerow([app_num,os.path.basename(fn),
                                             pdf_meta_data_for_fn[fn].creationdate,
                                             pdf_meta_data_for_fn[fn].author,
                                             pdf_meta_data_for_fn[fn].creator])
        os.system("ls -l %s" % csv_file_name)


    def scan_apps(dict_on_app_num, pdf_metadata_property_getter):
        "scan the all the apps PDF files for an app looking for those that pdf_metadata_property_getter returns the same data for"
        def scan_files(fn_list, pdf_metadata_property_getter):
            "scan the all the app's PDF files looking for those that pdf_metadata_property_getter returns the same data for"
            if len(fn_list) < 2:
                return False # only one file? nothing to suspect
            fn_iter = iter(fn_list)
            x0 = pdf_metadata_property_getter(next(fn_iter))
            if not x0:
                return False
            for fn in fn_iter:
                xi = pdf_metadata_property_getter(fn)
                if not xi or xi != x0:
                    return False
            return True

        # scan the apps looking for suspicious reference files
        d = {}
        for app_num in dict_on_app_num:
            if scan_files(fn_for_app_num[app_num], pdf_metadata_property_getter):
                d[app_num] = app_num
        return d
        
    cd       = scan_apps(fn_for_app_num, lambda fn: pdf_meta_data_for_fn[fn].creationdate)
    cd_c     = scan_apps(cd,             lambda fn: pdf_meta_data_for_fn[fn].creator)
    cd_c_a   = scan_apps(cd_c,           lambda fn: pdf_meta_data_for_fn[fn].author)
    write_as_csv_file(cd, "creationdate.csv")
    write_as_csv_file(cd_c, "creationdate-creator.csv")
    write_as_csv_file(cd_c_a,"creationdate-creator-author.csv")
    a       = scan_apps(fn_for_app_num, lambda fn: pdf_meta_data_for_fn[fn].author)
    write_as_csv_file(a, "author.csv")

    def concoct_profile_log_file_name_from_app_number(app_num):
        """concoct full path of profile.data file from app_num.
           Depends on inside knowledge of how gradapps stores its stuff"""
        log_file_fn = os.path.join(MSCAC_PROFILE_DATA_ROOT_DIR,app_num,"log")
        if not os.path.exists(log_file_fn):
            die("cannot find", log_file_fn)
        assert os.path.exists(log_file_fn)
        return log_file_fn

    for app_num in a: #cd_c_a:
        pretty_print(app_num,fn_for_app_num[app_num])
        # flush python buffers or interpreter will buffer output and won't interleave with grep output
        sys.stdout.flush() 
        os.system("grep reportFinalized " + concoct_profile_log_file_name_from_app_number(app_num))
        
        
    if False: #example
        pretty_print("112",fn_for_app_num["112"])
        print(scan("112",lambda fn: pdf_meta_data_for_fn[fn].creationdate))


# PDF date/time format http://www.verypdf.com/pdfinfoeditor/pdf-date-format.htm
# (D:YYYYMMDDHHmmSSOHH'mm')

# >>> help('PyPDF3.pdf.PdfFileReader.getDocumentInfo')

# Help on function getDocumentInfo in PyPDF3.pdf.PdfFileReader:

# PyPDF3.pdf.PdfFileReader.getDocumentInfo = getDocumentInfo(self)
#     Retrieves the PDF file's document information dictionary, if it exists.
#     Note that some PDF files use metadata streams instead of docinfo
#     dictionaries, and these metadata streams will not be accessed by this
#     function.
    
#     :return: the document information of this PDF file
#     :rtype: :class:`DocumentInformation<pdf.DocumentInformation>` or ``None`` if none exists.
