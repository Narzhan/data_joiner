import csv

correct_records = []
incorrect_records = []

# , errors="ignore"
with open("rytir.csv", "r") as file:
    reader = csv.reader(file, delimiter=";")
    for row in reader:
        if " - " in row[0]:
            incorrect_records.append(";".join(row))
        else:
            correct_records.append(";".join(row))
with open("rytir-filtered.csv", "w") as file:
    for row in correct_records:
        file.write(row + "\n")
    for row in incorrect_records:
        file.write(row + "\n")
