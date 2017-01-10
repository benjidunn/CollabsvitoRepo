from __future__ import print_function

""" downloaded from http://xbmc-addons.googlecode.com/svn/addons/ """
""" modified by Collabsvito """
""" addons.xml generator """

import os
import sys
import zipfile
import re
import time
import shutil
import xml.etree.ElementTree as ET
 
# Compatibility with 3.0, 3.1 and 3.2 not supporting u"" literals
if sys.version < '3':
    import codecs
    def u(x):
        return codecs.unicode_escape_decode(x)[0]
else:
    def u(x):
        return x

sys.stdout=open("Z_logging(DELETE).txt","w")
 
class Generator:
    """
        Generates a new addons.xml file from each addons addon.xml file
        and a new addons.xml.md5 hash file. Must be run from the root of
        the checked-out repo. Only handles single depth folder structure.
    """

    def __init__(self):
        # generate files
        self._generate_addons_file()
        self._generate_md5_file()
        # notify user
        print ('Finished updating ~ addons.xml and addons.xml.md5 ~ files')
        print ('>>>')
 
    def _generate_addons_file(self):
        # addon list
        addons = os.listdir(".")
        print ('There are - '+ str(len(addons)) +' - Files and Folders in RootDirectory')
        # final addons text
        addons_xml = u("<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"yes\"?>\n<addons>\n")
        # loop thru and add each addons addon.xml file
        for addon in addons:
            try:
                # skip any file or .svn folder or .git folder
                if (not os.path.isdir(addon) or addon == ".svn" or addon == ".git"): continue
                # create path
                _path = os.path.join(addon, "addon.xml")
                # skip path if it has no addon.xml
                if not os.path.isfile(_path): continue
                print ('Found ADDON = '+_path)
                # split lines for stripping
                xml_lines = open(_path, "r").read().splitlines()
                # new addon
                addon_xml = ""
                # loop thru cleaning each line
                for line in xml_lines:
                    # skip encoding format line
                    if (line.find("<?xml") >= 0): continue
                    # add line
                    if sys.version < '3':
                        addon_xml += unicode( line.rstrip()+"\n", "UTF-8")
                    else:
                        addon_xml += line.rstrip()+"\n"
                # we succeeded so add to our final addons.xml text
                addons_xml += addon_xml.rstrip()+"\n"
            except Exception as e:
                print (e)
                # missing or poorly formatted addon.xml
                print ('Excluding %s for %s' %(_path, e))
        # clean and add closing tag
        addons_xml = addons_xml.strip() + u("\n</addons>")
        # save file
        self._save_file(addons_xml.encode("UTF-8"), file="addons.xml")
 
    def _generate_md5_file(self):
        # create a new md5 hash
        try:
            import md5
            m = md5.new(open("addons.xml", "r").read()).hexdigest()
        except ImportError:
            import hashlib
            m = hashlib.md5(open("addons.xml", "r", encoding="UTF-8").read().encode("UTF-8")).hexdigest()
        # save file
        try:
            self._save_file(m.encode("UTF-8"), file="addons.xml.md5")
        except Exception as e:
            # oops
            print ('An error occurred creating addons.xml.md5 file!\n%s' %e)
 
    def _save_file(self, data, file):
        try:
            # write data to the file (use b for Python 3)
            open(file, "wb").write(data)
        except Exception as e:
            # oops
            print ('An error occurred saving %s file!\n%s' %(file, e))

def zipfolder(foldername, target_dir, zips_dir):
    zipobj = zipfile.ZipFile(zips_dir+foldername, 'w', zipfile.ZIP_DEFLATED)
    rootlen = len(target_dir) + 1
    for base, dirs, files in os.walk(target_dir):
        for file in files:
            fn = os.path.join(base, file)
            zipobj.write(fn, os.path.join(foldername[:-4],fn[rootlen:]))
    zipobj.close()


if (__name__ == "__main__"):
    # start
    Generator()
    #rezip files an move
    print ('STARTING zip file creation ...')
    rootdir = sys.path[0]
    zipsdir = rootdir+'\\packages'

    filesinrootdir = os.listdir(rootdir)
    for x in filesinrootdir:
        if re.search("plugin|repository|script", x):
            foldertozip = rootdir+'\\'+x
            zipfilename = x+'.zip'
            zipfilenamefirstpart = zipfilename[:-4]
            zipfilenamelastpart = zipfilename[len(zipfilename)-4:]
            zipsfolder = 'packages'
            zipsfolder = os.path.join(zipsfolder,x)
            zipsfolder = os.path.normpath(zipsfolder)+os.sep
            if not os.path.exists(zipsfolder):
                os.makedirs(zipsfolder)
                print ('Directory doesn\'t exist, creating: '+zipsfolder)
            #check if and move changelog, fanart and icon to zipdir
            filesinfoldertozip = os.listdir(foldertozip)
            for y in filesinfoldertozip:
                print ('processing file: '+os.path.join(rootdir,x,y))
                if re.search("addon.xml", y): # get version number of plugin
                    tree = ET.parse(os.path.join(rootdir,x,y))
                    root = tree.getroot()
                    for elem in root.iter('addon'):
                        print (elem.tag +': '+ elem.attrib['version'])
                        version = '-'+elem.attrib['version']
                if re.search("changelog|icon|fanart", y):
                    shutil.copyfile(os.path.join(rootdir,x,y),os.path.join(zipsfolder,y))
                    print ('COPYING '+ y +' to '+ zipsfolder)
            zipfolder(zipfilenamefirstpart+zipfilenamelastpart, foldertozip, zipsfolder)
            print ('ZIPPING '+ zipfilename +' renaming and moving to '+ zipfilenamefirstpart+version)
            print ('>>>')
#            print 'zipfolder',zipsfolder
#            print 'foldertozip',foldertozip
            shutil.move( os.path.join(os.path.join(os.getcwd(),zipsfolder),zipfilenamefirstpart+zipfilenamelastpart),os.path.join(os.path.join(os.getcwd(),zipsfolder),zipfilenamefirstpart+version+zipfilenamelastpart))
print ('Good Bye - every Process has FINISHED')
sys.stdout.close()