import matplotlib.pyplot as plt

file_path = "./count.txt"
data=[]
with open(file_path, "r") as file:
 	for line in file:
		#iif(int(line.strip())>100000 or int(line.strip())<100000):
    		data.append(int(line.strip()))

indices = list(range(len(data)))
plt.figure(figsize=(12, 6))
plt.scatter(indices, data,s=3, alpha=0.75, edgecolors='black')

plt.xlabel("Index")
plt.ylabel("Count")

plt.grid(axis='y', linestyle='--', alpha=0.7)
plt.show()
