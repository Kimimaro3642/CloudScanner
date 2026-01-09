import argparse
from .core import reporter
from .scan import run_azure

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--out",default="reports/run.html")
    ap.add_argument("--json",default="reports/run.json")
    a=ap.parse_args()
    f=run_azure()
    reporter.write_json(f,a.json)
    reporter.write_html("azure",f,a.out)
    print("Done, findings:",len(f))
if __name__=="__main__": main()
