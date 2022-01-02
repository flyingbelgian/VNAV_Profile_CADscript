import input, calculator, output

cat = "B"

# constants are assumed to be in SI values (m, grad, m/s) and category independent
# list of constants includes values to be used for conversion from non-SI values
constant = input.Constants("constants.csv")
constant.populate()

# rulebase values are set by the relevant regulators
# ICAO standard values to be used of there are no region/country specific standards
rule = input.Variables("rulebase.csv", cat)
rule.populate(constant)

# variables are related to a specific procedure and aerodrome
# due to possible different update cycles between procedures for a specific aerodrome
# it is possible that aerodrome data differs between procedures at the same aerodrome
# future update to link file name to procedure name to allow tracing of applicability
var = input.Variables("variables.csv", cat)
var.populate(constant)

# surface parameters are calculated based on provided constants, rulebase and
# procedure variables
param = calculator.Parameters(constant, rule, var)

# print(values)
output.writeCSV(constant.value,"outputconstant.csv")
output.writeCSV(rule.value,"outputrule.csv")
output.writeCSV(var.value,"outputvar.csv")
output.writeCSV(param.value,"outputparam.csv")