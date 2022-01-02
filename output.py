def writeCSV(values, name):
    with open(name, 'w') as file:
        for item,value in values.items():
            file.write(f"{item},{round(value,10)}\n")

def drawFAS(values):
    start = (values['xFAS'],0)
    end = (values['xFAF_start'],)
