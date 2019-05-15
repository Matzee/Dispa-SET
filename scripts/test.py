from __future__ import division
import sys
sys.path.append("..")

import DispaSET as ds
import pandas as pd
import numpy as np

path = '../Simulations/simulation_test'
inputs, results = ds.get_sim_results(path=path, cache=True)
#print(results)
