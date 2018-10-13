import requests
import json
import pandas as pd
import api_keys
import time

class BLSservice:
	headers = {'Content-type': 'application/json'}

	#For Current Year data
	def __init__(self, series_id):
		self.series_id = series_id
		curr_time = time.localtime()
		self.start_year = str(curr_time.tm_year)
		self.end_year = str(curr_time.tm_year)
		self.catalog = True
		self.calculations = True
		self.annualaverage = True

	#For Multiple Year data with options
	def __init__(self, series_id, start_year, end_year, catalog= True, calculations= True, annualaverage= True):
		self.series_id = series_id
		self.start_year = start_year
		self.end_year = end_year
		self.catalog = catalog
		self.calculations = calculations
		self.annualaverage = annualaverage
				
	def get_data(self):
		try:
			self.data = json.dumps({"seriesid": self.series_id,
					   "startyear":self.start_year, 
					   "endyear":self.end_year,
					   "catalog":self.catalog, 
					   "calculations":self.calculations, 
					   "annualaverage":self.annualaverage,
				"registrationkey": api_keys.api_key})

			
			self.p = requests.post('https://api.bls.gov/publicAPI/v2/timeseries/data/', 
						data=self.data, headers=self.headers)

			self.json_data = json.loads(self.p.text)
		except:
			print("ERROR when getting the data")
			
	def create_dataframe(self):
		self.item_list = []

		if self.json_data['status'] == "REQUEST_SUCCEEDED":
			for series in self.json_data['Results']['series']:
				seriesId = series['seriesID']
				series_title = series['catalog']['series_title']
				clean_title = series_title.replace('Entertainment: ', '')
				demographic, characteristic = clean_title.split(': ', 1)
						
				for item in series['data']:
					year = item['year']
					period = item['period']
					value = item['value']
					
					item_dict = {"SeriesTitle": characteristic,
								  "Year": year,
								  "Value": value
								}
					self.item_list.append(item_dict)

			self.item_df = pd.DataFrame(self.item_list)
		else:
			print(self.json_data['status'])

		self.transposed_item_df = self.item_df.T
		self.clean_df = self.transposed_item_df.loc[['SeriesTitle', 'Value']]

	def create_excel_file_from_df(self, excel_name):
		try:
			writer = pd.ExcelWriter(excel_name, engine='xlsxwriter', options={'strings_to_numbers': True})
			pd.DataFrame(self.item_df).to_excel(writer, sheet_name='Sheet1', index=False)
			writer.save()
		except:
			print("ERROR generating Excel")
		
	def create_excel_file_from_transposed_df(self, excel_name):
		try:
			writer = pd.ExcelWriter(excel_name, engine='xlsxwriter', options={'strings_to_numbers': True})
			pd.DataFrame(self.transposed_item_df).to_excel(writer, sheet_name='Sheet1', index=False)
			writer.save()
		except:
			print("ERROR generating Excel")
		
	def create_excel_file_from_clean_df(self, excel_name):
		try:
			writer = pd.ExcelWriter(excel_name, engine='xlsxwriter', options={'strings_to_numbers': True})
			pd.DataFrame(self.clean_df).to_excel(writer, sheet_name='Sheet1', index=False)
			writer.save()
		except:
			print("ERROR generating Excel")
		