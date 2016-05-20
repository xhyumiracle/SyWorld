import test1
import ast
import time
import sys
import getopt

def f(h):
    print '###'
    print h
def main(argv):
    try:
        opts, args = getopt.getopt(argv[1:], ':a:v:', ['ha=', 'hv='])
        print args
    except getopt.GetoptError, err:
        print err
        print 'error!'
        sys.exit(2)
    for o, a in opts:
        if o in ('-a', '--ha'):
            print "a or ha"
            print a
        if o in ('-v', '--hv'):
            print "v or hv"
            print a
    print "asdf"


if __name__ == '__main__':
    main(sys.argv)
