import pandas as pd
import numpy as np
from urllib.request import urlopen
import re
from io import BytesIO
from zipfile import ZipFile

def csv2other(file, format='json', skiprows=None):
    filename = file.split('.')[0]
    df = pd.read_csv(file, skiprows=skiprows)
    if format=='format':
        df.to_json(f"{filename}.json")
    elif format=='parquet':
        df.to_parquet(f"{filename}.parquet", engine="auto")
    else:
        ValueError("Invalid format specified: 'json' or 'parquet' only")

    print(f"Saved {file} as {filename}.{format}")
    return df


def open_file(path, indiv_file=None, codec='utf-8') -> str:
    '''
    Reads single text file (also within zip archive) into text blob from local path or url
    Args:
        path (str): path of text or zip file
        indiv_file (str): reads specific file within zip archive (defaults to None)
        codec (str): encoding of string (defaults to 'utf-8'). Set to None for no encoding

    Returns: text (str)
    Example:
        >>>url = 'https://www.cms.gov/Medicare/Coding/ICD9ProviderDiagnosticCodes/Downloads/ICD-9-CM-v32-master-descriptions.zip'
        >>>text = open_file(url, indiv_file='CMS32_DESC_LONG_DX.txt', codec=None)

    '''
    # if url
    if re.match(r'^http|^www.',path):
        # if zip
        if re.search('\.zip$',path):
            resp = urlopen(path)
            zipfile = ZipFile(BytesIO(resp.read()))
            if not indiv_file:
                indiv_file = re.search('/((\w|\s)*)\.zip$',path).group(1) + '.txt'
            text = zipfile.open(indiv_file,'r').read()
            print(f"Reading {indiv_file}...")
        else:
            text = urlopen(path).read()
    # if local
    else:
        f = open(path, "r")
        text = f.read()

    if codec:
        text = text.decode(codec)

    return text


def grep(file,pattern,linenum=True,indiv_file=None):
    ans=[]
    text = open_file(file,indiv_file).split("\n")
    for num, line in enumerate(text):
        if re.search(pattern,line):
            if linenum:
                ans.append(num)
#                print(num)
            else:
                ans.append(line)
#               print(line)
    if len(ans)>0:
        return ans
    else:
        print(f"No matches found in {file}!")
        return None


def parse_line(file,pattern,group=1,indiv_file=None):
    """
    Read in text file from local or url. Grep line of interest and parse string of interest using regex groups

    Args:
        file: text file path (local or url)
        pattern: regex string to look out for, include groups e.g. r'^prefix(.*)suffix$'
        group: regex group (defaults to 1)
        indiv_file: individual file to read in zip (default to infer from file name)

    Returns: string from file in group matching pattern

    Examples:
        >>> parse_line('https://download.geonames.org/export/dump/readme.txt',r'^admin1CodesASCII.txt.*Columns: (.*)$',1)
        code, name, name ascii, geonameid

    """
    text = open_file(file,indiv_file).split("\n")
    for line in text:
        match = re.search(pattern, line)
        if match:
            matched_string = match.group(group)
            return matched_string


def parse_blob(file,pattern,group=1,indiv_file=None):
    """
    Read in text file from local or url. Grep line of interest and parse string of interest using regex groups

    Args:
        file: text file path (local or url)
        pattern: regex string to look out for, include groups e.g. r'^prefix(.*)suffix$'
        group: regex group (defaults to 1)
        indiv_file: individual file to read in zip (default to infer from file name)

    Returns: string from file in group matching pattern

    Examples:
        >>> parse_blob('https://download.geonames.org/export/dump/readme.txt',r'^admin1CodesASCII.txt.*Columns: (.*)$',1)
        code, name, name ascii, geonameid

    """
    text = open_file(file,indiv_file)
    match = re.search(pattern, text)
    if match:
        matched_string = match.group(group)
        return matched_string


def force_int_or_null(x):
    try:
        return int(x)
    except:
        return np.nan


