# cache_googlefonts_locally

Cache GoogleFonts resources from css or css-url to local file.

```
usage: CachedGoogleFonts.py [-h] [-o outputpath] [-p prefix] [-u URL] [-f FILEPATH] [-l FILEPATH]

Cache Google Fonts locally.

options:
  -h, --help            show this help message and exit
  -o outputpath         Specifies the output base path
  -p prefix             Specifies the prefix path of processed url
  -u URL, --url URL     Specifies a URL of Google Fonts Stylesheet to download from
  -f FILEPATH, --css FILEPATH
                        Specifies a CSS file of Google Fonts Stylesheet to process
  -l FILEPATH, --list FILEPATH
                        Specifies a file containing a list of URLs and/or CSS file
                        paths, one per line
```

Not tested in all cases, use in your own risk.

```
# help
python CachedGoogleFonts.py --help

# parse multiple url
python CachedGoogleFonts.py -u https://fonts.googleapis.com/icon?family=Material+Icons -u https://fonts.googleapis.com/css?family=Roboto:300,400,500,600,700

# parse multiple css
python CachedGoogleFonts.py -f Roboto.css -f "Roboto Mono.css"

# parse list (read once)
"""
list.txt:
https://fonts.googleapis.com/css?family=Roboto:300,400,500,600,700
https://fonts.googleapis.com/css?family=Roboto+Mono
https://fonts.googleapis.com/icon?family=Material+Icons
"""
python CachedGoogleFonts.py -l list.txt
```

For avoiding multiple fonts and stylesheets in same name, all generated file will have a random suffix in file name.
