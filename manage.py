#!/usr/bin/env python
import os
import sys

if __name__ == "__main__":
    #print("HERE", os.getcwd())
    #for dirname, dirnames, filenames in os.walk('.'):
    ## print path to all subdirectories first.
    # for subdirname in dirnames:
    #    print(os.path.join(dirname, subdirname))
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "website.settings")

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
