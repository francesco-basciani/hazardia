import argparse
from hazardia.web.server import serve
if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--runtime',required=True);ap.add_argument('--port',type=int,default=8080);a=ap.parse_args();serve(a.runtime,a.port)
