#! /usr/bin/env python
import sys, os, zipfile

vers = sys.argv[1]
base = 'skellington-' + sys.argv[1]
package = zipfile.ZipFile(base + '.zip', 'w', zipfile.ZIP_DEFLATED)
def add_files(generator):
    for dirpath, dirnames, filenames in generator:
        dirnames.remove('.svn')
        for name in filenames:
            suffix = os.path.splitext(name)[1]
            if suffix in ('.pyc', '.pyo'): continue
            if name[0] == '.': continue
            filename = os.path.join(dirpath, name)
            package.write(filename, filename.replace('skellington', base))
add_files(os.walk('skellington'))

