import calculator

values = calculator.getSource()

values = values | calculator.addCalcVariables(values)

values = values | calculator.addHL(values)

values = values | calculator.addTempCorr(values)

values = values | calculator.addOAS(values)

values = values | calculator.addLateralLimits(values)

print(values)

output = [f'{item}: {values[item]}' for item in values]
# print(output)
text = ""
with open("command_script.txt", 'w') as file:
    for line in output:
        file.write(line + "\n")