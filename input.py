import csv

class Constants:
    def __init__(self, file):
        self.values = {}
        with open(file) as source:
            data = csv.reader(source)
            for row in data:
                self.values[row[0]] = float(row[1])

class Variables:
    def __init__(self,file):
        self.values = []
        with open(file) as source:
            data = csv.reader(source)
            for row in data:
                self.values.append(row)
