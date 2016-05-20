import time
n = 100000
x=1
y=-1
t1=time.clock()
for i in range(n):
    if x==1:
        pass
    elif x==2:
        pass
    elif x==3:
        pass
    else:
        if y<=0:pass
t2=time.clock()
print t2-t1


def test(func):
    func()

def ch():
    global y
    if y<=0:pass


def ch2():
    pass

test=ch
t1=time.clock()
for i in range(n):
    pass
t2=time.clock()
print t2-t1

test=ch2
t3=time.clock()
for i in range(n):
    test()
t4=time.clock()
print t4-t3
print t4-t3-t2+t1
