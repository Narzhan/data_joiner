import uuid
import csv

ids = []

def generate_id():
    while True:
        id = str(uuid.uuid4())[:6]
        if id not in ids:
            ids.append(id)
            return id

with open("rytir.csv", "r") as input_file:
    reader = csv.reader(input_file, delimiter=";")
    print("File load done")
    print("Starting to generate ids")
    with open("rytir2.csv", "w") as output_file:
        for row in reader:
            output_file.write("{};{}\n".format(generate_id(), ";".join(row)))
    print("Done")

