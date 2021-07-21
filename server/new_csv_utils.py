import pandas as pd
import numpy as np
from scipy.signal import savgol_filter
import os
import cv2

# MPII : (0 - r ankle, 1 - r knee, 2 - r hip, 3 - l hip, 4 - l knee, 5 - l ankle, 6 - pelvis,
# 7 - thorax, 8 - upper neck, 9 - head top, 10 - r wrist, 11 - r elbow, 12 - r shoulder, 13 - l shoulder, 14 - l elbow, 15 - l wrist)

class CSV:
	"""
	A class to incorporate common csv functionality used throughout the project

	...

	Attributes
	----------
	filename: str
		name of the CSV file
	columns: list
		columns in the CSV file
	df : pandas.DataFrame
		pandas dataframe to be written to csv

	Methods
	-------
	add_list(row: list):
		adds a list or list of lists to the dataframe

	save(mode:str = 'a', header: bool = False, index: bool = True):
		saves the dataframe to the csv file named ```filename```

	filter_columns(window_length: int = 13, polyorder: int = 2, columns: list = None):
		- filters the specified columns with a savitzy-golay filter
		- suffixes column names with '-Filtered'

	filter_columns_and_overwrite(window_length: int = 13, polyorder: int = 2, columns: list = None):
		- same as ```filter_columns``` except that suffixed columns are not added
		- columns are overwritten with the new values

	destructor:
		saves the dataframe to the csv file named ```filename``` in case user has not called the ```save``` function
	"""

	def __init__(self, filename: str, columns: list = None):
		assert columns is not None and type(columns) == list

		self.filename = filename
		self.columns = columns

		self.df = pd.DataFrame(columns=self.columns)
		self.df.to_csv(filename)

	def add_list(self, row: list):
		new_df = pd.DataFrame(row, columns=self.columns)

		self.df = self.df.append(new_df, ignore_index=True)

	def save(self, mode:str = 'a',
		header: bool = False, index: bool = True):

		self.df.to_csv(self.filename, mode=mode, header=header, index=index)

	def filter_columns(self, window_length: int = 13,
		polyorder: int = 2, columns: list = None):

		if columns is None:
			columns = self.columns

		for col in self.df.columns:
			if col in columns:
				vals = self.df[col]
				self.df[f'{col}-Filtered'] \
				= savgol_filter(vals, window_length,
							polyorder, mode='nearest')

		self.save('w', True, False)

	def filter_columns_and_overwrite(self, window_length: int = 13,
		polyorder: int = 2, columns: list = None):

		if columns is None:
			columns = self.columns

		for col in self.df.columns:
			if col in columns:
				vals = self.df[col]
				self.df[col] \
				= savgol_filter(vals, window_length,
							polyorder, mode='nearest')

		self.save('w', True, False)

	def __del__(self):
		print('--- Call the save function using the CSV object for a safer implementation ---')
		self.save()
