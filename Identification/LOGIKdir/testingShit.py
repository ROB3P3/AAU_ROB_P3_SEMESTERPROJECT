import math
from fractions import Fraction


process = []
numberOfThreads = 14
indexJump = int(math.modf(66/numberOfThreads)[1])
optimizeFraction = Fraction(math.modf(66/numberOfThreads)[0]).limit_denominator(1000000)
Offset = (numberOfThreads/optimizeFraction.denominator)*optimizeFraction.numerator
indexOffsetEnd = 0
indexOffsetStart = 0
for i in range(numberOfThreads):
    if Offset != 0:
        indexOffsetEnd +=1
        Offset -= 1
    if i == 0:
        if Offset != 0:
            indexOffsetEnd +=1
            Offset -= 1
        process.append([[1,indexJump+indexOffsetEnd],1])
    elif i == numberOfThreads-1:
        process.append([[i*indexJump+indexOffsetStart,67],i*indexJump+indexOffsetStart])
    else:
        process.append([[i*indexJump+indexOffsetStart,(i+1)*indexJump+indexOffsetEnd],i*indexJump+indexOffsetStart])
    indexOffsetStart = indexOffsetEnd


for i in process:
    print(i, str(i[0][1]-i[0][0]))
print(len(process))

print(math.modf(66/numberOfThreads))
print(math.modf(66/numberOfThreads)[0]*16)
print(Fraction(math.modf(66/numberOfThreads)[0]).limit_denominator(1000000))
print((numberOfThreads/optimizeFraction.denominator)*optimizeFraction.numerator)