#!/usr/bin/env python3
import csv
from matplotlib import pyplot as plt

g_database= {}

state_codes = {
    "AB" : "Alberta",
    "BC" : "British Columbia",
    "MB" : "Manitoba",
    "NB" : "New Brunswick",
    "NL" : "Newfoundland and Labrador",
    "NT" : "Northwest Territories",
    "NS" : "Nova Scotia",
    "NU" : "Nunavut",
    "ON" : "Ontario",
    "PE" : "Prince Edward Island",
    "QC" : "Quebec",
    "SK" : "Saskatchewan",
    "YT" : "Yukon",
}

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

def compute_tax(country: str, state: str, income : float, year : int = 2021) -> (float, float):
	db = load_database([country])
	country_data = db[country]
	if state.capitalize() in country_data[year]:
		state = state.capitalize()
	if state not in country_data[year]:
		state = state_codes[state]
	state_data = country_data[year][state]
	federal_data = country_data[year]['Federal']
	state_taxes = compute_tax_helper(income, state_data)
	federal_taxes = compute_tax_helper(income, federal_data)

	return (state_taxes, federal_taxes)

def formatNum(input : float) -> str:
	return "{:,.2f}".format(input)

def state_summary(country: str, state: str, income : float, year : int = 2021) -> float:
	(state_taxes, federal_taxes) = compute_tax(country, state, income, year)
	outString  = "Total Income: $" + formatNum(income)
	outString += "\nState Taxes: $" + formatNum(state_taxes)
	outString += "\nFederal Taxes: $" + formatNum(federal_taxes)
	outString += "\nTotal Taxes: $" + formatNum(state_taxes + federal_taxes)
	outString += "\nIncome After Taxes: $" + formatNum(income - (state_taxes + federal_taxes))
	return outString

def plotComparisons(input_list = None, plotIncome = True, plotRate = False):
	db = load_database()
	outputImage = 'graph.png'

	income_diff = 1000
	x_axis = list(range(0, 300000, income_diff))
	y_axis = {}
	year = 2021

	fig, ax = plt.subplots() 
	for state in input_list:
		if state == 'Federal':
			continue
		y_axis[state] = []
		for income in x_axis:
			(state_taxes, federal_taxes) = compute_tax('Canada', state, income)
			if plotIncome:
				y_axis[state].append(income - (state_taxes + federal_taxes))
			elif plotRate == True: # Plot tax rate
				if income == 0:
					y_axis[state].append(0)
				else:
					y_axis[state].append(100.0 * (state_taxes + federal_taxes) / income)
			else: # Plot taxes
				y_axis[state].append(state_taxes + federal_taxes)
		ax.plot(x_axis, y_axis[state], label=state)
	ax.legend()
	ax.set_xlabel('Taxable Income')
	ax.set_ylabel('Income After Taxes')

	fig.savefig(outputImage, format='png', dpi=300, bbox_inches='tight')
	plt.close()

def main():
	print(compute_tax('Canada', 'Ontario', 100000))
	plotComparisons(["British Columbia", "Ontario", "Quebec", "Manitoba", "Alberta"])

if __name__ == '__main__':
	main()
