import csv
import math

class Source:
    def __init__(self, file, cat="D"):
        self.cat = cat
        self.source = []
        with open(file) as source:
            data = csv.reader(source)
            for row in data:
                self.source.append(row)

    def filterCat(self):
        filtered = []
        for row in self.source:
            try:
                if row[0][-2] != "_":
                    # If label doesn't end with "_X" it isn't category specific
                    filtered.append(row)
                elif row[0][-1] == self.cat:
                    # Remove part of label identifying category for relevant entries
                    label_length = len(row[0]) - 2 
                    filtered.append([row[0][:label_length], row[1], row[2]])
                else:
                    # Discard values for irrelevant aircraft categories
                    pass
            except IndexError:
                # If label is less than 2 characters it cannot be category related
                filtered.append(row)
        return filtered

    def convert(self, constants):
        converted = []
        for row in self.source:
            if row[2] == 'ft':
                converted.append([row[0], float(row[1])*constants.value['ft2m'], "m"])
            elif row[2] == 'deg':
                converted.append([row[0], math.tan(math.radians(float(row[1]))), "grad"])
            elif row[2] == 'NM':
                converted.append([row[0], float(row[1])*constants.value['NM2m'], "m"])
            elif row[2] == 'kt':
                converted.append([row[0], float(row[1])*constants.value['kt2ms'], "m/s"])
            else:
                converted.append([row[0], float(row[1]), row[2]])
        return converted

class Constants(Source):
    def populate(self):
        self.value = {}
        for row in self.source:
            self.value[row[0]] = float(row[1])

class Variables(Source):
    def populate(self, constants):
        self.source = self.filterCat()
        self.source = self.convert(constants)
        self.value = {}
        for row in self.source:
            self.value[row[0]] = row[1]
