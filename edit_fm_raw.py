import re
import os
from tkinter.filedialog import askopenfilenames
import tkinter

tkinter.Tk().withdraw()
conversions_dir = "converted"
filenames = askopenfilenames(initialdir=os.path.dirname(os.path.realpath(__file__)),
                             filetypes = (("raw files","*.raw"),("all files","*.*")))

for i, filename in enumerate(filenames):
    [fileroot, filename] = os.path.split(filename)
    CONVERSION_DIR = os.path.join(fileroot, conversions_dir)
    if not os.path.exists(CONVERSION_DIR):
        os.mkdir(CONVERSION_DIR)
    outputname = os.path.join(CONVERSION_DIR, filename)
    print("Processing {} into {}...".format(filename, outputname))
    FLAG = True
    with open(os.path.join(fileroot, filename),  mode='rb') as f:
        with open(outputname,  mode='wb') as o:
            for line in f:
                line = line.decode(encoding='ansi')
                # Remove 4 characters from the header xml entry.
                if line.strip().startswith("<Header Copyright="):
                    line = line.replace('Norway', 'No')
                # # Make edits to the Channel xml entry
                if line.strip().startswith("<Channel ") and FLAG:
                    m = re.findall('(PulseDuration="[^"]*)"', line)[0]
                    line = re.sub('(PulseDuration="[^"]*)"', m + ';0"', line)
                    m = re.findall('(PulseDurationFM="[^"]*)"', line)[0]
                    line = re.sub('(PulseDurationFM="[^"]*)"', m + ';0"', line)
                    FLAG = False
                o.write(bytes(line, encoding='ansi'))
