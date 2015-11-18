import numpy as np
import pandas as pd

def train_test_split_index(n,test_size=0.2,seed=None):
	if(seed):
		np.random.seed(seed)
	rand_i = np.random.choice(range(n), n, replace=False)
	test_i = rand_i[range(int(round(n*test_size)))]
	train_i = rand_i[range(int(round(n*test_size)),n)]
	return train_i, test_i

def split_by_year_week(X, test_yr_wk):
	train_i = []
	test_i = []
	for i in range(X.shape[0]):
		match = False
		row_yr_wk = (X.iloc[i]['year'], X.iloc[i]['week'])
		for yr_wk in test_yr_wk:
			if row_yr_wk[0] == yr_wk[0] and row_yr_wk[1] == yr_wk[1]:
				match = True
				test_i += [i]
				break
		if not match:
			train_i += [i]
	return train_i, test_i