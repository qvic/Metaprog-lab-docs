import argparse

from parser.parser import Parser

parser = argparse.ArgumentParser(description='Documentation generator for Java.')
parser.add_argument('directory', type=str, help='Directory with sources. Should contain "java/" directory.')
parser.add_argument('-v',  dest='verbose', help='Verbose output', action='store_true')

args = parser.parse_args()
Parser.parse(args.directory, args.verbose)