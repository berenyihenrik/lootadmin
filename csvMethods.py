import csv

def readcsv(filename):
    with open(filename, 'r') as file:
        reader = csv.reader(file)
        rows = []
        for row in reader:
            rows.append(row)
        file.close()
        return rows