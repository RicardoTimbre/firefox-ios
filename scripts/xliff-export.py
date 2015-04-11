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

def export_xliff_file(file_node, export_path, target_language):
    directory = os.path.dirname(export_path)
    if not os.path.exists(directory):
        os.makedirs(directory)
    with open(export_path, "w") as fp:
        for trans_unit_node in file_node.xpath("x:body/x:trans-unit", namespaces=NS):
            sources = trans_unit_node.xpath("x:source", namespaces=NS)
            targets = trans_unit_node.xpath("x:target", namespaces=NS)

            # Special hack for en-US.
            if target_language == "en":
                targets = sources

            if len(sources) == 1 and len(targets) == 1:
                notes = trans_unit_node.xpath("x:note", namespaces=NS)
                if len(notes) == 1:
                    line = u"/* %s */\n" % notes[0].text
                    fp.write(line.encode("utf8"))
                line = u"\"%s\" = \"%s\";\n\n" % (sources[0].text, targets[0].text)
                fp.write(line.encode("utf8"))

def original_path(root, target, original):
    parts = original.split(os.sep)
    lproj = "%s.lproj" % target_language
    return os.path.join(root, parts[-2], lproj, parts[-1])

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
        print "Exporting", xliff_path
        with open(xliff_path) as fp:
            tree = etree.parse(fp)
            root = tree.getroot()

            # Make sure there are <file> nodes in this xliff file.
            file_nodes = root.xpath("//x:file", namespaces=NS)
            if len(file_nodes) == 0:
                print "  ERROR: No translated files. Skipping."
                continue

            # Take the target language from the first <file>. Not sure if that
            # is a bug in the XLIFF, but in some files only the first node has
            # the target-language set.
            source_language = file_nodes[0].get('source-language')
            target_language = file_nodes[0].get('target-language')
            if not target_language:
                # Special hack for en-US. It does not have target-language set but
                # we still want to write out string files for it. Because if we do
                # not, english systems will default to some random language.
                if "en-US" in xliff_path:
                    target_language = 'en'
                else:
                    print "  ERROR: Missing target-language. Skipping."
                    continue

            # Export each <file> node as a separate strings file under the
            # export root.
            for file_node in file_nodes:
                original = file_node.get('original')
                if original in FILES:
                    export_path = original_path(export_root, target_language, original)
                    print "  Writing", export_path
                    export_xliff_file(file_node, export_path, target_language)
