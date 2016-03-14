#!/usr/bin/evn python
""" 
Command-line utility for administrative task
"""

import os
import sys

if __name__ == "__main__":

    os.environ.setdefault(
        "MOLNFRAMEWORK_SETTINGS_MODULE",
        "sample.settings"
    )

    from molnframework.core.management import execute_command_line

    execute_command_line(sys.argv)



