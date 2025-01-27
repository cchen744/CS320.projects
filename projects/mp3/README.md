# Machine Project 3: Loan Analysis

## Overview

Sadly, there is a long history of lending discrimination based on race
in the United States.  Lenders have literally drawn red
lines on a map around certain neighborhoods where they would not
offer loans, based on the racial demographics of those neighborhoods
(read more about redlining here: https://en.wikipedia.org/wiki/Redlining).
In 1975, congress passed the Home Mortgage Disclosure Act (HDMA) to
bring more transparency to this injustice
(https://en.wikipedia.org/wiki/Home_Mortgage_Disclosure_Act).  The
idea is that banks must report details about loan applications and
which loans they decided to approve.

The public HDMA dataset spans all the states and many years, and is documented here:
* https://www.ffiec.gov/hmda/pdf/2020guide.pdf
* https://cfpb.github.io/hmda-platform/#hmda-api-documentation

In this machine project, we'll analyze every loan application made in Wisconsin in
2020.

<hr/>

## Learning Objectives

There's a lot of new stuff here, and students have often reported back
that P3 is the hardest of the semester, so we encourage you to start
early.

During this machine project, students will:
- Practice with the Object-Oriented Programming (OOP) paradigm by creating custom classes for analyzing loan data.
- Work with analyzing large datasets.
- Create efficient data structures for data storage and lookup.
- Develop custom tests to ensure code quality.
- Write their own Python modules that can be used in other notebooks or scripts.

<hr/>

## Setup

Before you begin working on the project make sure you run the following commands from the `projects` directory:

```bash
cd mp3 # navigate to the project directory
git checkout main # switch to the main branch
git pull # pull remote changes to your local branch
git checkout MP3 # switch to MP3 branch
git merge main # merge changes from main to MP3
```

Once you run these commands, you should verify that you are on the `MP3` branch by running `git branch`, you should also be able to run `ls` to see that this machine project and all of its files are present. Additional instructions can be found in the [git-workflows](../../git-workflows/README.md/#starting-a-machine-project) document.

You are now ready to begin the machine project. Make sure that you add-commit-push your code as you go.

<hr/>

## Project Structure
This project consists of a **Group Part** worth 75% and an **Individual Part** worth 25%.
* **Group Part:**
    * Part 1: Loan Classes _(`loans.py`)_
    * Part 2: Binary Search Tree _(`search.py`)_
    * Part 3: 'Merchants Bank of Indiana' Analysis _(`mp3.ipynb`)_
* **Individual Part:**
    * Part 4: 'Landmark Credit Union' Analysis _(`mp3.ipynb`)_

<hr/>

## Testing

To test your answers, do the following:
1. **Restart Kernel:** Do a "Kernel" > "Restart Kernel & Run All Cells" in your notebook
2. **Save Notebook:** Once the notebook finished running, do "File" > "Save Notebook"
3. **Navigate to Project:** In terminal, navigate to your `mp3` directory
4. **Run Tester:** Run `python3 tester.py` and work on fixing any issues

**Notes**: 
* ***Do not*** include the question, or anything else after "#Q__" or else we may be unable to
parse your notebook.
* **It is okay to add additional cells outside of these, but only questions that have "#Q__" as
the first line will be graded.**
* You need to do a "Restart Kernel & Run All Cells" each time you make modifications to your
notebook. Wait for all cells to run before saving. If you get an error that says "Expected
execution count XX but found YY", you need to do this again.

<hr/>

## Submission

**Required Files**
* `mp3.ipynb`
* `loans.py`: A Python module (.py file) containing classes for creating `Applicant`, `Loan`, and `Bank` objects. (Will start in lab)
* `search.py`: A Python module (.py file) containing classes for creating `Node`, and `BST` objects. (Will start in lab)
* `module_tester.py`: A Python script (.py file) for testing the two modules we wrote above.

To submit the machine project, make sure that you have followed the instructions for "submitting a machine project"
in the [git-workflows](../../git-workflows/README.md/#submitting-a-machine-project) document for the required file(s) above.

When following the submission instructions from above, the final output should look similar to this in GitLab:

<img src="img/successful-submission.PNG">

**Note**: When we ran the autograder on this demonstration, we **did not** add in the additional tests. Make sure
that you add in the additional tests in `module_tester.py` to achieve full marks.

If you do not know how to get to this screen, review the link above. If you are having issues, please come to office hours.

<hr/>

## Important Notes
1. Hardcoding of any kind or trying to "cheat" the autograder **will be penalized heavily and can also result in 0 marks for all the projects**. If you are confused about your code, please reach out to the teaching staff before submission.

<hr/>

# Group Part (75%)

For this portion of the machine project, you may collaborate with your group members in any way (including looking at group members' code). You may also seek help from CS 320 course staff (peer mentors, TAs, and the instructor). You **may not** seek or receive help from other CS 320 students (outside of your group) or anybody else outside of the course.

## Part 1: Loan Classes

For part 1 of this machine project, you will be working to create custom classes for handling data related to loans. These classes will allow us to easily take in large amounts of data and format it in a way that is easy for us to work with and analyze. 

To begin, finish the `Applicant` and `Loan` classes from [Lab 3](../../labs/Lab3/README.md) (if you haven't already done so). These classes hold data about people who apply to loans and other data related to loans respectively.

We'll now add a `Bank` class to `loans.py` file that can keep track of some bank information as well as a list of `Loan` objects that are tied to this bank.  A `Bank` object can be created like this (create a class with the necessary constructor for this to work):

```python
lcu = loans.Bank("Landmark Credit Union")
```

### banks.json

The `__init__` of your `Bank` class should check that the given name appears in the `banks.json` file.  If it does, the `__init__` should also lookup the `lei` ("Legal Entity Identifier") corresponding to the name and store that in an `lei` attribute.  In other words, `lcu.lei` should give the LEI for LCU, in this case "549300KY533JFETOYG46".

**Note**: Try to avoid reading in the `banks.json` file each time you create a new `Bank` object. Instead, try defining it outside of the `Bank` class to optimize the creation of new `Bank` objects.

### wi.zip

The `__init__` should also iterate over the loan data from the CSV inside of `wi.zip` and either skip the loan data if the `lei` doesn't match that of the `Bank` object, or create a `Loan` object from the loan data if the `lei` does match and append it to a list that is stored as an attribute in the `Bank` object called `loan_list`. For example, someone should be able to call `lcu.loan_list` to get a list of all of the `Loan` objects that have the same `lei` as the `Bank` object we created above.

You already learned how to read text from a zip file in lab using `TextIOWrapper` and the `zipfile` module. Read the documentation and example for how to read CSV files with `DictReader` here: https://docs.python.org/3/library/csv.html#csv.DictReader.  You can combine this with what you learned about zipfiles.  When you create a `DictReader`, just pass in a `TextIOWrapper` object instead of a regular file object.

### Special Methods

Using this new `loan_list` attribute, you are able to print the last loan for this `Bank` object using:

```python
print(lcu.loan_list[-1])
```

And we can check how many loans there are associated with this `Bank` object using:

```python
print(len(lcu.loan_list))
```

For convenience, we want to be able to directly use brackets and `len` directly on `Bank` objects, like this:
* `lcu[-1]`
* `len(lcu)`

Add the special methods to `Bank` necessary to make the above two lines of code work.

## Testing

Running `python3 tester.py` does two things:

1. Compute a score based on whether answers in your `mp3.ipynb` are correct.
2. Get a second score by running `module_tester.py`, which exercises various classes/methods in `loan.py` (already done) and `search.py` (the next part)

Your total score is an average of these two components.

Try running `python3 module_tester.py` now.  You should see the following (assuming you haven't worked ahead on `search.py`):

```
{'score': 40.0, 'errors': ['could not find search module']}
```

It should actually be possible to get 50.0 from `module_tester.py`
after just completing `loans.py`, but we left some tests undone so you
can get practice writing tests for yourself.

Open `module_tester.py` and take a look at the `loans_test`.  The
function tries different things (e.g., creating different `Loan` and
`Applicant` objects and calling various methods).

Whenever something works, a global variable `loans_points` is
increased.  There are also asserts, and if any fail, the test stops
giving points.  For example, here's a bit that tests the `lower_age`
method:

```python
    # lower_age
    assert loans.Applicant("<25", []).lower_age() == 25
    assert loans.Applicant("20-30", []).lower_age() == 20
    assert loans.Applicant(">75", []).lower_age() == 75
    loans_points += 1
```

### Requirement: Additional tests in `module_tester.py`
You should add some additional test code of your choosing 
(based on where you think bugs are most likely to occur).  When the 
additional code shows that `loans.py` works correctly, it should add 4 
points to `loan_points`.  You could do this is one step (`loans_points += 4`),
or better, divide the points over the testing of a few different
aspects.

There are not any specific requirements for additional testing -- just make sure 
that you do add a new test (or more) and then give yourself more points.

### Debugging the Module Tester

If you are not currently passing the module tester, it is likely that you are failing one of the test cases which are created using `assert`. One common way of debugging these errors is by using print debugging. Here is an example of how print debugging might work for this machine project:

Let's say the following `assert` statement is failing:

```python
...
assert loans.Applicant("<25", []).lower_age() == 25
...
```

Adding a print statement above this line with `loans.Applicant("<25", []).lower_age()` will let us know the output of this code. So our code would now look something like this:

```python
...
print(loans.Applicant("<25", []).lower_age())
assert loans.Applicant("<25", []).lower_age() == 25
...
```

From here, we will be able to see what our code is outputting and can modify our code accordingly. For example, if we see that our code is printing `'25'`, we now know that our code is outputting a string instead of an int, and we can make the appropriate change in `loans.py` before rerunning the module tester.

## Part 2: Binary Search Tree

For part 2 of this machine project, you will be creating custom classes for a `Node` and `BST` data structures. These classes will allow us to lookup specific `Loan` objects efficiently as we will see in the questions below.

To begin, finish the `Node` and `BST` classes from [Lab 4](../../labs/Lab4/README.md) (if you haven't already done so). 

**Note:** if we haven't gotten to BSTs in lecture and lab yet, you can still work on some of the questions in parts 3 and 4, but you should wait to work on the ones related to trees.

### Special Method

Add a special method to `BST` so that if `t` is a `BST` object so that it is possible to lookup items with `t["some key"]` instead of `t.root.lookup("some key")`.

<hr/>

## **Follow the instructions in `mp3.ipynb` to complete the rest of the project (Part 3 and Part 4)**