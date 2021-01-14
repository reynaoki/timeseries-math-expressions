from hec.heclib.dss import HecDss
from hec.heclib.util import HecTime
from hec.hecmath import TimeSeriesMath
from hec.io import TimeSeriesContainer

# Need to import the ParseMathExpr module. Update this depending on where you stored 
# the ParseMathExpr.py script, and make sure this path is on the sys.path
from NWDJyLib import ParseMathExpr

startTW = HecTime() # Starting time window
endTW = HecTime() # Ending time window
startTW.setYearMonthDay(1928, 7, 1, 1440) # July 1st, 1928 at midnight
endTW.setYearMonthDay(2008, 9, 30, 1440) # September 30th, 2008 at midnight

# Convert to readable string
startTW = startTW.dateAndTime(4).upper()
endTW = endTW.dateAndTime(4).upper()

# Set up DSS file name and open the file
dssInputFileName = "example_input.dss"
dssInputFile = HecDss.open(dssInputFileName)

variables = ["ARDB", "MCDB"]
dssPaths = ["//ARROW LAKES_IN/FLOW-UNREG//1DAY/COMPUTED/", "/COLUMBIA/MICA_IN/FLOW-IN//1DAY/NWP/"]

# Load DSS timeseries into TimeSeriesMath objects and place into a  dictionary
inputs = {}
for variable, dssPath in zip(variables, dssPaths):
  inputTSM = dssInputFile.read(dssPath, startTW, endTW)
  inputs.update({variable: inputTSM})

# Make sure to close files when we are done using them
dssInputFile.done()
dssInputFile.close()

# Set up an output DSS file
dssOutputFileName = "example_output.dss"
dssOutputFile = HecDss.open(dssOutputFileName)

# Evaluate the equation that will multiply the ARDB timeseries by 2, add the MCDB timeseries, and then subtract a constant of 200
# Make sure to pass the dictionary containing all of the variables as the second argument
outputTSM = ParseMathExpr.evaluate("2*ARDB + MCDB - 200", inputs)

# Prepare the TimeSeriesMath object for writing to a DSS file
outputTSC = outputTSM.getContainer() # convert from TimeSeriesMath to TimeSeriesContainer
outputTSC.storedAsdoubles = True # store in double precision
outputTSC.fileName = dssOutputFileName # file name that the timeseries is written to
outputTSC.fullName = "//EXAMPLE_OUTPUT/FLOW//1DAY/OUTPUT/" # whatever the desired output pathname is

# Write the DSS timeseries to the output DSS file
dssOutputFile.write(outputTSC)

# Make sure to close files when we are done using them
dssOutputFile.done()
dssOutputFile.close()
