import math

print(math.modf(66/8))
print(66/8)

process = []
numberOfThreads = 12
indexJump = int(math.modf(66/numberOfThreads)[1]+1)
for i in range(numberOfThreads):
    if i == 0:
        process.append([[1,indexJump],1])
    elif i == numberOfThreads-1:
        process.append([[i*indexJump,67],i*indexJump])
    else:
        process.append([[i*indexJump,(i+1)*indexJump],i*indexJump])

for i in process:
    print(i, str(i[0][1]-i[0][0]))
print(len(process))