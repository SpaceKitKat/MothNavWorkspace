#!/usr/bin/python3

import numpy as np
from loadYoyoData import load_data
import discretize
import pickle
import glob
import os

# ARGS: dict of trials, forest data, traj data, trial name, date time
# RETURNS: N/A
# generates discretized patches of trees from forest data for each
# point in traj data. These masks are stored in a list. Later, this
# list and mask block size are saved to a dict using trial name
# and datetime as a key.
def processTrial(trial_hash,dtree,traj,tn,dt):
   pt_cnt = 0
   bsize = 0
   # init np that can contain mats (i.e., dtype = object)
   trial = np.zeros(len(traj.values),dtype=object)
   # process other points
   for point in traj.values:
      # get scoring region, may contain trees
      [patch,sz] = discretize.get_patch(point,dtree)
      # discretize that shit
      [mask, bsize_temp] = discretize.discretize(point,patch,sz,min(dtree.r))
      bsize = max(bsize_temp,bsize)
      # save mask, trial count, and block size
      if (0 < bsize_temp):
         discretize.pack(mask,pt_cnt,trial)
      else:
         print("(!) processTrial: failed to compute mask for "+tn+"["+str(pt_cnt)+"]")

      pt_cnt += 1

   trial_hash[tn+'_'+str(dt)] = [trial,bsize]

   print(tn)
   print("len: "+str(len(trial)))

   return

# converts strings to bytes and writes them to
# a binary file generated by open('file','wb')
def writeTo(f,txt):
   f.write(bytes(txt+'\n','UTF-8'))
   return

def main():
   DATA_LOC = "../data/masks/"
   # read tree data
   dtree = load_data("csv","../data/test/csv/forest.csv")
   print( "Forest size: "+str(len(dtree.values)) )

   # check that moth data is not empty
   if(len(dtree) == 0):
      print("(!) ERROR: No tree data loaded.")
      return

   # initialize dictionary
   # key = tN, val = [trial,block_size]
   trial_hash = {}

   # files to process
   single_trials = glob.glob("/home/bilkit/Dropbox/moth_nav_analysis/data/single_trials/*.h5")
   if (len(single_trials) < 1):
      print("No trials to process.\n~~Done.")
      return
   single_trials.sort()
   print("Computing masks for:")
   for t in single_trials: print('\t'+t+'\n')

   # log processed trials in Notes file
   if (os.path.exists(DATA_LOC+"trial_log")):
      LOG = open(DATA_LOC+"trial_log",'ab') # append to file
   else:
      LOG = open(DATA_LOC+"trial_log",'wb')

   # load the first file in data dir (assume files are sorted)
   trial_cnt = 0

   mothname = ""
   filepath,desc = "",""
   for st in single_trials:
      # load trial
      raw_data = load_data("h5",st)    # check for loaded files
      print( "Processing points: "+str(len(raw_data.values)) )
      # check that moth data is not empty
      if(len(raw_data) == 0):
         print("(!) ERROR: No moth data loaded for "+st)
         continue

      new_moth = raw_data.moth_id.iloc[0]

      # processing a new moth save prev moth - skips first trial
      if (mothname != "" and mothname != new_moth):
         print(mothname+": saving "+str(trial_cnt)+" trajs in "+filepath+'/'+desc+".pickle")
         with open(filepath+'/'+desc+'.pickle', 'wb') as handle:
           pickle.dump(trial_hash, handle)
         # reset count
         trial_cnt = 0
         # reset dictionary
         trial_hash = {}

      # log trial
      if (trial_cnt == 0):
         writeTo(LOG,str(new_moth)+":")
      writeTo(LOG,"\tt"+str(trial_cnt)+" = "+str(len(raw_data.values)))

      mothname = new_moth

      # init filepath for dumping pickle files
      filepath = DATA_LOC+mothname
      if not os.path.exists(filepath):
        os.makedirs(filepath)
      # get xy data and conditions description
      traj = raw_data[['pos_x','pos_y']]
      desc = str(int(raw_data.flight_speed.iloc[0]))+'_'+\
         str(int(raw_data.fog_min.iloc[0]))+'_'+\
         str(int(raw_data.fog_max.iloc[0]))

      processTrial(trial_hash,dtree,traj,'t'+str(trial_cnt),raw_data.datetime.iloc[0])

      # update trial count
      trial_cnt += 1


   # save the last trial_hash
   with open(filepath+'/'+desc+'.pickle', 'wb') as handle:
     pickle.dump(trial_hash, handle)

   LOG.close()

   print("~~Done :)")
   return

main()


