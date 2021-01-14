# timeseries-math-expressions
A Jython module for using expressions to perform math operations on TimeSeriesMath objects (from Hydrologic Engineering Center).

Original source code from https://nerdparadise.com/programming/parsemathexpr, which was written by Blake O'Hare. This code has been modified to accept variables as TimeSeriesMath objects.

Currently supports order of operations for parenthesis, multiplication, division, addition, and subtraction. Also supports the default variables for the mathematical constants 'pi' and 'e'.

**Usage:**
The following function returns a number (int or float) or a TimeSeriesMath object:
ParseMathExpr.evaluate(equation, {vars})
  - equation: a string written out as a mathematical expression (ie. "5*A + B - C/2")
  - vars: a dictionary containing all of the variables (where the keys are the variable names, and the values are either numbers or TimeSeriesMath objects)

See example usage of this module in `example.py`
