#!/usr/bin/env python3
# vim: set noexpandtab shiftwidth=2 tabstop=2 :
import csv
from matplotlib import pyplot as plt
import matplotlib

g_database = {}
g_EI_database = {}
g_QB_EI_database = {}
g_CPP_database = {}
g_BPA_database = {}

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

def loadEI(fileName, database) -> None:
	with open(fileName) as csvfile:
		csvReader = csv.reader(csvfile, delimiter=',')
		print("Loading", fileName)
		for row in csvReader:
			try:
				if csvReader.line_num == 1:
					continue
				year = int(row[0])
				max_earnings = float(row[1])
				rate = float(row[2])
				max_EI = float(row[3])
				max_employer_premium = float(row[4])
				database[year] = (max_earnings, rate, max_EI, max_employer_premium)
			except ValueError:
				print("TODO: Issues")
	return

def compute_EI(country: str, state: str, income: float, year: int = 2021) -> float:
	EI_database = g_EI_database
	QB_EI_database = g_QB_EI_database
	if not EI_database or not QB_EI_database:
		print("Reloading EI data")
		loadEI('data/canadaEI.csv', EI_database)
		loadEI('data/canadaQuebecEI.csv', QB_EI_database)
	EI = 0.0
	if country == "Canada":
		if state == "Quebec" or state == "QB":
			database = g_QB_EI_database
		else:
			database = g_EI_database
		rate = database[year][1]
		max_val = database[year][2]
		EI = min(income * rate / 100.0, max_val)
	return EI

def loadCPP(fileName, database):
	with open(fileName) as csvfile:
		csvReader = csv.reader(csvfile, delimiter=',')
		print("Loading", fileName)
		for row in csvReader:
			try:
				if csvReader.line_num == 1:
					continue
				year = int(row[0])
				max_annual_earnings = float(row[1])
				exception_amount = float(row[2])
				max_cont_earnings = float(row[3])
				rate = float(row[4])
				max_contribution = float(row[5])
				max_self_contribution = float(row[6])
				database[year] = (max_annual_earnings, exception_amount, max_cont_earnings, rate, max_contribution, max_self_contribution)
			except ValueError:
				print("TODO: Issues")
	return

def compute_CPP(country: str, state: str, income: float, year: int = 2021) -> float:
	CPP_database = g_CPP_database
	if not CPP_database:
		print("Reloading CPP data")
		loadCPP('data/canadaCPP.csv', CPP_database)
	CPP = 0.0
	if country == "Canada":
		database = g_CPP_database
		max_annual_earnings = database[year][0]
		exception_amount = database[year][1]
		max_cont_earnings = database[year][2]
		rate = database[year][3]
		max_contribution = database[year][4]
		max_self_contribution = database[year][5]
		CPP_income = max(0, income - exception_amount)
		CPP = min(max_contribution, CPP_income * rate / 100.0)
	return CPP

def loadBPA(fileName, database):
	with open(fileName) as csvfile:
		csvReader = csv.reader(csvfile, delimiter=',')
		print("Loading", fileName)
		for row in csvReader:
			try:
				if csvReader.line_num == 1:
					continue
				year = int(row[0])
				state = row[1].strip()
				income = float(row[2])
				rate = float(row[3])
				if year not in database:
					database[year] = {}
				database[year][state] = (income, rate)

			except ValueError:
				print("TODO: Issues")
	return

def compute_BPA(country: str, state: str, income: float, year: int = 2021) -> float:
	BPA_database = g_BPA_database
	if not BPA_database:
		print("Reloading BPA data")
		loadBPA('data/canadaBPA.csv', BPA_database)
	BPA_deduction = 0.0
	if country == "Canada":
		database = g_BPA_database
		if year not in database: 
			print("Couldn't find the right yera")
			return 0
		if state in database[year]:
			state_income = database[year][state][0]
			state_rate = database[year][state][1]
			BPA_deduction += min(income, state_income) * state_rate / 100.0
		else:
			print("Found an issue.")
			return 0
		federal_income = database[year]["Federal"][0]
		federal_rate = database[year]["Federal"][1]
		BPA_deduction += min(income, federal_income) * federal_rate / 100.0
	return BPA_deduction

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
	if state.capitalize() in country_data[year]:
		state = state.capitalize()
	if state not in country_data[year]:
		state = state_codes[state]
	state_data = country_data[year][state]
	total_taxes = compute_tax_helper(income, state_data)
	total_taxes += compute_EI(country, state, income, year)
	total_taxes += compute_CPP(country, state, income, year)
	total_taxes -= compute_BPA(country, state, income, year)

	return total_taxes

def formatNum(input : float) -> str:
	return "{:,.2f}".format(input)

def state_summary(country: str, state: str, income : float, year : int = 2021) -> float:
	total_taxes = compute_tax(country, state, income, year)
	outString  = "Total Income: $" + formatNum(income)
	outString += "\nTotal Taxes: $" + formatNum(total_taxes)
	if country == "Canada":
		EI = compute_EI(country, state, income, year)
		CPP = compute_CPP(country, state, income, year)
		outString += "\n- Income Tax: $" + formatNum(total_taxes - (EI + CPP))
		outString += "\n- EI: $" + formatNum(EI)
		outString += "\n- CPP: $" + formatNum(CPP)
	outString += "\nIncome After Taxes: $" + formatNum(income - total_taxes)
	outString += "\n\n*Note that this is just an estimate, and doesn't include other things that are deducted from your income."
	return outString

def plotComparisons(input_list = None, plotIncome = True, plotRate = False):
	db = load_database()
	outputImage = 'graph.png'

	income_start = 0
	income_bound = 300000
	income_diff = int((income_bound - income_start) / 500)
	x_axis = list(range(income_start, income_bound, income_diff))
	y_axis = {}
	year = 2021

	fig, ax = plt.subplots()
	for state in input_list:
		y_axis[state] = []
		for income in x_axis:
			total_taxes = compute_tax('Canada', state, income)
			if plotIncome:
				y_axis[state].append(income - total_taxes)
				ax.set_ylabel('Income After Taxes')
			elif plotRate == True: # Plot tax rate
				if income == 0:
					y_axis[state].append(0)
					ax.set_ylabel('Total Taxes Paid')
				else:
					y_axis[state].append(100.0 * (total_taxes) / income)
					ax.set_ylabel('Average Tax Rate')
			else: # Plot taxes
				y_axis[state].append(total_taxes)
		ax.plot(x_axis, y_axis[state], label=state)
	ax.legend()
	ax.set_xlabel('Taxable Income')
	ax.get_xaxis().set_major_formatter(matplotlib.ticker.FuncFormatter(lambda x, p: format(int(x), ',')))
	ax.get_yaxis().set_major_formatter(matplotlib.ticker.FuncFormatter(lambda x, p: format(int(x), ',')))
	plt.xticks(rotation=45)

	fig.savefig(outputImage, format='png', dpi=300, bbox_inches='tight')
	plt.close()

def main():
	print(compute_tax('Canada', 'Ontario', 100000))
	plotComparisons(["British Columbia", "Ontario", "Quebec", "Manitoba", "Alberta"])

if __name__ == '__main__':
	main()
