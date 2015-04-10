#!/usr/bin/env python

#
# xliff-import.py project.xcodeproj xliff-export-directory
#
#  This script will import xliff files into a project. It will parse
#  the xliff files and will add the strings files into the project. The
#  strings files will be added as localized resources.
#

import glob
import sys

from mod_pbxproj import XcodeProject, PBXFileReference, PBXBuildFile

TARGETS = ["Client", "SendTo", "ShareTo"]

def get_groups(project):
    return [group for group in project.objects.values() if group.get('isa') == 'PBXGroup']

def find_group(project, path):
    for group in project.objects.values():
        if group.get('isa') == 'PBXGroup':
            if group.get('path') == path:
                return group

def find_target(project, name):
    for target in project.get_build_phases('PBXNativeTarget'):
        if target['name'] == name:
            return target

def find_resources_phase(project, target):
    if not target:
        return None
    for build_phase_id in target['buildPhases']:
        phase = project.objects[build_phase_id]
        if phase.get('isa') == 'PBXResourcesBuildPhase':
            return phase

# TODO This should come from the transformed XLIFF files
def paths_for_localized_resources(root, target_name):
    return glob.glob(root + "/" + target_name + "/*.lproj")

def add_file(project, path, parent_group):
    file_reference = PBXFileReference.Create(path)
    parent_group.add_child(file_reference)
    project.objects[file_reference.id] = file_reference
    build_file = PBXBuildFile.Create(file_reference)
    project.objects[build_file.id] = build_file
    project.modified = True
    return (file_reference, build_file)

if __name__ == "__main__":
    project = XcodeProject.Load(sys.argv[1] + "/project.pbxproj")
    if not project:
        print "Can't open ", sys.argv[1] + "/project.pbxproj"
        sys.exit(1)

    for target_name in TARGETS:
        target = find_target(project, target_name)
        if not target:
            print "Can't find target ", target_name
            sys.exit(1)

        group = find_group(project, target_name)
        if not group:
            print "Can't find group ", target_name
            sys.exit(1)

        phase = find_resources_phase(project, target)
        if not phase:
            print "Can't find 'PBXResourcesBuildPhase' phase for target ", target_name
            sys.exit(1)

        if target and group and phase:
            print paths_for_localized_resources(sys.argv[2], target_name)
            for path in paths_for_localized_resources(sys.argv[2], target_name):
                print "%s: %s" % (target_name, path)
                file_reference, build_file = add_file(project, path, group)
                phase.add_build_file(build_file)

    project.backup()
    project.save()
