""" Python utility functions """
from datetime import datetime
from sys      import argv

def script_name():
    """ return name of script run """
    return argv[0]

def print_all_vars(globls:dict, title=None, trailer=None,
    print_time:bool = True, print_script:bool = True,
    fmt_value:str = "%20s", fmt_name:str = "%30s: ", vars_exclude=None,
    out_file=None, caller=None, end=None):
    """ print time, script name, and variable names and values. Typically called
    with print_all_vars(globals()) """
    if out_file:
        sys.stdout = open(out_file, "w")
    if title:
        print(title)
    if print_time:
        print(fmt_name%"time" + datetime.now().strftime("%Y-%m-%d %H:%M"))
    if caller:
        print(fmt_name%"function", caller)
    if print_script:
        print(fmt_name%"script" + script_name())
    if not vars_exclude:
        vars_exclude = []
    for key, value in globls.copy().items():
        vl = str(value)
        if (not key.startswith("df") and not key.startswith("__")
            and not vl.startswith("<") and not vl.startswith("%")
            and not key.startswith("print") and not key.startswith("describe")
            and not key.startswith("write") and not key.startswith("plot")
            and not key.startswith("run_")
            and not key.startswith("nprint")
            and not key.endswith("_pdf") and not key.endswith("funcs")
            and not vl.startswith("typing.")
            and key not in vars_exclude
            and key not in ["timings", "start", "time_after_imports", "WEEKLY",
                "total_profit_str"]):
            if isinstance(value, dict):
                print(fmt_name%key, "dict")
                for k, v in value.items():
                    print(fmt_name%"", f'{k}: {v}')
            else:
                print(fmt_name%key, fmt_value%value, sep="")
    if trailer:
        print(trailer,end="")
    if end:
        print(end=end)
    if out_file:
        sys.stdout.close()
        sys.stdout = sys.__stdout__ # Reset stdout to its default value

def index(xlist, value):
    """ return the position of value in xlist, -1 if not found """
    if value in xlist:
        return xlist.index(value)
    else:
        return -1
