import argparse

from parser.parser import Parser

parser = argparse.ArgumentParser(description='Documentation generator for Java.')

parser.add_argument('input', type=str, help='Directory or file path with sources.')
parser.add_argument('output_directory', type=str, help='Directory with sources. Should contain "java/" directory.')

parser.add_argument('--shallow', dest='shallow', help='Scan only files in passed directory.', action='store_true')
parser.add_argument('--name', type=str, dest='project_name', help='Project name, showed on index page.')
parser.add_argument('--version', type=str, dest='project_version', help='Project version, showed on index page.')
parser.add_argument('-v', dest='verbose', help='Verbose output', action='store_true')

args = parser.parse_args()

Parser.parse(args.input, args.output_directory, args.project_name, args.project_version, args.verbose, args.shallow)
