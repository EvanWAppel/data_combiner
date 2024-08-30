import os
from datetime import datetime
import pandas as pd
import re
#import win32com.client
import openpyxl as xl

def logger():
    if os.environ['OS'] == "Windows_NT":
        log = r"c:\Users\{}\spend_model\log.txt".format(os.environ['USERNAME'])
    elif os.environ['OS'] == 'POSIX':
        log = r"/log.txt".format(os.environ['HOME'])
    else:
        print(f"{datetime.today()} >>> Here's a nickel, kid. Go and buy yourself a better computer.")
    return log

def entry(text):
    log = logger()
    message = f">>> {datetime.today()} ]|[ {text}"
    with open(log,'a') as l:
        print(message,file=l)
    print(message,flush=True)
    l.close()

def assumptions():
    if os.environ['OS'] == "Windows_NT":
        if os.path.isdir(r""):
            root = r""
        elif os.path.isdir(r""):
            root = r""
        else:
            root = input("Enter the file path for the Brand Spend Data Model")
            # modification: added MARKET to file path plus some other cool shit
    if os.environ['os'] == "POSIX":
        root = "/usr_data/MARKET/Marketing Analytics/Brand Analysis/04 - Dashboards/Brand Spend Data Model"
    source = root+r"\Source Data"
    target = root+r"\Target Data"
    imp = pd.read_excel(source+r'\IMP FACTOR.xlsx')
    budget = pd.read_excel(source+r'\BrandQuaterlyGoalsByChannel.xlsx')
    entry("Assumptions loaded.")
    entry(f"Source is {source}")
    entry(f"Target is {target}")
    return {"root":root,"source":source,"target":target,"imp":imp,"budget":budget}

def file_gatherer(source, criteria) -> list:
    targets = []
    for i in os.listdir(source):
        x = re.search(criteria,i)
        if x is not None:
            targets.append(i)
    entry(f"Files gathered based on {criteria} applied to {source}:")
    for i in targets:
        entry(f"TARGET FILE NAME: {i}")
    return targets

def data_framer(source: str = None, files: list = None, sheets= None, skiprows: int = None):
    # The list of files to be fed into this function need to be all of the same data type
    dataset = pd.DataFrame()
    if isinstance(sheets,list) :
        for i in files:
            for j in sheets:
                try:
                    payload = pd.read_excel(os.path.join(source,i),sheet_name=j,skiprows=skiprows)
                    entry(f"DF from file {i} sheet {j} has len {len(payload)}")
                    dataset = pd.concat([dataset,payload])
                except Exception as e:
                    entry(f"pd.read_excel() failed on {i} with sheet {j} because of {e}") 
    elif sheets is None:
        for k in files:
            try:
                if re.search(".*csv.*",k):
                    payload = pd.read_csv(os.path.join(source,k),skiprows=skiprows)
                    entry(f"DF from file {k} has len {len(payload)}")
                elif re.search(".*xlsx.*",k):
                    payload = pd.read_excel(os.path.join(source,k),skiprows=skiprows)
                    entry(f"DF from file {k} has len {len(payload)}")
                else:
                    print("FAIL")
                #payload = pd.DataFrame(payload,index=[0])
                dataset = pd.concat([dataset,payload])
            except Exception as e:
                entry(f"pd.read_csv() failed on {k} because of {e}")
    else:
        entry(f"data_framer() was passed sheets={sheets} for files={files} of data type {type(files)}, which is not accepted.")
    entry(f"Dataset has len of {len(dataset)}")
    return dataset

def file_writer():
    pass



        