#!/usr/bin/env python3
import data_loader
from matplotlib import pyplot as plt

def plotComparisons(input_list = None):
	db = data_loader.load_database()
	outputImage = 'graph.png'

	income_diff = 1000
	x_axis = list(range(0, 150000, income_diff))
	y_axis = {}
	year = 2021

	fig, ax = plt.subplots() 
	for state in db['Canada'][year]:
		if state == 'Federal':
			continue
		if (input_list != None) and (state not in input_list):
			continue
		y_axis[state] = []
		for income in x_axis:
			(state_taxes, federal_taxes) = data_loader.compute_tax('Canada', state, income)
			y_axis[state].append(income - (state_taxes + federal_taxes))
		ax.plot(x_axis, y_axis[state], label=state)
	ax.legend()
	ax.set_xlabel('Taxable Income')
	ax.set_ylabel('Income After Taxes')

	fig.savefig(outputImage, format='png', dpi=300, bbox_inches='tight')

def main():
	plotComparisons(["British Columbia", "Ontario", "Quebec", "Manitoba", "Alberta"])

if __name__ == '__main__':
	main()