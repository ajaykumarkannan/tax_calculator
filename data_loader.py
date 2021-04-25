#!/usr/bin/env python3
import csv

def load_database() -> dict:
	data_list = ['Canada']
	database = {}
	for country in data_list:
		country_entry = {}
		with open('data/' + country.lower() + '.csv') as csvfile:
			csvReader = csv.reader(csvfile, delimiter=',')
			for row in csvReader:
				try:
					if csvReader.line_num == 1:
						continue
					year = int(row[0])
					state = row[1].strip()
					min_income = int(row[2])
					rate = float(row[3])
					if year not in country_entry:
						country_entry[year] = {}
					if state not in country_entry[year]:
						country_entry[year][state] = []
					country_entry[year][state].append((min_income, rate))
				except ValueError:
					print("TODO: Issues")
		database[country] = country_entry
	
	return database

def main():
	print(load_database())


if __name__ == '__main__':
	main()