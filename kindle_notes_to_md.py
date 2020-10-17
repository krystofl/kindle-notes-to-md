#!/usr/bin/env python3
'''
Convert an HTML file of book notes exported from an Amazon Kindle
to a Markdown document
'''
import argparse
import sys
import traceback

from eglogging import *
logging_load_human_config()



class Kindle_notes:
  def __init__(self):
    '''
    args are from argparse
    '''

    self.book_title = ''
    self.author     = ''

    # only those chapters for which notes exist
    self.chapters = []

    # each chapter has notes & highlights
    # each of those has a source



  def parse_file(self, html_file: str):
    # parse an input HTML file
    ERROR("TODO")



  def write_to_file(self, outfile : str = 'output.md'):
    # write the markdown file
    ERROR("TODO")



def parse_command_line_args():

  description = "Convert an HTML file of book notes exported from an Amazon " \
                "Kindle to a Markdown document "
  parser = argparse.ArgumentParser(description = description)

  # positinal input argument
  parser.add_argument('input',
                      help = 'Input HTML file')

  parser.add_argument('-o', '--output',
                      default = 'converted.md',
                      help = 'File to which to save the Markdown document')

  args = parser.parse_args()
  return args



if __name__ == '__main__':
  try:
    args = parse_command_line_args()

    notes = Kindle_notes()
    notes.parse_file(args.input)
    notes.write_to_file(args.output)

  except Exception as ex:
    CRITICAL("Exception: {}".format(ex))
    traceback.print_exc()
    sys.exit(1)
