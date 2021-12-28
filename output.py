def writeCSV(values):
    with open("parameters.csv", 'w') as file:
        for item,value in values.items():
            file.write(f"{item},{value}\n")

def drawFAS(values):
    start = (values['xFAS'],0)
    end = (values['xFAF_start'],)
