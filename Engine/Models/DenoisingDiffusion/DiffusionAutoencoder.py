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
    import sys
    import logging

    from tensorflow.keras.models import Model
    from tensorflow.keras.layers import Dense
    from tensorflow.keras.layers import Input

    from tensorflow.keras.layers import Reshape
    from tensorflow.keras.layers import Flatten

    from tensorflow.keras.models import model_from_json
    from Engine.Activations.Activations import Activations

except ImportError as error:
    logging.error(error)
     
    sys.exit(-1)


DEFAULT_DIFFUSION_AUTOENCODER_LOSS = 'mse'
DEFAULT_DIFFUSION_AUTOENCODER_ENCODER_FILTERS = [320, 160]
DEFAULT_DIFFUSION_AUTOENCODER_DECODER_FILTERS = [160, 320]
DEFAULT_DIFFUSION_AUTOENCODER_LAST_LAYER_ACTIVATION = 'sigmoid'
DEFAULT_DIFFUSION_AUTOENCODER_LATENT_DIMENSION = 64
DEFAULT_DIFFUSION_AUTOENCODER_BATCH_SIZE_CREATE_EMBEDDING = 128
DEFAULT_DIFFUSION_AUTOENCODER_BATCH_SIZE_TRAINING = 64
DEFAULT_DIFFUSION_AUTOENCODER_INTERMEDIARY_ACTIVATION = 'swish'
DEFAULT_DIFFUSION_AUTOENCODER_INTERMEDIARY_ACTIVATION_ALPHA = 0.05
DEFAULT_DIFFUSION_AUTOENCODER_ACTIVATION_OUTPUT_ENCODER = 'sigmoid'



class DiffusionAutoencoderModel(Activations):
    """
    A LatentDiffusion Autoencoder model that combines an encoder-decoder architecture
    with diffusion-based latent space learning. This model enables flexible
    configuration of activation functions, layer structures, and loss functions,
    making it suitable for various generative and representation learning tasks.

    The autoencoder follows a variational approach, where the latent space
    undergoes a diffusion process to enhance feature disentanglement. This
    technique has been explored in deep generative models to improve the
    quality of generated data while preserving meaningful representations.

    References:
        - Ho, J., Jain, A., & Abbeel, P. (2020). "Denoising LatentDiffusion Probabilistic Models."
          Advances in Neural Information Processing Systems (NeurIPS).
          Available at: https://arxiv.org/abs/2006.11239

    Example:
        >>> model = DiffusionAutoencoderModel(
        ...     input_shape=128,
        ...     latent_dimension=32,
        ...     number_encoder_neurons=[256, 128, 64],
        ...     number_decoder_neurons=[64, 128, 256],
        ...     loss_function="mse",
        ...     last_activation="sigmoid",
        ...     activation_output_encoder="relu",
        ...     batch_size_create_embedding=32,
        ...     intermediary_activation_autoencoder="leaky_relu",
        ...     intermediary_activation_alpha=0.2
        ... )
    """
    def __init__(self, input_shape,
                 latent_dimension: int = DEFAULT_DIFFUSION_AUTOENCODER_LATENT_DIMENSION,
                 number_encoder_neurons=None,
                 number_decoder_neurons=None,
                 loss_function: str = DEFAULT_DIFFUSION_AUTOENCODER_LOSS,
                 last_activation: int = DEFAULT_DIFFUSION_AUTOENCODER_LAST_LAYER_ACTIVATION,
                 activation_output_encoder: str = DEFAULT_DIFFUSION_AUTOENCODER_ACTIVATION_OUTPUT_ENCODER,
                 batch_size_create_embedding: int = DEFAULT_DIFFUSION_AUTOENCODER_BATCH_SIZE_TRAINING,
                 intermediary_activation_autoencoder: str = DEFAULT_DIFFUSION_AUTOENCODER_INTERMEDIARY_ACTIVATION,
                 intermediary_activation_alpha: str = DEFAULT_DIFFUSION_AUTOENCODER_INTERMEDIARY_ACTIVATION_ALPHA):
        """
        Initializes the DiffusionAutoencoderModel with user-defined architecture
        and training parameters.

        Args:
            input_shape (int): Number of features in the input data.
            latent_dimension (int): Size of the latent space (bottleneck layer).
            number_encoder_neurons (list[int]): Number of neurons per encoder layer.
            number_decoder_neurons (list[int]): Number of neurons per decoder layer.
            loss_function (str): Loss function used during training.
            last_activation (str): Activation function for the final decoder layer.
            activation_output_encoder (str): Activation function for the encoder output.
            batch_size_create_embedding (int): Batch size used for embedding generation.
            intermediary_activation_autoencoder (str): Activation function for intermediate layers.
            intermediary_activation_alpha (float): Parameter for activations requiring an alpha value (e.g., LeakyReLU).
            :param input_shape:
            :param latent_dimension:
            :param number_encoder_neurons:
            :param number_decoder_neurons:
            :param loss_function:
            :param last_activation:
            :param activation_output_encoder:
            :param batch_size_create_embedding:
            :param intermediary_activation_autoencoder:
            :param intermediary_activation_alpha:
        """

        if number_decoder_neurons is None:
            number_decoder_neurons = DEFAULT_DIFFUSION_AUTOENCODER_DECODER_FILTERS

        if number_encoder_neurons is None:
            number_encoder_neurons = DEFAULT_DIFFUSION_AUTOENCODER_ENCODER_FILTERS

        self._decoder_model_loaded = None
        self._encoder_model_loaded = None
        self._input_shape = input_shape
        self._latent_dimension = latent_dimension
        self._list_number_neurons_per_layer_encoder = number_encoder_neurons
        self._list_number_neurons_per_layer_decoder = number_decoder_neurons
        self._intermediary_activation_function = intermediary_activation_autoencoder
        self._intermediary_activation_alpha = intermediary_activation_alpha
        self._activation_output_encoder = activation_output_encoder
        self._last_activation = last_activation
        self._loss_function = loss_function
        self._batch_size_create_embedding = batch_size_create_embedding
        self._neural_model = None

    def build_autoencoder(self):
        """
        Builds the full autoencoder model by combining the encoder and decoder.
        """
        encoder_input = Input(shape=(self._input_shape,))
        encoder_output = self._build_encoder(encoder_input)

        decoder_output = self._build_decoder(encoder_output)

        # Define the full autoencoder model
        self._neural_model = Model(encoder_input, decoder_output)

    def _build_encoder(self, encoder_input):
        """
        Builds the encoder part of the autoencoder.

        Args:
            encoder_input: Input layer for the encoder.

        Returns:
            Encoder output tensor.
        """
        neural_model_encoder = encoder_input
        neural_model_encoder = Flatten()(neural_model_encoder)

        # Add encoder hidden layers
        for number_neurons in self._list_number_neurons_per_layer_encoder:
            neural_model_encoder = Dense(number_neurons)(neural_model_encoder)
            neural_model_encoder = self._add_activation_layer(neural_model_encoder, self._intermediary_activation_function)

        # Latent space layer
        neural_model_encoder = Dense(self._latent_dimension)(neural_model_encoder)
        neural_model_encoder = self._add_activation_layer(neural_model_encoder, self._activation_output_encoder)

        # Reshape to add spatial dimension to latent vector
        neural_model_encoder = Reshape((self._latent_dimension, 1), name='output_encoder')(neural_model_encoder)

        return neural_model_encoder

    def _build_decoder(self, neural_model_decoder):
        """
        Builds the decoder part of the autoencoder.

        Args:
            neural_model_decoder: Input tensor from the encoder.

        Returns:
            Decoder output tensor.
        """
        neural_model_decoder = Flatten(name='input_decoder')(neural_model_decoder)

        # Initial dense layer in decoder
        neural_model_decoder = Dense(self._latent_dimension)(neural_model_decoder)
        neural_model_decoder = self._add_activation_layer(neural_model_decoder, self._intermediary_activation_function)

        # Add decoder hidden layers
        for number_neurons in self._list_number_neurons_per_layer_decoder:
            neural_model_decoder = Dense(number_neurons)(neural_model_decoder)
            neural_model_decoder = self._add_activation_layer(neural_model_decoder, self._intermediary_activation_function)

        # Output layer, reconstructing input shape
        neural_model_decoder = Dense(self._input_shape)(neural_model_decoder)
        neural_model_decoder = self._add_activation_layer(neural_model_decoder, self._last_activation)

        return neural_model_decoder

    def load_model(self, json_path, weights_path):
        """
        Loads the autoencoder model architecture and weights from files.

        Args:
            json_path (str): Path to the JSON file containing the model architecture.
            weights_path (str): Path to the file containing model weights.
        """
        with open(json_path, 'r') as json_file:
            loaded_model_json = json_file.read()

        self._neural_model = model_from_json(loaded_model_json)
        self._neural_model.load_weights(weights_path)

    def get_encoder_and_decoder(self):
        """
        Builds and retrieves the encoder and decoder models from the trained autoencoder.

        Returns:
            tuple: (Encoder model, Decoder model)

        Raises:
            ValueError: If the autoencoder model has not been built.
        """
        self.build_autoencoder()
        if self._neural_model is None:
            raise ValueError("The model has not been built yet. Please build the model first by calling `build_autoencoder()`.")

        # Extract encoder part
        encoder_output_layer = self._neural_model.get_layer(name='output_encoder')
        self._encoder_model_loaded = Model(inputs=self._neural_model.input,
                                           outputs=encoder_output_layer.output, name="EncoderModel")

        # Build decoder model
        latent_input = Input(shape=(self._latent_dimension, 1))
        neural_flow = latent_input
        decoder_input_layer = self._neural_model.get_layer(name='input_decoder')
        decoder_output = decoder_input_layer(neural_flow)

        # Pass through decoder layers
        for layer in self._neural_model.layers[self._neural_model.layers.index(decoder_input_layer) + 1:]:
            decoder_output = layer(decoder_output)

        self._decoder_model_loaded = Model(latent_input, decoder_output, name="DecoderModel")

        return self._encoder_model_loaded, self._decoder_model_loaded

    def training(self, x_train_data, epochs, batch_size):
        """
        Compiles and trains the autoencoder model.

        Args:
            x_train_data (ndarray): Training data (inputs and targets are the same).
            epochs (int): Number of training epochs.
            batch_size (int): Batch size for training.
        """
        self._neural_model.compile(loss=self._loss_function)
        self._neural_model.fit(x_train_data, x_train_data, epochs=epochs, batch_size=batch_size, validation_split=0.2)

    def create_embedding(self, data):
        """
        Generates latent space embeddings using the trained encoder.

        Args:
            data (ndarray): Input data to encode.

        Returns:
            ndarray: Latent space representations.
        """
        return self._encoder_model_loaded.predict(data, batch_size=self._batch_size_create_embedding)


    @property
    def input_shape(self):
        """Get the input shape of the model."""
        return self._input_shape

    @input_shape.setter
    def input_shape(self, value):
        if not isinstance(value, int) or value <= 0:
            raise ValueError("Input shape must be a positive integer")
        self._input_shape = value

    @property
    def latent_dimension(self):
        """Get the latent dimension size."""
        return self._latent_dimension

    @latent_dimension.setter
    def latent_dimension(self, value):
        if not isinstance(value, int) or value <= 0:
            raise ValueError("Latent dimension must be a positive integer")
        self._latent_dimension = value

    @property
    def encoder_neurons(self):
        """Get the list of neurons per encoder layer."""
        return self._list_number_neurons_per_layer_encoder

    @encoder_neurons.setter
    def encoder_neurons(self, value):
        if not isinstance(value, list) or not all(isinstance(x, int) and x > 0 for x in value):
            raise ValueError("Encoder neurons must be a list of positive integers")
        self._list_number_neurons_per_layer_encoder = value

    @property
    def decoder_neurons(self):
        """Get the list of neurons per decoder layer."""
        return self._list_number_neurons_per_layer_decoder

    @decoder_neurons.setter
    def decoder_neurons(self, value):
        if not isinstance(value, list) or not all(isinstance(x, int) and x > 0 for x in value):
            raise ValueError("Decoder neurons must be a list of positive integers")
        self._list_number_neurons_per_layer_decoder = value

    @property
    def intermediary_activation(self):
        """Get the intermediary activation function."""
        return self._intermediary_activation_function

    @intermediary_activation.setter
    def intermediary_activation(self, value):
        if not isinstance(value, str):
            raise ValueError("Intermediary activation must be a string")
        self._intermediary_activation_function = value

    @property
    def intermediary_activation_alpha(self):
        """Get the alpha parameter for intermediary activation."""
        return self._intermediary_activation_alpha

    @intermediary_activation_alpha.setter
    def intermediary_activation_alpha(self, value):
        if not isinstance(value, (int, float)) or value < 0:
            raise ValueError("Intermediary activation alpha must be a non-negative number")
        self._intermediary_activation_alpha = value

    @property
    def encoder_output_activation(self):
        """Get the encoder output activation function."""
        return self._activation_output_encoder

    @encoder_output_activation.setter
    def encoder_output_activation(self, value):
        if not isinstance(value, str):
            raise ValueError("Encoder output activation must be a string")
        self._activation_output_encoder = value

    @property
    def last_activation(self):
        """Get the last layer activation function."""
        return self._last_activation

    @last_activation.setter
    def last_activation(self, value):
        if not isinstance(value, str):
            raise ValueError("Last activation must be a string")
        self._last_activation = value

    @property
    def loss_function(self):
        """Get the loss function."""
        return self._loss_function

    @loss_function.setter
    def loss_function(self, value):
        if not isinstance(value, str):
            raise ValueError("Loss function must be a string")
        self._loss_function = value

    @property
    def batch_size_create_embedding(self):
        """Get the batch size for embedding creation."""
        return self._batch_size_create_embedding

    @batch_size_create_embedding.setter
    def batch_size_create_embedding(self, value):
        if not isinstance(value, int) or value <= 0:
            raise ValueError("Batch size must be a positive integer")
        self._batch_size_create_embedding = value

    @property
    def neural_model(self):
        """Get the neural model."""
        return self._neural_model

    @neural_model.setter
    def neural_model(self, value):
        self._neural_model = value

    @property
    def encoder_model_loaded(self):
        """Get the loaded encoder model."""
        return self._encoder_model_loaded

    @encoder_model_loaded.setter
    def encoder_model_loaded(self, value):
        self._encoder_model_loaded = value

    @property
    def decoder_model_loaded(self):
        """Get the loaded decoder model."""
        return self._decoder_model_loaded

    @decoder_model_loaded.setter
    def decoder_model_loaded(self, value):
        self._decoder_model_loaded = value
