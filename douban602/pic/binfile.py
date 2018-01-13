di = {1:1,2:5}

f=open('123.data','w')
f.write(str(di))
f.close()

g=open('123.data','r')
x = g.read()
print x

print eval(x)==f
