import json
from zipfile import ZipFile
import csv
import io
import time
#import graphviz

class Applicant:
    def __init__(self, age, race):
        self.age = age
        self.race = set()
        for r in race:
            if r not in race_lookup:
                pass
            else:
                self.race.add(race_lookup[r])
    
    def __repr__(self):
        return f"Applicant({repr(self.age)}, {sorted(self.race)})"
    
    def lower_age(self):
        '''Get the lower bound of age range''' 
        if self.age.startswith('>') or self.age.startswith('<'):
            return int(self.age[1:])
        elif '-' in self.age:
            return int(self.age.split('-')[0])
        else:
            return int(self.age)
    
    def __lt__(self, other):
        '''Compare applicants based on their lower age bound'''
        return self.lower_age() < other.lower_age()
    

race_lookup = {
    "1": "American Indian or Alaska Native",
    "2": "Asian",
    "3": "Black or African American",
    "4": "Native Hawaiian or Other Pacific Islander",
    "5": "White",
    "21": "Asian Indian",
    "22": "Chinese",
    "23": "Filipino",
    "24": "Japanese",
    "25": "Korean",
    "26": "Vietnamese",
    "27": "Other Asian",
    "41": "Native Hawaiian",
    "42": "Guamanian or Chamorro",
    "43": "Samoan",
    "44": "Other Pacific Islander"
}


class Loan:
    def __init__(self, values):
        self.loan_amount = self.float_extract(values["loan_amount"]) 
        # write the float_extract method as specified below
        # add lines here
        self.interest_rate = self.float_extract(values["interest_rate"])
        #self.tract_minority_population_percent = float_extract(values["tract_minority_population_percent"])
        self.property_value = self.float_extract(values["property_value"])
        if values["co-applicant_age"] != "9999":
            self.applicants = [Applicant(values['applicant_age'], [values['applicant_race-1'],values['applicant_race-2'],values['applicant_race-3'],values['applicant_race-4'],values['applicant_race-5']]),
                               Applicant(values['co-applicant_age'], [values['co-applicant_race-1'],values['co-applicant_race-2'],values['co-applicant_race-3'],values['co-applicant_race-4'],values['co-applicant_race-5']])]
        else:
            self.applicants = [Applicant(values['applicant_age'], [values['applicant_race-1'],values['applicant_race-2'],values['applicant_race-3'],values['applicant_race-4'],values['applicant_race-5']])]
        
    def float_extract(self, string):
        if string == "NA" or string == "Exempt":
            return  -1
        else:
            return float(string)
        
    
    def __str__(self):
        return f"<Loan: {self.interest_rate}% on ${self.loan_amount} with {len(self.applicants)} applicant(s)>"
    
    def __repr__(self):
        return f"<Loan: {self.interest_rate}% on ${self.loan_amount} with {len(self.applicants)} applicant(s)>"
    
    def yearly_amounts(self, yearly_payment):
    # TODO: assert interest and amount are positive
        amt = self.loan_amount
        interest_rate = self.interest_rate/100
        yearly_amounts = []
        
        while amt > 0 and interest_rate>0: 
        # TODO: yield amt
            yearly_amounts.append(amt)
        # TODO: add interest rate multiplied by amt to amt
        # TODO: subtract yearly payment from amt
            amt = amt*(1+interest_rate)- yearly_payment
            
        return yearly_amounts
    
with open('banks.json') as b:
            banks = json.load(b) #banks.json is converted to a list of dictionaries.
    
class Bank:
    def __init__(self,name):
        
        self.name = name
        
        for bank in banks:
            if bank['name'] == name:
                self.lei = bank['lei']
                self.count = bank['count']
                self.period = bank['period']
                break # stop iteration when bank is found
                
        self.loan_list = []

        
        with ZipFile('wi.zip') as zf:
            with zf.open('wi.csv') as csvfile:
                text_file = io.TextIOWrapper(csvfile,encoding = 'utf-8')
                loans_reader = csv.DictReader(text_file)
                for loan in loans_reader:
                    if loan['lei'] == self.lei:
                        self.loan_list.append(Loan(loan))
                        