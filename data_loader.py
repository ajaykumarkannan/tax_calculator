#!/usr/bin/env python3
import csv

g_database= {}

def load_database(data_list = ['Canada']) -> dict:
	database = g_database
	for country in data_list:
		if country not in database:
			print("Reloading the data for " + country)
		else:
			return database
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

def compute_tax_helper(income : float, data : list):
	taxes = 0
	remaining_income = income
	for (income_range, rate) in reversed(data):
		cur_taxable_income = max(0, remaining_income - income_range)
		remaining_income -= cur_taxable_income
		taxes += cur_taxable_income * rate / 100.0

	return taxes

def compute_tax(country: str, state: str, income : float, year : int = 2021) -> float:
	db = load_database([country])
	country_data = db[country]
	state_data = country_data[year][state]
	federal_data = country_data[year]['Federal']
	state_taxes = compute_tax_helper(income, state_data)
	federal_taxes = compute_tax_helper(income, federal_data)

	return (state_taxes, federal_taxes)

def main():
	print(compute_tax('Canada', 'Ontario', 100000))


if __name__ == '__main__':
	main()