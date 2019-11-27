
import PyPDF3 #note weird name. obtained by pip3 install pypdf3

VERBOSE=False

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

 
def get_info(path):
    with open(path, 'rb') as f:
        my_pdf_file_reader = PyPDF3.pdf.PdfFileReader(f)
        info = my_pdf_file_reader.getDocumentInfo()
        if not info:
            return None
 
        if VERBOSE: print(info)
 
        if VERBOSE:
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
        
        #from https://stackoverflow.com/questions/16503075/convert-creationtime-of-pdf-to-a-readable-format-in-python
        if '/CreationDate' in info:
            datestring = info['/CreationDate'][2:-7]
        elif 'CreationDate' in info:
            datestring = info['CreationDate'][2:-7]
        elif '/ModDate' in info:
            datestring = info['/ModDate'][2:-7]
        elif 'ModDate' in info:
            datestring = info['ModDate'][2:-7]
        else:
            print("no creation date in info??", path)
            print("info",info)
            return None
        
    #print("datestring from info['/CreationDate'][2:-7]", datestring)
    from time import mktime, strptime
    from datetime import datetime
    try:
        ts = strptime(datestring, "%Y%m%d%H%M%S")
    except:
        print("strptime throws on", datestring)
        return None
    dt = datetime.fromtimestamp(mktime(ts))
    d = dt.date()
    if VERBOSE:
        print("creation date",d)
        os.system("ls -l " + path)
    return d

if __name__ == '__main__':
    path = os.path.join(MSCAC_PAPERS_DIR,'326','file326-3.pdf')
    print(path)
    print(get_info(path))

    dict = {}
    for root, dirs, files in os.walk(MSCAC_PROFILE_DATA_ROOT_DIR):
        for file in files:
            if file.endswith('pdf') or file.endswith('PDF'): 
                #print(root,dirs,os.path.join(root, file))
                (dir,fn) = os.path.split(root)
                #print (root,dirs,files,file,dir,fn)
                (dir2,app_num) =os.path.split(dir)
                #print (dir2,fn2)
                #input("xxxx")
                #app_num = str(os.path.basename(root))
                print(app_num)
                if not app_num in dict:
                    dict[app_num] = []
                dict[app_num].append(os.path.join(root, file))

    dict_dates = {}
    for app_num in dict.keys():
        file_list = dict[app_num]
        if VERBOSE: print(app_num)
        for fn in file_list:
            try:
                file_creation_date = get_info(fn)
                if file_creation_date:
                    if not app_num in dict_dates:
                        dict_dates[app_num] = []
                    dict_dates[app_num].append(file_creation_date)
                    if VERBOSE: print( app_num, os.path.basename(fn), file_creation_date)
                else:
                    print( app_num, os.path.basename(fn), 'NO DATE', file=sys.stderr)
            except:
                import traceback,sys
                print("get_info throws for", app_num, fn, file=sys.stderr)
                traceback.print_exc(file=sys.stderr)

    input('ready for date search?')
    
    import datetime
    for app_num in dict_dates.keys():
        date_list = dict_dates[app_num]
        if len(date_list) < 2:
            continue
        max_date = datetime.date(2018,1,1)
        min_date = datetime.date(2020,12,12) 
        for d in date_list:
            if d > max_date:
                max_date = d
            if d < min_date:
                min_date = d
        if max_date == min_date:
            for p in dict[app_num]:
                print (app_num,os.path.basename(p))
                #print(app_num, min_date, date_list, dict[app_num])


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
