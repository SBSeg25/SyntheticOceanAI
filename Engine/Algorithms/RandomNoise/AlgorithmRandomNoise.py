#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = 'Synthetic Ocean AI - Team'
__email__ = 'syntheticoceanai@gmail.com'
__version__ = '{1}.{0}.{1}'
__initial_data__ = '2022/06/01'
__last_update__ = '2025/03/29'
__credits__ = ['Synthetic Ocean AI']


# MIT License
#
# Copyright (c) 2025 Synthetic Ocean AI
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.


try:
    import os
    import sys

    import json
    import numpy

    import random
    import logging
    import tensorflow

    from abc import ABC

    from tensorflow.keras import Model

    from tensorflow.keras.utils import to_categorical
    from tensorflow.keras.losses import BinaryCrossentropy

except ImportError as error:
    print(error)
    sys.exit(-1)


class RandomNoiseAlgorithm:
    """
    A class that organizes data samples based on class labels, applies random noise,
    and generates synthetic samples based on provided class labels.

    This algorithm allows for:
    - Storing and retrieving samples based on their class labels.
    - Introducing noise to the samples using the salt-and-pepper method.
    - Generating synthetic samples based on class distributions.

    Mathematical Definition:
        - Let X be the input samples with shape (n, d), where n is the number of samples and d is the feature dimension.
        - Let Y be the one-hot encoded labels with shape (n, c), where c is the number of classes.
        - The dictionary of samples is defined as:

            D = { k: { x_i for which y_ik = 1 } }

    where each sample x_i is mapped to its corresponding class label k.

        - Noise is applied to features with probability p as follows:

            x'_ij = 1 - x_ij, if u_ij <= p
            x'_ij = x_ij, otherwise
            where u_ij is a random value sampled from a uniform distribution U(0,1).

    - Synthetic samples are generated by retrieving samples based on specified class distributions and rounding them:

        x̃_i = round(x_i)

    Example:
        >>> python
        ...     model = RandomAlgorithm(noise_level=0.1, noise_type='salt_and_pepper')
        ...     model.fit(X_train, Y_train)
        ...     noisy_samples = model.predict([0, 1, 2])
        >>>     generated_samples = model.get_samples({"classes": {0: 5, 1: 10}})

    """


    def __init__(self,
                 noise_level,
                 noise_type,
                 *args, **kwargs):

        super().__init__(*args, **kwargs)

        # Initialize instance variables with provided or default values
        self._noise_level = noise_level
        self._noise_type = noise_type
        self._dictionary_samples = {}

    def compile(self):
        pass

    def fit(self, x, y):
        """
        Organizes samples into a dictionary where the keys are class labels
        (determined using argmax on one-hot encoded labels) and the values
        are lists of samples belonging to each class.

        Args:
            x (array-like): Samples, shape (num_samples, feature_dim)
            y (array-like): One-hot encoded labels, shape (num_samples, num_classes)
        """
        self._dictionary_samples = {}

        for sample, label in zip(x, y):

            # Convert one-hot encoding to class index
            class_label = numpy.argmax(label)


            if class_label not in self._dictionary_samples:
                self._dictionary_samples[class_label] = []

            self._dictionary_samples[class_label].append(sample)

        # Convert lists to numpy arrays for consistency
        for key in self._dictionary_samples:
            self._dictionary_samples[key] = numpy.array(self._dictionary_samples[key])

        print(self._dictionary_samples)


    def predict(self, labels):
        """
        Selects random samples based on given class labels and applies salt-and-pepper noise.

        Args:
            labels (list[int]): List of class labels to fetch samples from.

        Returns:
            np.ndarray: Array of selected and noised samples.
        """
        # List to store noisy samples
        noisy_samples = []

        # Iterate over each provided label
        for label in labels:

            # Check if there are available samples for the given label
            if label in self._dictionary_samples and len(self._dictionary_samples[label]) > 0:

                # Select a random sample
                sample = random.choice(self._dictionary_samples[label])
                sample = numpy.array(sample, dtype=numpy.float32)

                # Generate a noise mask
                noise_mask = numpy.random.rand(*sample.shape) <= self._noise_level

                # Apply salt-and-pepper noise
                sample_noisy = numpy.where(noise_mask, 1 - sample, sample)

                # Add the noisy sample to the list
                noisy_samples.append(sample_noisy)

            else:
                noisy_samples.append(None)

        # Return an array containing noisy samples, preserving None values
        return numpy.array(noisy_samples, dtype=object)

    def get_samples(self, number_samples_per_class):


        # Dictionary to store generated samples for each class.
        generated_data = {}

        # Loop through each class and the desired number of samples for that class.
        for label_class, number_instances in number_samples_per_class["classes"].items():

            # Generate synthetic samples using the generator.
            generated_samples = self.predict([label_class] * number_instances)
            # Store generated samples for the current class.
            generated_data[label_class] = generated_samples

        # Return the dictionary containing generated samples for all requested classes.
        return generated_data

    def save_model(self, directory, file_name):
        """
        Save the encoder and decoder models in both JSON and H5 formats.

        Args:
            directory (str): Directory where models will be saved.
            file_name (str): Base file name for saving models.
        """
        pass

    @staticmethod
    def _save_model_to_json(model, file_path):
        """
        Save model architecture to a JSON file.

        Args:
            model (tf.keras.Model): Model to save.
            file_path (str): Path to the JSON file.
        """
        pass

    def load_models(self, directory, file_name):
        """
        Load the generator and discriminator models from a directory.

        Args:
            directory (str): Directory where models are stored.
            file_name (str): Base file name for loading models.
        """
        pass

    @staticmethod
    def summary():
        logging.info("D = { k: { x_i for which y_ik = 1 } }")