import argparse, os, requests, random

def safe_file_name(name):
    # replace any non-ascii characters with _
    return ''.join([c if ord(c) < 128 else '_' for c in name]).replace(" ","_")

def check_file_existed_readable(filepath):
    if not os.path.isfile(filepath):
        return 1, "File not found: " + filepath
    if not os.access(filepath, os.R_OK):
        return 2, "File not readable: " + filepath
    return 0, ""

def process_url(url):
    try:
        print("Downloading " + url + "...")
        response = requests.get(url)
        if response.status_code == 200 and 'text/css' in response.headers['content-type']:
            print("Downloaded " + url + ", size="+str(len(response.text))+" bytes.")
            css_text = response.text
            return css_text
        else: raise Exception('Invalid response')
    except requests.exceptions.HTTPError as errh:
        print("HTTP Error:", errh)
        exit(1)
    except requests.exceptions.ConnectionError as errc:
        print("Error Connecting:", errc)
        exit(1)
    except requests.exceptions.Timeout as errt:
        print("Timeout Error:", errt)
        exit(1)
    except requests.exceptions.RequestException as err:
        print("Something went wrong:", err)
        exit(1)

def process_css(file):
    try:
        print("Reading " + file + "...")
        with open(file, 'r') as f:
            css_text = f.read()
            print("Read " + file + ", size="+str(len(css_text))+" bytes.")
            return css_text
    except:
        print("Error reading file:", file)

def download_into(url,path,istext=True):
    # download from url as text .css file to specified file path
    # called as download_into("http://example.com/style.css", "./style.css")
    try:
        print("Downloading " + url + " to " + path + "...")
        response = requests.get(url)
        if response.status_code == 200:
            if istext:
                css_text = response.text
                with open(path, 'w', encoding="utf8") as f:
                    f.write(css_text)
            else:
                with open(path, 'wb') as f:
                    f.write(response.content)
        else: 
            print("Error downloading " + url + " to " + path + ".")
            print("status="+str(response.status_code)+", content-type="+response.headers['content-type']+".")
            raise Exception('Invalid response')
    except requests.exceptions.HTTPError as errh:
        print("HTTP Error:", errh)
        exit(1)
    except requests.exceptions.ConnectionError as errc:
        print("Error Connecting:", errc)
        exit(1)
    except requests.exceptions.Timeout as errt:
        print("Timeout Error:", errt)
        exit(1)
    except requests.exceptions.RequestException as err:
        print("Something went wrong:", err)
        exit(1)

def css_parser(css, base="./", splited=False, prefix=""):
    #! TODO put css and fonts into folders
    name = "unknown"+str(random.randint(0, 1000000))
    sname = safe_file_name(name)
    processed = []
    lines = []
    # print("Parsing CSS...")
    for line in css.split("\n"):
        oline = line
        line = line.strip()
        # print("Parsing line: " + line)
        if line.startswith("src: url("):# src: url(URL)
            url = line[9:].split(")")[0]
            print("Found " + url + ".")
            fmt = ".woff"
            if "format(truetype)" in line or ".ttf" in line:
                fmt = ".ttf"
            elif "format(woff2)" in line:
                fmt = ".woff"
            print("Format: " + fmt)
            # 6 random letters
            rd = ''.join(random.choice('abcdefghijklmnopqrstuvwxyz') for i in range(6))
            sname = safe_file_name(name)+'_'+rd+fmt
            finfo = {"name":name, "file":sname, "url":url, "path": os.path.join(base, sname),"fmt":fmt}
            processed.append(finfo)
            download_into(url, finfo["path"], False)
            print("Downloaded " + finfo["name"] + " to " + finfo["path"] + ".")
            nurl = os.path.join(prefix,base if base != "./" else "",sname)
            lines.append(oline.replace(url, nurl))
        elif line.startswith("font-family: "):#font-family: 'Roboto';
            name = line[14:-2]
            sname = safe_file_name(name)+"_"+''.join(random.choice('abcdefghijklmnopqrstuvwxyz') for i in range(6))
            lines.append(oline)
        else: 
            lines.append(oline)
    return lines, processed, name, sname

def process(list=[], base="./", splited=False, prefix=""):
    print("Got " + str(len(list)) + " sources to process.")
    for source in list:
        print("Processing " + str(source) + "...")
        isUrl, path = source
        css = process_url(path) if isUrl else process_css(path)
        lines, processed, name, sname = css_parser(css, base, splited, prefix)
        fpath = os.path.join(base, sname+".css")
        with open(fpath, 'w', encoding="utf8") as f:
            f.write("\n".join(lines))

def startswith(text="",prefixes=[]):
    for prefix in prefixes:
        if text.startswith(prefix):
            return True
    return False


if __name__=='__main__':
    _BASEPATH = ''
    _SOURCES = []
    _SPLITED = False
    _PREFIX = ""

    parser = argparse.ArgumentParser(description='Cache Google Fonts locally.')

    parser.add_argument('-o', dest='output_path', metavar='outputpath',
                        help='Specifies the output base path')
    # parser.add_argument('-s', '--split', dest='splited', action='store_true',
    #                     help='Split files into folders based on file names')
    parser.add_argument('-p', dest='prefix', metavar='prefix',
                        help='Specifies the prefix path of processed url')
    parser.add_argument('-u','--url', dest='urls', action="append", metavar='URL',
                        help='Specifies a URL of Google Fonts Stylesheet to download from')
    parser.add_argument('-f','--css', dest='css_files', action="append", metavar='FILEPATH',
                        help='Specifies a CSS file of Google Fonts Stylesheet to process')
    parser.add_argument('-l','--list', dest='list_file', metavar='FILEPATH',
                        help='Specifies a file containing a list of URLs and/or CSS files')

    args = parser.parse_args()

    if args.output_path:
        _BASEPATH = args.output_path
    else:
        _BASEPATH = './'

    if args.prefix:
        _PREFIX = args.prefix

    # if args.splited:
    #     _SPLITED = True

    if args.urls:
        for url in args.urls:
            if url.startswith('http://') or url.startswith('https://'):
                _SOURCES.append([True, url])
            else:
                print('Invalid URL: ' + url)
                exit(1)

    if args.css_files:
        for css_file in args.css_files:
            err, msg = check_file_existed_readable(args.list_file)
            if err:
                print(msg)
                exit(1)
            _SOURCES.append([False, css_file])

    if args.list_file:
        err, msg = check_file_existed_readable(args.list_file)
        if err:
            print(msg)
            exit(1)
        with open(args.list_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line.startswith('http://') or line.startswith('https://'):
                    _SOURCES.append([True, line])
                else:
                    err, msg = check_file_existed_readable(args.list_file)
                    if err:
                        print(msg)
                        exit(1)
                    _SOURCES.append([False, line])

    process(_SOURCES, _BASEPATH, _SPLITED, _PREFIX)
