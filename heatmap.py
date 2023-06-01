import os
import matplotlib.pyplot as plt
import numpy as np

np.set_printoptions(threshold=np.inf)
# generate 2 2d grids for the x & y bounds
y, x = np.meshgrid(np.linspace(-4, 4, 150), np.linspace(-4, 4, 150))

z = (1 - x / 2. + x ** 5 + y ** 3) * np.exp(-x ** 2 - y ** 2)
# z should be the value *within* x and y, which are bounds.
print(" x -------", x.shape)
print(x)
print(" y -------", y.shape)
print(y)
print(" z -------", z.shape)
print(z)
# Hence, removing the last value from the z array.
z = z[:-1, :-1]
z_min, z_max = -np.abs(z).max(), np.abs(z).max()

fig, ax = plt.subplots()

c = ax.pcolormesh(x, y, z, cmap='OrRd', vmin=z_min, vmax=z_max)
ax.set_title('pcolormesh')

# setting the limits of the plot to the limits of the data
ax.axis([x.min(), x.max(), y.min(), y.max()])
fig.colorbar(c, ax=ax)







y, x = np.meshgrid(np.linspace(0, 1, 50), np.linspace(0, 1, 50))
data = np.zeros((50, 50))
print(data.shape)

filename = os.path.join(os.getcwd(), 'kairos_258.txt')
with open(filename, 'r') as file :
    contents = file.readlines()

for line in contents :
    split_line = line.split('\t')
    xx = int((float)(split_line[6]) * 50)
    yy = int((float)(split_line[7]) * 50)
    data[xx][yy] += 1
    print(xx, yy, data[xx][yy])

print(data)

data = data[:-1, :-1]
data_min, data_max = -np.abs(data).max(), np.abs(data).max()

fig, ax = plt.subplots()

c = ax.pcolormesh(x, y, data, cmap='jet', vmin=data_min, vmax=data_max)
ax.set_title('pcolormesh')

# setting the limits of the plot to the limits of the data
ax.axis([x.min(), x.max(), y.min(), y.max()])
fig.colorbar(c, ax=ax)


plt.show()

