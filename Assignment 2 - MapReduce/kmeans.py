from kmeans_iteration import KMeansIteration
import math


# Function to run the KMeans algorithm on the input data
def run_kmeans(data_path, centers, threshold=0.01, max_iterations=10):
    # Store the initial centers to check for convergence later
    old_centers = centers

    # Loop through the maximum number of iterations
    for i in range(max_iterations):
        print(f'Iteration {i + 1}')

        # Set up the arguments for the KMeansIteration MRJob
        job_args = [
            data_path,
            '--centers', ','.join(map(str, centers)),
            '-r', 'hadoop',
            '--hadoop-streaming-jar',
            '/home/mainuser/hadoop/hadoop-3.3.5/share/hadoop/tools/lib/hadoop-streaming-3.3.5.jar'
        ]

        # Create a new instance of the KMeansIteration MRJob and run it
        job = KMeansIteration(args=job_args)
        with job.make_runner() as runner:
            runner.run()

            # Collect the new centers from the output of the MRJob
            centers = []
            for _, center in job.parse_output(runner.cat_output()):
                centers.extend(center)
                print(center)

        # Check for convergence
        if converged(old_centers, centers, threshold):
            print('Converged')
            break

        # Update old_centers to be the current centers for the next iteration
        old_centers = centers


# Function to check for convergence between the old and new centers
def converged(old_centers, new_centers, threshold):
    total_distance = 0
    for i in range(0, len(old_centers), 2):
        # Calculate the Euclidean distance between the old and new centers
        total_distance += math.sqrt(
            (old_centers[i] - new_centers[i]) ** 2 + (old_centers[i + 1] - new_centers[i + 1]) ** 2)
    average_distance = total_distance / (len(old_centers) / 2)
    print(f'Average distance: {average_distance}')
    print(f'Threshold: {threshold}')
    return average_distance < threshold


if __name__ == '__main__':
    data_path = 'hdfs://localhost:9000/user/mainuser/clustered_data.txt'

    # Read the coordinates from the centroids.txt file
    with open('centroids.txt', 'r') as f:
        x1, y1 = map(float, f.readline().split())
        x2, y2 = map(float, f.readline().split())
        x3, y3 = map(float, f.readline().split())

    initial_centers = [x1, y1, x2, y2, x3, y3]

    # Run the KMeans algorithm
    run_kmeans(data_path, initial_centers)