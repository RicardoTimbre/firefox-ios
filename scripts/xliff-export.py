#!/usr/bin/env python

#
# xliff-export.py l10n-repository export-directory
#
# Convert the l10n repository from the following format:
#
#  en/firefox-ios.xliff
#  fr/firefox-ios.xliff
#
# To the following format:
#
#  Client/en.lproj/Localizable.strings
#  Client/fr.lproj/Localizable.strings
#  ShareTo/en.lproj/Localizable.strings
#  ShareTo/fr.lproj/Localizable.strings
#  SendTo/en.lproj/Localizable.strings
#  SendTo/fr.lproj/Localizable.strings
#

import glob
import os
import sys

from lxml import etree

NS = {'x':'urn:oasis:names:tc:xliff:document:1.2'}

# Files we are interested in. It would be nice to not hardcode this but I'm not totally sure how yet.
FILES = [
    "Client/Info.plist",
    "Client/Localizable.strings",
    "Client/search.strings",
    "Extensions/SendTo/Localizable.strings",
    "Extensions/ShareTo/Localizable.strings"
]

def export_xliff_file(file_node, export_path):
    directory = os.path.dirname(export_path)
    if not os.path.exists(directory):
        os.makedirs(directory)
    with open(export_path, "w") as fp:
        for trans_unit_node in file_node.xpath("x:body/x:trans-unit", namespaces=NS):
            sources = trans_unit_node.xpath("x:source", namespaces=NS)
            targets = trans_unit_node.xpath("x:target", namespaces=NS)
            if len(sources) == 1 and len(targets) == 1:
                line = u"\"%s\" = \"%s\";\n" % (sources[0].text, targets[0].text)
                fp.write(line.encode("utf8"))

if __name__ == "__main__":

    import_root = sys.argv[1]
    if not os.path.isdir(import_root):
        print "import path does not exist or is not a directory"
        sys.exit(1)

    export_root = sys.argv[2]
    if not os.path.isdir(export_root):
        print "export path does not exist or is not a directory"
        sys.exit(1)

    for xliff_path in glob.glob(import_root + "/*/firefox-ios.xliff"):
        print "Processing ", xliff_path
        with open(xliff_path) as fp:
            tree = etree.parse(fp)
            root = tree.getroot()
            for file_node in root.xpath("//x:file", namespaces=NS):
                original = file_node.get('original')
                target_language = file_node.get('target-language')
                if original in FILES and target_language:
                    path_components = original.split(os.sep)
                    export_path = os.path.join(export_root, path_components[-2], "%s.lproj" % target_language, path_components[-1])
                    print "  Generating ", export_path
                    export_xliff_file(file_node, export_path)
