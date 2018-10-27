values=[20,66,12,48,38,38,20,65,54]
i=0
j=1
profits=[]
while i<len(values):
	j=i+1
	for j in range(j,len(values)):
		profit=values[j]-values[i]
		profits.append(profit)
		j+=1
	i+=1
print(profits)
print(max(profits))

# Create your tests here.
