#!/usr/bin/python3

import numpy as np
from loadYoyoData import load_data
import discretize
import pickle
import glob
import os

def processTrial(trial_hash,dtree,traj,name,dt):
   cnt = 0
   # init np that can contain mats (i.e., dtype = object)
   trial = np.zeros(len(traj.values),dtype=object)
   # process other points
   for point in traj.values:
      # get scoring region, may contain trees
      [patch,sz] = discretize.get_patch(point,dtree)
      # print("\t"+str(len(patch.values))+" ts")
      # discretize that shit
      [mask, bsize] = discretize.discretize(point,patch,sz,min(dtree.r))
      # save mask
      discretize.pack(mask,cnt,trial)

      cnt += 1

   trial_hash[name+'_'+str(dt)] = trial

   print("trial #"+str(len(trial_hash)))
   print("trial pts: "+str(len(trial)))
   print("filled: "+str(cnt))

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
   trial_hash = {}

   # files to process
   single_trials = glob.glob("/home/bilkit/Dropbox/moth_nav_analysis/data/single_trials/*.h5")
   single_trials.sort()

   # log processed trials in Notes file
   if (os.path.exists(DATA_LOC+"trial_log")):
      LOG = open(DATA_LOC+"trial_log",'ab') # append to file
   else:
      LOG = open(DATA_LOC+"trial_log",'wb')

   # load the first file in data dir (assume files are sorted)
   new_trial_set = True
   cnt = 0

   mothname = ""
   filepath,desc = "",""
   for st in single_trials:
      # load trial
      dmoth = load_data("h5",st)    # check for loaded files
      print( "Processing points: "+str(len(dmoth.values)) )
      # log trial
      if (cnt == 0):
         writeTo(LOG,str(dmoth.moth_id.iloc[0])+":")
      writeTo(LOG,"\tt"+str(cnt)+" = "+str(len(dmoth.values)))

      # check that moth data is not empty
      if(len(dmoth) == 0):
         print("(!) ERROR: No moth data loaded for "+st)
         continue

      # save trial set as pickle file
      if (new_trial_set):
         new_trial_set = False
      else:
         # processing a new moth
         if (mothname != dmoth.moth_id.iloc[0]):
            print(mothname+": saving "+cnt+" trajs in "+filepath+'/'+desc+".pickle")
            # save old trial hash in mothid dir
            with open(filepath+'/'+desc+'.pickle', 'wb') as handle:
              pickle.dump(trial_hash, handle)
            # start new trial set
            new_trial_set = True
            # reset count
            cnt = 0
            # reset dictionary
            trial_hash = {}

      mothname = dmoth.moth_id.iloc[0]
      # init filepath for dumping pickle files
      filepath = DATA_LOC+mothname
      if not os.path.exists(filepath):
        os.makedirs(filepath)
      # get xy data and conditions description
      traj = dmoth[['pos_x','pos_y']]
      desc = str(int(dmoth.flight_speed.iloc[0]))+'_'+\
         str(int(dmoth.fog_min.iloc[0]))+'_'+\
         str(int(dmoth.fog_max.iloc[0]))

      processTrial(trial_hash,dtree,traj,'t'+str(cnt),dmoth.datetime.iloc[0])

      # update trial count
      cnt += 1

   # save the last trial_hash
   with open(filepath+'/'+desc+'.pickle', 'wb') as handle:
     pickle.dump(trial_hash, handle)

   LOG.close()

   print("~~Done :)")
   return

main()


