VERBOSE=False

def die(*objs):
    print("FATAL ERROR: ", *objs, file=sys.stderr)
    exit(42)

def err_msg(*objs):
    if VERBOSE: print("ERROR: ", *objs, file=sys.stderr)

import PyPDF3 #note weird name. obtained by pip3 install pypdf3
import types # for SimpleNamespace


def die(*objs):
    print("ERROR: ", *objs, file=sys.stderr)
    exit(42)

import os
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
    
def get_creation_date(info):
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
            err_msg("no creation date in info??", path, info)
            return None
    except:
        err_msg("info[CreationDate] deref throws?", info)
        return None
        
    if VERBOSE: print("datestring from info['/CreationDate'][2:-7]", datestring)
    from time import mktime, strptime
    from datetime import datetime
    try:
        ts = strptime(datestring, "%Y%m%d%H%M%S")
        dt = datetime.fromtimestamp(mktime(ts))
        return dt.date()
    except:
        err_msg("date conversion throws on", datestring)
        return None

def get_creator(info):
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
            err_msg("no Creator found in", info)
            return None
        else:
            return name
    except:
        err_msg("info[Creator] deref throws?", info)
        return None
    
def get_author(info):
    try:
        if '/Author' in info:
            name = info['/Author']
        elif 'Author' in info:
            name = info['Author']
        else:
            name = None
        if not name:
            err_msg("no Author found in", info)
            return None
        else:
            #print("Author",name)
            return name
    except:
        err_msg("info[Author] deref throws?", info)
        return None

    
def get_info_ns(path):
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
            return ns

        dict = {}
        dict["author"] = get_author(info)
        dict["creator"] = get_creator(info)
        dict["creationdate"] = get_creation_date(info)
        ns = types.SimpleNamespace(**dict)
        # print("ns.creator:", ns.creator)
        # print("ns.author:", ns.author)
        # print("ns.creationdate:", ns.creationdate)        
        return ns

def naive_get_info(path):
    "before I learned the havoc in PDF metadata keys"
    with open(path, 'rb') as f:
        my_pdf_file_reader = PyPDF3.pdf.PdfFileReader(f)
        info = my_pdf_file_reader.getDocumentInfo()
        if not info:
            return None
        print(type(info).__name__)
        print(info)
        number_of_pages = my_pdf_file_reader.getNumPages()
        author = info.author
        creator = info.creator
        producer = info.producer
        subject = info.subject
        title = info.title
        print('author:', info.author)
        print('creator:',info.creator)
        print('producer:',info.producer)
        print('subject:', info.subject)
        print('title:', info.title)
                    
def pretty_print(app_num, file_list):
    print("app_num", app_num)
    for fn in file_list:
        print("    %020s,%30s,%30s" % (
                os.path.basename(fn),
                pdf_meta_data_for_fn[fn].author,
                pdf_meta_data_for_fn[fn].creator
                ))

if __name__ == '__main__':
    import os, sys
    path = os.path.join(MSCAC_PAPERS_DIR,'326','file326-3.pdf')
    
    if False:
        print(path)
        print(get_info_ns(path))
        exit(0)

    #traverse the directory tree and collect all the PDF files under each app
    #gradapps keeps the review letters for a applicant in the data/app_num/reviews directory
    # scan the files in each app and stash the PDF meta information for each one
    
    dict = {} # maps app_num to list of files in app_num/reviews
    reviews_for_app_num = {} # maps app_num to list of files in app_num/reviews
    pdf_meta_data_for_fn = {}
    for root, dirs, files in os.walk(MSCAC_PROFILE_DATA_ROOT_DIR):
        for file in files:
            if file.endswith('pdf') or file.endswith('PDF'): 
                (dir,fn) = os.path.split(root)
                (dir2,app_num) =os.path.split(dir)
                #print(app_num)
                if not app_num in dict:
                    dict[app_num] = []
                    reviews_for_app_num[app_num] = []
                ffn = os.path.join(root, file)
                dict[app_num].append(ffn)
                reviews_for_app_num[app_num].append(ffn)
                pdf_meta_data_for_fn[ffn] = get_info_ns(ffn)

    import datetime
    creation_dates_match = {}
    creator_match = {}
    author_match = {}
    for app_num in dict:
        file_list = dict[app_num]
        if len(file_list) < 2:
            continue
        fn0 = file_list[0]
        cd0 = pdf_meta_data_for_fn[fn0].creationdate
        flg = True
        for fn in file_list:
            #print(fn,pdf_meta_data_for_fn[fn])
            d = pdf_meta_data_for_fn[fn].creationdate
            if not d or pdf_meta_data_for_fn[fn].creationdate != cd0:
                flg = False
                break
        if flg:
            creation_dates_match[app_num] = app_num
            #print("app_num", app_num, "creation dates match", cd0)
            
            cr0  = pdf_meta_data_for_fn[fn0].creator
            flg2 = True
            for fn in file_list:
                cr = pdf_meta_data_for_fn[fn].creator
                if not cr or pdf_meta_data_for_fn[fn].creator != cr0:
                    flg2 = False
                    break
            if flg2:
                creator_match[app_num] = app_num
                #print("app_num", app_num, "creator matches also", cr0)
                flg3 = True
                a0 = pdf_meta_data_for_fn[fn].author
                for fn in file_list:
                    a = pdf_meta_data_for_fn[fn].author
                    if not a or pdf_meta_data_for_fn[fn].author != a0:
                        flg3 = False
                        break
                if flg3:
                    author_match[app_num] = app_num
                    #print("app_num", app_num, "author match", a0)
                
    print("creation date, creator and author match")
    for app_num in author_match:
        pretty_print(app_num, dict[app_num])
    print("creation date, creator match")
    for app_num in creator_match:
        pretty_print(app_num, dict[app_num])
    print("creation date match")
    for app_num in creation_dates_match:
        pretty_print(app_num, dict[app_num])

    exit(0)
        
    #
    # look at every file in every app and collect the creation date of each file
    # dict_dates = {}
    # for app_num in dict.keys():
    #     file_list = dict[app_num]
    #     if VERBOSE: print(app_num)
    #     for fn in file_list:
    #         try:
    #             info_ns = get_info_ns(fn)
    #             if info_ns == None:
    #                 continue
    #             if info_ns.creationdate:
    #                 if not app_num in dict_dates:
    #                     dict_dates[app_num] = []
    #                 dict_dates[app_num].append(info_ns.creationdate)
    #                 if VERBOSE: print( app_num, os.path.basename(fn), info_ns.creationdate)
    #             else:
    #                 print( app_num, os.path.basename(fn), 'NO DATE', file=sys.stderr)
    #         except:
    #             import traceback,sys
    #             print("get_info_ns throws for", app_num, fn, file=sys.stderr)
    #             traceback.print_exc(file=sys.stderr)

    # input('ready for date search?')

    # #look at the dates and look for files that were created on same date
    # import datetime
    # for app_num in dict_dates.keys():
    #     date_list = dict_dates[app_num]
    #     if len(date_list) < 2:
    #         continue
    #     max_date = datetime.date(2018,1,1)
    #     min_date = datetime.date(2020,12,12) 
    #     for d in date_list:
    #         if d > max_date:
    #             max_date = d
    #         if d < min_date:
    #             min_date = d
    #     if max_date == min_date:
    #         for p in dict[app_num]:
    #             print (app_num,os.path.basename(p))
    #             #print(app_num, min_date, date_list, dict[app_num])


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
