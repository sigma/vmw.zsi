#! /usr/bin/env python

# This script does not use 2.x features so that you can build an RPM
# on a system that doesn't have 2.x installed (e.g., basic RedHat).

import ConfigParser, sys, time

cf = ConfigParser.ConfigParser()
cf.read('setup.cfg')

major = cf.getint('version', 'major')
minor = cf.getint('version', 'minor')
release = cf.getint('bdist_rpm', 'release')

if '--incr' in sys.argv:
    release = release + 1
    cf.set('bdist_rpm', 'release', release)
    f = open('setup.cfg', 'w')
    cf.write(f)
    f.close()

if '--pyver' in sys.argv:
    f = open('ZSI/version.py', 'w')
    f.write("# Auto-generated file; do not edit\n")
    f.write("Version = (%d, %d, %d)\n" % (major, minor, release))
    f.close()

if '--texver' in sys.argv:
    f = open('doc/version.tex', 'w')
    f.write('% Auto-generated file; do not edit\n')
    f.write(time.strftime('\\date{%B %d, %Y}\n', time.localtime()))
    f.write('\\release{%d.%d.%d}\n' % (major, minor, release))
    f.write('\\setshortversion{%d.%d}\n' % (major, minor))
    f.close()
