#!/usr/bin/env python
import git
import os
from time import mktime

import github3

from classwerk.utils import *

def add_subparser(parser, subparser):
    parser = subparser.add_parser("download-submissions", help='download releases from student repos', parents=[parser])
    parser.add_argument('-o', '--output', help='output directory', required=True)
    parser.add_argument('-t', '--tag', help='tag to download', required=True)
    parser.set_defaults(command=download_submissions)

def download_submissions(args, handle, **kwargs):
    if not os.path.isdir(args.output):
        print Colors.error("Output directory must exist!")
        sys.exit(1)
    print "Saving submissions into %s" % os.path.abspath(args.output)

    c = get_config(args.config)
    org = handle.organization(c['organization'])
    all_repos = org.repositories()

    teams = filter_teams(c['teams'], args.filter)

    i = 1
    for repo in org.repositories():
        
        tag = False
        if 'prefix' in c:
            name = "%s-%s" % (c['prefix'], team)
            if repo.name.startswith(c['prefix']) and repo.name[len(c['prefix']):] in teams:
                tag = True
        else:
            name = repo.name
            if repo.name in teams:
                tag = True

        if tag:
            print "-> %s (%s/%s)" % (name, i, len(teams))
            for release in repo.releases():
                if release.name == args.tag:
                    print "  \-> %s" % Colors.success("Downloading %s (%s)"  % (release.name, release.published_at))
                    try:
                        repo.archive('tarball', os.path.join(args.output, "%s.tar.gz" % repo.name), release.tag_name)
                    except Exception as e:
                        print "  \-> Error (%s)" % e
            i += 1


