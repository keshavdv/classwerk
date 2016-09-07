#!/usr/bin/env python
import argparse
import importlib
import os
import sys
sys.dont_write_bytecode = True

from configparser import ConfigParser
from github3 import GitHub, GitHubEnterprise

from classwerk import cmds
from classwerk.utils import Colors
from classwerk.utils import CREDENTIALS_FILE
from classwerk.utils import generate_auth_token
from classwerk.utils import modules_in_pkg


def parse_args():
	parser = argparse.ArgumentParser(description='Github Administration tools')
	base_parser = argparse.ArgumentParser(add_help=False)

	subparsers = parser.add_subparsers(help='[-h, --help] for subcommand help')
	base_parser.add_argument('-c', '--config', help='path to class config file (default: class.yml)', default="class.yml")
	base_parser.add_argument('-p', '--profile', help='Specify auth profile to use', default="default")
	base_parser.add_argument('-f', '--file', help='Specify auth file to use', default=CREDENTIALS_FILE)
	base_parser.add_argument('-F', '--filter', nargs='*', dest='filter', help='filter by team name', default=None)

	for command in sorted(modules_in_pkg(cmds)):
		module = importlib.import_module('classwerk.cmds.%s' % command)
		module.add_subparser(base_parser, subparsers)

	return parser.parse_args()


def main():
	args = parse_args()
	c = ConfigParser()

	# Check if token already exists or generate one
	c.read(args.file)

	if args.profile not in c.sections():
		print Colors.warn("Could not find profile '%s' in '%s', generating new credentials." % (args.profile, args.file))
		token = generate_auth_token(args.profile, args.file)
		c.read(args.file)

	profile = c[args.profile]

	enterprise_url = profile.get('url', None)
	token = profile.get('token')
	
	if enterprise_url:
		g = GitHubEnterprise(enterprise_url, token=token)
	else:
		g = GitHub(token=token)
		
	args.command(args, handle=g)


if __name__ == '__main__':
	main()

