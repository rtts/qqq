#!/usr/bin/env python
from django.core.management import execute_from_command_line, setup_environ
try:
    import settings # Assumed to be in the same directory.
except ImportError:
    import sys
    sys.stderr.write("Error: Manage.py can't find the file 'settings.py' in the directory containing %r. It appears you've customized things.\nYou'll have to run django-admin.py, passing it your settings module.\n(If the file settings.py does indeed exist, it's causing an ImportError somehow.)\n" % __file__)
    sys.exit(1)

if __name__ == "__main__":
    # I changed this to be able to have a project as well as an app named qqq
    setup_environ(settings, 'settings')
    execute_from_command_line()
