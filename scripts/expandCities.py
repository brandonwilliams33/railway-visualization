"""Persist each city's fact snapshot before moving to the next city."""
from acquireCity import acquire
import argparse
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('cities',nargs='+');p.add_argument('--province',default='zhejiang');p.add_argument('--name',default='浙江');a=p.parse_args()
 for city in a.cities:
  print('\nCITY',city,flush=True)
  acquire(a.province,city,a.name)
