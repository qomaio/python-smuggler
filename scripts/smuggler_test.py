from __future__ import print_function
import os

from pyhli import *
import qoma_smuggler as qm

print("\n")
qm.open_hli()

dbname = os.path.join(os.environ['FAME'],'util','driecon')
famedata = qm.read_fame(dbname)
print("\nfamedata holds {0:d} entries\n".format(len(famedata)))

print("{0:s}".format(qm.meta_to_string(famedata,'GDP')))

qm.write_fame("mycopy",famedata)

cmd = ['  open mycopy;   output<acc over>tmp.txt;   whats gdp;   output terminal;   close mycopy  ']
cfmfame ([-1], cmd)
qm.print_file('tmp.txt')

qm.close_hli()
os.remove("mycopy.db")
os.remove("tmp.txt")
print("\n")

