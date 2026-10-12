import pandas as pd


# Clean Student Data
def clean_students():

    students = pd.read_csv("data/students.csv")

    students = students.drop_duplicates()

    students = students.fillna("Not Available")

    students["skills"] = students["skills"].str.lower()

    students["interests"] = students["interests"].str.lower()

    students.to_csv("data/students.csv", index=False)

    return students


# Clean Internship Data
def clean_internships():

    internships = pd.read_csv("data/internships.csv")

    internships = internships.drop_duplicates()

    internships = internships.fillna("Not Available")

    internships["required_skills"] = internships["required_skills"].str.lower()

    internships["domain"] = internships["domain"].str.lower()

    internships.to_csv("data/internships.csv", index=False)

    return internships