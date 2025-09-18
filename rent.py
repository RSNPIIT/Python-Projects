rent = abs(int(input("Enter the hostel/flat rent here : ")))
food = abs(int(input("Enter the fooding expenses here : ")))
electricity_spent = abs(int(input("Enter the electricity units spent by the hostel/flat room here : ")))
units = abs(int(input("Enter the cost per unit according to the Standand Indian Bill Rate : ")))
persons = abs(int(input("Enter the number of residents living in the hostel : ")))
bill = electricity_spent * units
output = (rent + food + bill) / persons
output_app = (rent + food + bill) // persons 
print(f"The per resident rent is : {output}")
print(f"But in order to resolve conflict the approximate rent is : {output_app}")
# This file is part of Python-Projects.
# Copyright (c) 2025 Ramrup Satpati
# Licensed under the GNU General Public License v3.0 (GPL-3.0).
