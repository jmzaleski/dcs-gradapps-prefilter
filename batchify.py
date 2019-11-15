def parse_positional_args():
    "parse the command line parameters of this program"
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "fn_of_list_of_files",
        help="batchify list of files"
        )

    args = parser.parse_args()
    return args.fn_of_list_of_files

def file_list(fn):
    "read list of file names"
    list = []
    with open(fn,"r") as apf:
        for line in apf:
            list.append(line.strip())
    return list


if __name__ == '__main__': 
    import sys
    import os
    import re
    fn = parse_positional_args()
    batch_ix = 0
    for fn in file_list(fn):
        #print(fn)
        ix = 0
        with open(fn,"r") as af:
            hdr_line = next(af) #skip header
            for line in af:
                if re.search("Reject",line):
                    continue
                if re.search("Unsure",line): #sure?
                    continue
                fields = line.strip().split(",")
                print("%s,batch-%0d2-%0d2" % (fields[0], batch_ix, ix) )
                ix += 1
        batch_ix += 1
            
        

