##Source from https://nerdparadise.com/programming/parsemathexpr, by Blake O'Hare

# A really simple expression evaluator supporting the
# six basic math functions (PEMDAS) and variables.

#Edited to be able to handle TimeSeriesMath objects
#By: Reyn Aoki
#Email contact: reyn.a.aoki@usace.army.mil
#Last updated: February 4, 2021

from hec.hecmath import TimeSeriesMath

class ParseMathExpr:
    def __init__(self, string, vars={}):
        self.string = string
        self.index = 0
        self.vars = {
            'pi' : 3.141592653589793,
            'e' : 2.718281828459045
            }
        for var in vars.keys():
            if self.vars.get(var) != None:
                raise Exception("Cannot redefine the value of " + var)
            self.vars[var] = vars[var]
    
    def getValue(self):
        value = self.parseExpression()
        self.skipWhitespace()
        if self.hasNext():
            raise Exception(
                "Unexpected character found: '" +
                self.peek() +
                "' at index " +
                str(self.index))
        return value
    
    def peek(self):
        return self.string[self.index:self.index + 1]
    
    def hasNext(self):
        return self.index < len(self.string)
    
    def skipWhitespace(self):
        while self.hasNext():
            if self.peek() in ' \t\n\r':
                self.index += 1
            else:
                return
    
    def parseExpression(self):
        return self.parseAddition()
    
    def parseAddition(self):
        values = [self.parseMultiplication()]
        while True:
            self.skipWhitespace()
            char = self.peek()
            if char == '+':
                self.index += 1
                result = self.parseMultiplication()
                values.append(result)
            elif char == '-':
                self.index += 1
                result = self.parseMultiplication()
                if isinstance(result, TimeSeriesMath):
                    values.append(result.negative())
                else:
                    values.append(-1 * result)
            else:
                break
        tempNum = 0
        for value in values:
            if isinstance(value, TimeSeriesMath):
                tempNum = value.add(tempNum)
            elif isinstance(tempNum, TimeSeriesMath):
                tempNum = tempNum.add(value)
            else:
                tempNum += value
        return tempNum
    
    def parseMultiplication(self):
        values = [self.parseParenthesis()]
        while True:
            self.skipWhitespace()
            char = self.peek()
            if char == '*':
                self.index += 1
                char2 = self.peek()
                if char2 == '*':
                    self.index += 1
                    result = self.parseParenthesis()
                    values.append(['**', result])
                else:
                    result = self.parseParenthesis()
                    values.append(result)
            elif char == '/':
                div_index = self.index
                self.index += 1
                result = self.parseParenthesis()
                if result == 0:
                    raise Exception(
                        "Division by 0 kills baby whales (occured at index " +
                        str(div_index) +
                        ")")
                if isinstance(result, TimeSeriesMath):
                    values.append(result.inverse())
                else:
                    values.append(1.0 / result)
            else:
                break
        values = self.parseExponent(values)
        value = 1.0
        for factor in values:
            if isinstance(factor, TimeSeriesMath):
                value = factor.multiply(value)
            elif isinstance(value, TimeSeriesMath):
                value = value.multiply(factor)
            else:
                value *= factor
        return value

    def parseExponent(self, values):
        tempValues = values
        safeGuard = 0
        i = 0
        while i < len(tempValues):
            if i+1 < len(tempValues):
                if isinstance(tempValues[i+1], list) and tempValues[i+1][0] == '**':
                    if isinstance(tempValues[i], TimeSeriesMath):
                        factor = tempValues[i].exponentiation(tempValues[i+1][1])
                    else:
                        factor = tempValues[i] ** tempValues[i+1][1]
                    tempValues[i] = factor
                    del tempValues[i+1]
                else:
                    i += 1
            else:
                i += 1
            safeGuard += 1
            if safeGuard > 1000:
                break
        return tempValues

    def parseParenthesis(self):
        self.skipWhitespace()
        char = self.peek()
        if char == '(':
            self.index += 1
            value = self.parseExpression()
            self.skipWhitespace()
            if self.peek() != ')':
                raise Exception(
                    "No closing parenthesis found at character "
                    + str(self.index))
            self.index += 1
            return value
        else:
            return self.parseNegative()
    
    def parseNegative(self):
        self.skipWhitespace()
        char = self.peek()
        if char == '-':
            self.index += 1
            result = self.parseParenthesis()
            if isinstance(result, TimeSeriesMath):
                return result.negative()
            else:
                return -1 * result
        else:
            return self.parseValue()
    
    def parseValue(self):
        self.skipWhitespace()
        char = self.peek()
        if char in '0123456789.':
            return self.parseNumber()
        else:
            return self.parseVariable()
    
    def parseVariable(self):
        self.skipWhitespace()
        var = ''
        while self.hasNext():
            char = self.peek()
            if char.lower() in '_abcdefghijklmnopqrstuvwxyz0123456789':
                var += char
                self.index += 1
            else:
                break
        
        value = self.vars.get(var, None)
        if value == None:
            raise Exception(
                "Unrecognized variable: '" +
                var +
                "'")
        if isinstance(value, TimeSeriesMath):
            return value
        else:
            return float(value)
    
    def parseNumber(self):
        self.skipWhitespace()
        strValue = ''
        decimal_found = False
        char = ''
        while self.hasNext():
            char = self.peek()
            if char == '.':
                if decimal_found:
                    raise Exception(
                        "Found an extra period in a number at character " +
                        str(self.index) +
                        ". Are you European?")
                decimal_found = True
                strValue += '.'
            elif char in '0123456789':
                strValue += char
            else:
                break
            self.index += 1
        if len(strValue) == 0:
            if char == '':
                raise Exception("Unexpected end found")
            else:
                raise Exception(
                    "I was expecting to find a number at character " +
                    str(self.index) +
                    " but instead I found a '" +
                    char +
                    "'. What's up with that?")
        return float(strValue)
        
def evaluate(expression, vars={}):
    try:
        p = ParseMathExpr(expression, vars)
        #This value should be a TimeSeriesMath object
        value = p.getValue()
    except Exception, ex:
        msg = ex.message
        raise Exception(msg)
    if isinstance(value, TimeSeriesMath):
        newTSC = value.getContainer()
        epsilon = 0.0000000001
        newTimes = []
        newValues = []
        for t,v in zip(newTSC.times, newTSC.values):
            if v > 0:
                if int(v + epsilon) != int(v):
                    v = int(v + epsilon)
                elif int(v - epsilon) != int(v):
                    v = int(v)
            else:
                if int(v + epsilon) != int(v):
                    v = int(v)
                elif int(v - epsilon) != int(v):
                    v = int(v - epsilon)
            newTimes.append(t)
            newValues.append(float(v))
        newTSC.times = newTimes
        newTSC.values = newValues
        newTSM = TimeSeriesMath(newTSC)
        return newTSM
        
    else:
        # Return an integer type if the answer is an integer
        if int(value) == value:
            return int(value)
        
        # If Python made some silly precision error
        # like x.99999999999996, just return x + 1 as an integer
        epsilon = 0.0000000001
        if value > 0:
            if int(value + epsilon) != int(value):
                return int(value + epsilon)
            elif int(value - epsilon) != int(value):
                return int(value)
        else:
            if int(value + epsilon) != int(value):
                return int(value)
            elif int(value - epsilon) != int(value):
                return int(value - epsilon)
    
    return value
