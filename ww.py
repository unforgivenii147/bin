#!/data/data/com.termux/files/usr/bin/env python3

import os
import subprocess

os.chdir('.')

subprocess.run(['wheel', 'pack', '.'])

# subprocess.run(['www'])

# input('\n\n\nOK?')
