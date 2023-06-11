import random
import numpy as np

# Read the coordinates from the centroids.txt file
with open('centroids.txt', 'r') as f:
    x1, y1 = map(float, f.readline().split())
    x2, y2 = map(float, f.readline().split())
    x3, y3 = map(float, f.readline().split())

# The three centers are stored in the variables x1, y1, x2, y2, x3, y3
# These values are read from the centroids.txt file, which contains the x and y coordinates
# of each of the three centers.

print("Initial centers:")
print(f"Center 1: ({x1}, {y1})")
print(f"Center 2: ({x2}, {y2})")
print(f"Center 3: ({x3}, {y3})")
print()

# Print the initial centers to the console for debugging purposes.

n = 2000000
data = []

# The code will generate 2 million (x, y) data points, which will be stored in the data list.

for i in range(n):
    # Generate a random distance with some randomness added
    r = abs(np.random.normal(loc=0, scale=3)) + abs(np.random.normal(loc=0, scale=2))

    # Add the generated distance to one of the three centers chosen randomly
    center = random.choice([(x1, y1), (x2, y2), (x3, y3)])
    x, y = center[0] + r * np.random.normal(loc=0, scale=1), center[1] + r * np.random.normal(loc=0, scale=1)

    # Add the generated (x, y) point to our data list
    data.append((x, y))

# This loop generates 2 million (x, y) data points. For each point, a random distance r is generated using the
# normal distribution with mean 0 and standard deviation 3, with an additional normal distribution with mean 0 and
# standard deviation 2 added to introduce more randomness. Then, one of the three centers is chosen randomly,
# and the generated distance r is added to the x and y coordinates of the center. The resulting (x, y) point is
# added to the data list.

# Save the generated data to a text file
with open('clustered_data.txt', 'w') as file:
    for x, y in data:
        file.write(f"{x}, {y}\n")

# Finally, the generated data is saved to a text file named "clustered_data.txt", with each point on a new line.

print("Data generation complete")
print(n, "data points saved to 'clustered_data.txt'")

# Print a message indicating that the data generation is complete and how many data points were generated and saved.