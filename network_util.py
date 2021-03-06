# -*- coding: utf-8 -*-

import sys
import numpy as np
from base_vgg16 import Vgg16
import tensorflow as tf

def fully_connected(input_layer, shape, name="", is_training=True, use_batchnorm=True, activation=tf.nn.relu):
    with tf.variable_scope("fully" + name):
        kernel = tf.get_variable("weights", shape=shape, \
            dtype=tf.float32, initializer=tf.truncated_normal_initializer(stddev=0.01))
        fully = tf.matmul(input_layer, kernel)
        if activation:
            fully = activation(fully)
        if use_batchnorm:
            fully = batch_norm(fully, is_training)
        return fully

def vgg_fully(input_layer, shape, name="", activation=tf.nn.relu):
    with tf.variable_scope(name):
        kernel = tf.get_variable("weights", shape=shape, \
            dtype=tf.float32, initializer=tf.truncated_normal_initializer(stddev=0.01))
        b = tf.get_variable("biases", shape=[shape[1]], initializer=tf.constant_initializer(0.0))
        fully = tf.matmul(input_layer, kernel)
        fully = tf.nn.bias_add(fully, b)
        if activation:
            fully = activation(fully)
        return fully

def batch_norm(inputs, phase_train, decay=0.9, eps=1e-5):
    """Batch Normalization

       Args:
           inputs: input data(Batch size) from last layer
           phase_train: when you test, please set phase_train "None"
       Returns:
           output for next layer
    """
    gamma = tf.get_variable("gamma", shape=inputs.get_shape()[-1], dtype=tf.float32, initializer=tf.constant_initializer(1.0))
    beta = tf.get_variable("beta", shape=inputs.get_shape()[-1], dtype=tf.float32, initializer=tf.constant_initializer(0.0))
    pop_mean = tf.get_variable("pop_mean", trainable=False, shape=inputs.get_shape()[-1], dtype=tf.float32, initializer=tf.constant_initializer(0.0))
    pop_var = tf.get_variable("pop_var", trainable=False, shape=inputs.get_shape()[-1], dtype=tf.float32, initializer=tf.constant_initializer(1.0))
    axes = range(len(inputs.get_shape()) - 1)

    if phase_train is not None:
        batch_mean, batch_var = tf.nn.moments(inputs, axes)
        train_mean = tf.assign(pop_mean, pop_mean * decay + batch_mean*(1 - decay))
        train_var = tf.assign(pop_var, pop_var * decay + batch_var * (1 - decay))
        with tf.control_dependencies([train_mean, train_var]):
            return tf.nn.batch_normalization(inputs, batch_mean, batch_var, beta, gamma, eps)
    else:
        return tf.nn.batch_normalization(inputs, pop_mean, pop_var, beta, gamma, eps)

def convBNLayer(input_layer, use_batchnorm, is_training, input_dim, output_dim, \
                kernel_size, stride, activation=tf.nn.relu, padding="SAME", name="", atrous=False, rate=1):
    with tf.variable_scope("convBN" + name):
        w = tf.get_variable("weights", \
            shape=[kernel_size, kernel_size, input_dim, output_dim], initializer=tf.contrib.layers.xavier_initializer())

        if atrous:
            conv = tf.nn.atrous_conv2d(input_layer, w, rate, padding="SAME")
        else:
            conv = tf.nn.conv2d(input_layer, w, strides=[1, stride, stride, 1], padding=padding)

        if use_batchnorm:
            if activation is not None:
                conv = activation(conv)
            bn = batch_norm(conv, is_training)
            return bn

        b = tf.get_variable("bias", \
            shape=[output_dim], initializer=tf.constant_initializer(0.0))
        bias = tf.nn.bias_add(conv, b)
        if activation is not None:
            return activation(bias)
        return bias

def convLayer(input_layer, input_dim, output_dim, \
                kernel_size, stride, activation=tf.nn.relu, padding="SAME", name=""):
    with tf.variable_scope(name):
        w = tf.get_variable("filter", \
            shape=[kernel_size, kernel_size, input_dim, output_dim], initializer=tf.contrib.layers.xavier_initializer())

        conv = tf.nn.conv2d(input_layer, w, strides=[1, stride, stride, 1], padding=padding)

        b = tf.get_variable("biases", shape=[output_dim], initializer=tf.constant_initializer(0.0))
        bias = tf.nn.bias_add(conv, b)
        if activation is not None:
            return activation(bias)
        return bias

def maxpool2d(x, kernel=2, stride=2, name="", padding="SAME"):
    """define max pooling layer"""
        return tf.nn.max_pool(
            x,
            ksize = [1, kernel, kernel, 1],
            strides = [1, stride, stride, 1],
            padding=padding,
            name=name)
