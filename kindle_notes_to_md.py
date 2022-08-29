#!/usr/bin/env python3
'''
Convert an HTML file of book notes exported from an Amazon Kindle
to a Markdown document
'''
import argparse
import os
import sys
import traceback
from collections import OrderedDict

import pyperclip
from bs4 import BeautifulSoup
from eglogging import *

logging_load_human_config()


class Note:
  # highlight, possibly including a note
  def __init__(self):
    self.text = ''  # the book text that was highlighted
    self.note = ''  # any note I added
    self.source = ''  # info about the source of this note (location etc.)
    self.location = None  # int Location as given by Kindle


class Chapter_notes:
  def __init__(self, chapter_title=''):
    self.title = chapter_title  # name of this chapter
    self.notes = OrderedDict()  # Location (int) -> [Note]

  def get_last_note(self):
    # returns the most recently-added note
    return self.notes[next(reversed(self.notes))]


class Kindle_notes:
  def __init__(self):
    self.book_title = ''
    self.author = ''

    # list of Chapter_notes
    self.chapter_notes = []

  def parse_file(self, html_file: str):
    # parse an input HTML file

    # read the file to a string
    with open(html_file, 'r', encoding='utf8') as fp:
      htmls = fp.read()

    # parse the string
    soup = BeautifulSoup(htmls, 'html.parser')

    # go through all the relevant parts
    all_divs = soup.select('[class]')

    # this gets built up repeatedly over several iterations of the below loop,
    # then added to the chapter notes
    wip_note = None

    last_note_type = ''  # should be either Highlight or Note

    for div in all_divs:
      # the class of the div
      c = div['class'][0]

      try:
        div_contents = div.get_text().strip().replace(u' \xa0', '')
      except AttributeError as e:
        # This happens, but we handle it as appropriate elsewhere
        # WARN("Couldn't strip contents of {}".format(c))
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
      # Highlight (<span class="highlight_yellow">yellow</span>) -  Location 180
      # </div>
      # <div class="noteText">
      # Product management is a strange role.
      # </div>
      # <div class="noteHeading">
      # Note -  Location 180
      # </div>
      # <div class="noteText">
      # Strange roles are for strange people!
      # </div>
      elif c == 'noteHeading':
        # first figure out what location this note/highlight is for
        source = ' '.join(div.stripped_strings)

        try:
          location = int(source.split()[-1])
          # INFO("Location {}".format(location))

          # the first word of the div should be either Highlight or Note
          last_note_type = source.split()[0]

          # if it's a "Note", add it to the previous highlight
          # because that's what the note is about
          # sometimes the exported notes have slightly different locations for
          #   highlights and notes on long passages
          if last_note_type == 'Note':
            try:
              wip_note = self.chapter_notes[-1].get_last_note()
            except Exception as e:
              WARN("Exception getting last-inserted note: {}".format(e))
              wip_note = None

          # make a new note for Highlights
          else:
            wip_note = None

          # if we don't have a note, create one
          if wip_note is None:
            wip_note = Note()
            wip_note.location = location

            # this happens twice for notes, but that's OK
            wip_note.source = ' '.join(div.stripped_strings)

            # add this WIP note to the dictionary
            self.chapter_notes[-1].notes[location] = wip_note

        except Exception as e:
          WARN("Couldn't figure out location from {}: {}".format(source, e))

      # now we have the highlight or note text
      elif c == 'noteText':

        # fix a result of a misplaced </div> that new Kindle App (1.38.0) adds in noteHeading
        # should work fine too, when Amazon will fix their app (split will just return single elem list)
        div_contents = div_contents.split('\n')[0]

        # save as either Highlight or Note, as appropriate
        if last_note_type == 'Highlight':
          wip_note.text = div_contents

        elif last_note_type == 'Note':
          wip_note.note = div_contents

  def output_md(self, args):

    # title & author
    md = "- Meta:\n"
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
      for location in chapter.notes:
        note = chapter.notes[location]

        # add the highlighted text
        md += "    - {}\n".format(note.text)

        # if there is a note, add it in bold
        if note.note != '':
          md += "      - **{}**\n".format(note.note)

        if args.location:
          # add the source of the text
          md += "      - {}\n".format(note.source)

    if args.clipboard:
      pyperclip.copy(md)

      INFO("Copied the output to clipboard", LOG_COLORS['GREEN'])
    else:
      # write the markdown file
      if not os.path.exists(args.output) or args.override:
        with open(args.output, 'w', encoding='utf8') as fp:
          fp.write(md)

        INFO("Wrote the output to {}".format(args.output), LOG_COLORS['GREEN'])
      else:
        INFO("Could not save .md file, because it already exists. Use --override flag.", LOG_COLORS['RED'])

  def copy_to_clipboard(self):
    """Copy result directly into clipboard"""


def parse_command_line_args():
  description = "Convert an HTML file of book notes exported from an Amazon " \
                "Kindle to a Markdown document "
  parser = argparse.ArgumentParser(description=description)

  # positinal input argument
  parser.add_argument('input',
                      help='Input HTML file')

  parser.add_argument('-nl', '--no-location',
                      dest='location',
                      action='store_false',
                      default=True,
                      help='Whether to skip export of location of notes/highlights')

  parser.add_argument('-c', '--clipboard',
                      action='store_true',
                      help='Use to export .md directly to the clipboard instead of file')

  parser.add_argument('-y', '--override',
                      action='store_true',
                      default=False,
                      help='Whether to override .md file in case if one already exists')

  parser.add_argument('-o', '--output',
                      default='',
                      help='A file to which save the Markdown document')

  args = parser.parse_args()

  # if no output passed, output .md file next to original one
  args.output = os.path.splitext(args.input)[0] + '.md'

  return args


if __name__ == '__main__':
  try:
    args = parse_command_line_args()

    notes = Kindle_notes()
    notes.parse_file(args.input)
    notes.output_md(args)

  except Exception as ex:
    CRITICAL("Exception: {}".format(ex))
    traceback.print_exc()
    sys.exit(1)
