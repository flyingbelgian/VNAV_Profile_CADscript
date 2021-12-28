import calculator
import output

values = calculator.getSource()

values = values | calculator.addCalcVariables(values)

values = values | calculator.addHL(values)

values = values | calculator.addTempCorr(values)

values = values | calculator.addOAS(values)

values = values | calculator.addLateralLimits(values)

#Round all parameters to maximum 10 digits after the decimal
for item,value in values.items():
    values[item] = round(value,10)

# print(values)
output.writeCSV(values)