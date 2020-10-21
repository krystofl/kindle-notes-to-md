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


class Note:
  # highlight or note
  def __init__(self):
    self.text   = '' # the book text that was highligthed
    self.note   = '' # any note I added
    self.source = '' # info about the source of this note (location etc.)



class Chapter_notes:
  def __init__(self, chapter_title = ''):
    self.title = chapter_title # name of this chapter
    self.notes = []            # list of Highlights

  def append(self, note):
    # append note to self.notes
    self.notes.append(note)



class Kindle_notes:
  def __init__(self):
    self.book_title = ''
    self.author     = ''

    # list of Chapter_notes
    self.chapter_notes = []



  def parse_file(self, html_file: str):
    # parse an input HTML file

    # read the file to a string
    with open(html_file, 'r') as fp:
      htmls = fp.read()

    # parse the string
    soup = BeautifulSoup(htmls, 'html.parser')

    # go through all the relevant parts
    all_divs = soup.find_all('div')

    # this gets built up repeatedly over several iterations of the below loop,
    # then added to the chapter notes
    new_note = None

    for div in all_divs:
      # the class of the div
      c = div['class'][0]

      try:
        div_contents = div.string.strip()
      except AttributeError as e:
        # WARN("Couldn't strip contents of {}".format(c))
        # INFO("div: {}".format(div))
        # INFO("div.contents: {}".format(div.contents))
        div_contents = None

      # handle title and author
      if c == 'bookTitle':
        self.book_title = div_contents
      elif c == 'authors':
        self.author = div_contents

      # start of chapter
      elif c == 'sectionHeading':
        # add a new empty chapter
        self.chapter_notes.append(Chapter_notes(div_contents))

      # Notes look like so:
      # <div class="noteHeading">
      # Highlight (<span class="highlight_yellow">yellow</span>) -  Location 942
      # </div>
      # <div class="noteText">
      # This is the text in the book that was highlighted.
      # </div>
      elif c == 'noteHeading':
        new_note = Note()
        new_note.source = ' '.join(div.stripped_strings)

      elif c == 'noteText':
        new_note.text = div_contents

        # add the note to the list
        self.chapter_notes[-1].append(new_note)

      # TODO: handle notes (as opposed to just highlights)


    WARN("TODO: handle notes (as opposed to just highlights)")
    return



  def write_to_file(self, outfile : str = 'output.md'):
    # write the markdown file

    # title & author
    md =  "- Meta:\n"
    md += "  - title: {}\n".format(self.book_title)
    md += "  - author: {}\n".format(self.author)
    md += "  - tags: #Books\n"

    # all the highlights
    md += "- # Raw Highlights & Notes:\n"

    # for each chapter...
    for chapter in self.chapter_notes:
      # add a new heading 1 bullet with the chapter title
      md += "  - ## {}\n".format(chapter.title)

      # for each note in the chapter...
      for note in chapter.notes:
        # add the highlighted text
        md += "    - {}\n".format(note.text)

        # add the source of the text
        md += "      - {}\n".format(note.source)

    #WARN("TODO: check if the file exists and handle as appropriate")

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
