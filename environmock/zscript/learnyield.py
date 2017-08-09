
def infinite(tracev):
    next = True
    while next:
        yield tracev, tracev+1
        tracev += 1

x = infinite(10)
for i in range(11):
    print(next(x))

print 2 ** 65536