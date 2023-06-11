from mrjob.job import MRJob
from mrjob.protocol import RawValueProtocol
import math

class KMeansIteration(MRJob):
    # Method to configure command line arguments
    def configure_args(self):
        super(KMeansIteration, self).configure_args()
        self.add_passthru_arg('--centers', help='comma-separated list of centers')

    # Method to initialize the mapper and load the center values from the command line arguments
    def mapper_init(self):
        centers = list(map(float, self.options.centers.split(',')))
        self.centers = [(centers[i], centers[i+1]) for i in range(0, len(centers), 2)]

    # Mapper method to calculate the closest center for each data point and emit the key-value pair
    def mapper(self, _, line):
        data = list(map(float, line.split(',')))
        distances = [math.sqrt((data[0]-center[0])**2 + (data[1]-center[1])**2) for center in self.centers]
        closest_center_index = distances.index(min(distances))
        yield closest_center_index, data

    # Reducer method to calculate the new center for each cluster and emit the key-value pair
    def reducer(self, key, values):
        new_center = [0.0, 0.0]
        count = 0
        for value in values:
            new_center[0] += value[0]
            new_center[1] += value[1]
            count += 1
        new_center[0] /= count
        new_center[1] /= count
        yield key, new_center

    # Set the input protocol to RawValueProtocol
    INPUT_PROTOCOL = RawValueProtocol


if __name__ == '__main__':
    KMeansIteration.run()

