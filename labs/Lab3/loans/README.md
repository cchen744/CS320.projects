# Loan Module

In these exercises, you'll start writing a `loans.py` module with two
Python classes you'll use for MP3.  It's OK if you don't finish these
classes during lab time (you can finish them with your group or alone
later when working on MP3).

## loans.py

In Jupyter, do the following:
1. Go to MP3
2. Right click in the file explore and create a "New File"
3. Name it loans.py
4. Open it

Using a .py module is easy -- just run `import some_mod` to run
`some_mod.py`, loading any functions or classes it has.

In your `loans.py`, add a print like this:

```python
print("Hello from loans.py!")

def hey():
    print("Hey!")
```

Now lets import it to your project notebook.  Create a `mp3.ipynb` in
the same directory as `loans.py`.

Run `import loans` in a cell.  You should see the first print!

You can also call the `hey` function now.  Try it:

```python
loans.hey()
```

If you change `hey` in `loans.py`, the new version won't automatically
reload into the notebook.  Add this so it will auto-reload:

```
%load_ext autoreload
%autoreload 2
```

Note this doesn't work all the time (if there's a bug in your
loans.py, you may need to do a Restart & Run All in the notebook after
fixing your module).

Feel free to delete the print statement and `hey` method from
`loans.py` (those were just for experimentation -- we'll be adding
other content to `loans.py`).

## 1. `Applicant` class

We'll want to create a class to represent people who apply for loans.  Start with this in `loans.py`:

```python
class Applicant:
    def __init__(self, age, race):
        self.age = age
        self.race = set()
        for r in race:
            ????
```

We'll be using HDMA loan data
(https://www.ffiec.gov/hmda/pdf/2023guide.pdf), which uses numeric
codes to represent race.  Here are the codes from the documentation,
recorded in a dictionary:

```python
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
```

Paste the race_lookup `dict` in your `loans.py` module, and use it to complete
your `__init__` constructor.  The loop should add entries in the
`race` parameter to the `self.race` attribute of the class,
converting from the numeric codes to text in the process.  The `race`
attribute is a set because applicants often identify with multiple
options.

**Note:**  Assume that the race parameter is either a string of digits or
a list of strings of digits.

Simply skip over any entries in the `race` parameter that don't appear
in the `race_lookup` dict (e.g., we'll see and skip "6" later because
that code indicates a missing value).

Test the code you wrote in `loans.py` from your `mp3.ipynb` notebook to
make sure the `Applicant.__init__` constructor properly fills the
`race` set.

```python
applicant = loans.Applicant("20-30", ["1", "2", "3"])
applicant.race
```

You should see this set:

```python
{'American Indian or Alaska Native', 'Asian', 'Black or African American'}
```

### `__repr__`

Add a `__repr__` method to your `Applicant` class:

```python
    def __repr__(self):
        return ????
```

Putting `applicant` at the end of a cell or printing `repr(applicant)` should show this:

```
Applicant('20-30', ['American Indian or Alaska Native', 'Asian', 'Black or African American'])
```

Note: The `race` attribute should be sorted lexicographically. It is also now a list, not a set, in this output.

### `lower_age`

You might notice that ages are given as strings rather than ints
because we need to support ranges (like "20-30").

Add a `lower_age` method that returns the lower int of an applicant's age range:

```python
    def lower_age(self):
        return ????
```

It should also support ages like "<75" (should just return the int
`75`) and ">25" (should just return the int `25`).

Try your method (you should get the int `20` since the age is "20-30"):

```python
applicant.lower_age()
```

Hints: you could use `.replace` get get rid of unhelpful characters
(like "<" and ">").  After that, splitting on "-" could help you find
the first number (it's OK to split on a character that doesn't appear
in a string -- you just get a list with one entry).

### `__lt__`

Recall that `__lt__` ("less than") lets you control what happens when
two objects get compared.

`obj1 < obj2` automatically becomes `obj1.__lt__(obj2)`, so you can
write `__lt__` to return a True/False, indicating whether `obj1` is
less than obj2.

Complete the following for your `Applicant` class:

```python
    def __lt__(self, other):
        return ????
```

Comparisons should be based on lower age.(Hint: use lower_age method)
Python sorting will also use your `__lt__` method.  Try it:

```python
sorted([
    loans.Applicant(">75", ["43", "44"]),
    loans.Applicant("20-30", ["1", "3"]),
    loans.Applicant("35-44", ["22"]),
    loans.Applicant("<25", ["5"]),
])
```

You should get this order:

```python
[Applicant('20-30', ['American Indian or Alaska Native', 'Black or African American']),
 Applicant('<25', ['White']),
 Applicant('35-44', ['Chinese']),
 Applicant('>75', ['Other Pacific Islander', 'Samoan'])]
```

## 2. `Loan` class

For the project, we'll use data loan data from this site:
https://cfpb.github.io/hmda-platform/#hmda-api-documentation.

Loan applications are described with dictionaries, all with the similar keys like this:

```python
values = {'activity_year': '2020', 'lei': '549300FX7K8PTEQUU487', 'derived_msa-md': '31540', 'state_code': 'WI',
         'county_code': '55025', 'census_tract': '55025002402', 'conforming_loan_limit': 'C',
         'derived_loan_product_type': 'Conventional:First Lien',
         'derived_dwelling_category': 'Single Family (1-4 Units):Site-Built',
         'derived_ethnicity': 'Not Hispanic or Latino', 'derived_race': 'White', 'derived_sex': 'Male',
         'action_taken': '3', 'purchaser_type': '0', 'preapproval': '2', 'loan_type': '1', 'loan_purpose': '4',
         'lien_status': '1', 'reverse_mortgage': '2', 'open-end_line_of_credit': '1',
         'business_or_commercial_purpose': '2', 'loan_amount': '225000.0', 'loan_to_value_ratio': '78.671',
         'interest_rate': '3.000', 'rate_spread': 'NA', 'hoepa_status': '3', 'total_loan_costs': 'NA',
         'total_points_and_fees': 'NA', 'origination_charges': 'NA', 'discount_points': 'NA',
         'lender_credits': 'NA', 'loan_term': '360', 'prepayment_penalty_term': 'NA', 'intro_rate_period': '1',
         'negative_amortization': '2', 'interest_only_payment': '2', 'balloon_payment': '2',
         'other_nonamortizing_features': '2', 'property_value': '285000', 'construction_method': '1',
         'occupancy_type': '1', 'manufactured_home_secured_property_type': '3',
         'manufactured_home_land_property_interest': '5', 'total_units': '1', 'multifamily_affordable_units': 'NA',
         'income': '0', 'debt_to_income_ratio': '>60%', 'applicant_credit_score_type': '1',
         'co-applicant_credit_score_type': '10', 'applicant_ethnicity-1': '2', 'applicant_ethnicity-2': '',
         'applicant_ethnicity-3': '', 'applicant_ethnicity-4': '', 'applicant_ethnicity-5': '',
         'co-applicant_ethnicity-1': '5', 'co-applicant_ethnicity-2': '', 'co-applicant_ethnicity-3': '',
         'co-applicant_ethnicity-4': '', 'co-applicant_ethnicity-5': '', 'applicant_ethnicity_observed': '2',
         'co-applicant_ethnicity_observed': '4', 'applicant_race-1': '5', 'applicant_race-2': '',
         'applicant_race-3': '', 'applicant_race-4': '', 'applicant_race-5': '', 'co-applicant_race-1': '8',
         'co-applicant_race-2': '', 'co-applicant_race-3': '', 'co-applicant_race-4': '', 'co-applicant_race-5': '',
         'applicant_race_observed': '2', 'co-applicant_race_observed': '4', 'applicant_sex': '1',
         'co-applicant_sex': '5', 'applicant_sex_observed': '2', 'co-applicant_sex_observed': '4',
         'applicant_age': '55-64', 'co-applicant_age': '9999', 'applicant_age_above_62': 'Yes',
         'co-applicant_age_above_62': 'NA', 'submission_of_application': '1', 'initially_payable_to_institution': '1',
         'aus-1': '6', 'aus-2': '', 'aus-3': '', 'aus-4': '', 'aus-5': '', 'denial_reason-1': '1',
         'denial_reason-2': '', 'denial_reason-3': '', 'denial_reason-4': '', 'tract_population': '3572',
         'tract_minority_population_percent': '41.1499999999999986', 'ffiec_msa_md_median_family_income': '96600',
         'tract_to_msa_income_percentage': '64', 'tract_owner_occupied_units': '812',
         'tract_one_to_four_family_homes': '910', 'tract_median_age_of_housing_units': '45'}
```

Paste the above to your notebook.  We want to use a dict like the above to create a `Loan` object as follows:

```python
loan = loans.Loan(values)
```

Whereas the `__init__` for `Applicant` took a few parameters, the
`__init__` for the `Loan` class will take a single parameter,
`values`, which will contain all the data necessary to set the `Loan`
attributes.

Start with the following, then modify and add code:

```python
class Loan:
    def __init__(????, values):
        self.loan_amount = self.float_extract(values["loan_amount"]) # write the float_extract method as specified below
        # add lines here

    def float_extract(self, string):
	if string == "NA" or string == "Exempt":
            return  ????
        else:
            return ????
```

Requirements:
* A `Loan` object should have four attributes: `loan_amount`, `property_value`, `interest_rate`, `applicants`
* The first three attributes are floats, using the float_extract method convert a string into a float. If the string is either "NA" or "Exempt"(that represent missing values), float_extract() should return -1, otherwise it should extract the float value from the string.
* The `applicants` attribute should be a list of `Applicant` objects, where the minimum number of elements of the list is 1 (applicant) and the maximum number of elements of the list is 2 (applicant and co-applicant).  
* Every loan object has at least one applicant, with age values["applicant_age"] and race(s) in the multiple values["applicant_race-????"] entries.
* Some loans have a second applicant (but no more) -- you'll know there is a second applicant when values["co-applicant_age"] != "9999". In that case, self.applicants should contain two Applicant objects, with the info from the second coming from the values["co-applicant_age"] and values["co-applicant_race-????"] entries.


Manually test your `Loan` class from your notebook with a few snippets:
* `loan.interest_rate` should be `3.0`
* `loan.applicants` should be `[Applicant('55-64', ['White'])]`
* choose a couple more...

### `__str__` and `__repr__`

Add a `__str__` method to your `Loan` class so that `print(loan)` gives the following:

```
<Loan: 3.0% on $225000.0 with 1 applicant(s)>
```

Add a `__repr__` that returns the same string as `__str__`.

Note: your print output should include **all** of the same characters, including the < and > and everything between.

### `yearly_amounts`

The loans have details regarding payment amount and frequency in the
terms, but for simplicity, we'll ignore that here.

The `yearly_amounts` method in the `Loan` class should be a generator
that yields loan amounts, as the loan is payed off over time.  Assume
that each year, a single payment is made, after interest is
calculated. 

**Note:** `loan.interest_rate` is in percentage. Convert it
to decimal before using it. Failure to do so may result in interest 
that will never be paid off, creating an infinite loop!

```python
def yearly_amounts(self, yearly_payment):
    # TODO: assert interest and amount are positive
    amt = self.loan_amount

    while amt > 0: 
        # TODO: yield amt
        # TODO: add interest rate multiplied by amt to amt
        # TODO: subtract yearly payment from amt
```

Your job:
1. Finish the TODOs in the above snippet.
2. Test your code from the notebook.  For example, you could run this from the notebook:

```python
for amt in loan.yearly_amounts(80000):
    print(amt)
```

And get this:

```
225000.0
151750.0
76302.5
```

3. Make the method a generator.  Get rid of the `result` list, and instead of appending to it, yield `amt`.  Make sure the loop works the same way as before in your notebook.  One advantage of the generator is that the method will work even if the payment is too small (the generator will keep yielding larger amounts as the debt keeps growing). 
**This last step is very important to passing the MPY tests!**
