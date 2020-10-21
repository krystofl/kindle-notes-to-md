#!/usr/bin/env python3
'''
Convert an HTML file of book notes exported from an Amazon Kindle
to a Markdown document
'''
import argparse
from html.parser import HTMLParser
import sys
import traceback

from bs4 import BeautifulSoup

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
    # each is a (title, [notes/highlights]) pair
    self.chapters = []

    # each chapter has notes & highlights
    # each of those has a source



  def parse_file(self, html_file: str):
    # parse an input HTML file

    # read the file to a string
    with open(html_file, 'r') as fp:
      htmls = fp.read()

    # parse the string
    soup = BeautifulSoup(htmls, 'html.parser')

    # go through all the relevant parts
    all_divs = soup.find_all('div')
    for div in all_divs:
      # the class of the div
      c = div['class'][0]

      # handle title and author
      if c == 'bookTitle':
        self.book_title = div.string.strip()
      elif c == 'authors':
        self.author = div.string.strip()

      # handle notes & highlights
      elif c == 'sectionHeading':
        # add a new empty chapter
        self.chapters.append((div.string.strip(), []))




  def write_to_file(self, outfile : str = 'output.md'):
    # write the markdown file

    # title & author
    md =  "- Meta:\n"
    md += "  - title: {}\n".format(self.book_title)
    md += "  - author: {}\n".format(self.author)
    md += "  - tags: #Books\n"

    # all the highlights
    md += "- # Raw Highlights & Notes:\n"
    for chapter in self.chapters:
      md += "  - ## {}\n".format(chapter[0])

    WARN("TODO: check if the file exists and handle as appropriate")

    with open(outfile, 'w') as fp:
      fp.write(md)

    INFO("Wrote the output to {}".format(outfile), LOG_COLORS['GREEN'])



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
