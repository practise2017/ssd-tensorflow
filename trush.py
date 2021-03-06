def build_model(self, input_layer, use_batchnorm=False, is_training=True, atrous=False, activation=tf.nn.relu, lr_mult=1):
    if atrous:
        self.pool_5 = maxpool2d(input_layer, kernel=3, stride=1, name="pool5")
    else:
        self.pool_5 = maxpool2d(input_layer, kernel=2, stride=2, name="pool5")
    self.conv_6 = convBNLayer(self.pool_5, use_batchnorm, is_training, 512, 1024, 3, 1, name="conv_6", activation=activation)
    self.conv_7 = convBNLayer(self.conv_6, use_batchnorm, is_training, 1024, 1024, 1, 1, name="conv_7", activation=activation)
    self.conv_8_1 = convBNLayer(self.conv_7, use_batchnorm, is_training, 1024, 256, 1, 1, name="conv_8_1", activation=activation)
    self.conv_8_2 = convBNLayer(self.conv_8_1, use_batchnorm, is_training, 256, 512, 3, 2, name="conv_8_2", activation=activation)
    self.conv_9_1 = convBNLayer(self.conv_8_2, use_batchnorm, is_training, 512, 128, 1, 1, name="conv_9_1", activation=activation)
    self.conv_9_2 = convBNLayer(self.conv_9_1, use_batchnorm, is_training, 128, 256, 3, 2, name="conv_9_2", activation=activation)
    self.conv_10_1 = convBNLayer(self.conv_9_2, use_batchnorm, is_training, 256, 128, 1, 1, name="conv_10_1", activation=activation)
    self.conv_10_2 = convBNLayer(self.conv_10_1, use_batchnorm, is_training, 128, 256, 3, 1, name="conv_10_2", activation=activation, padding="VALID")
    self.conv_11_1 = convBNLayer(self.conv_10_2, use_batchnorm, is_training, 256, 128, 1, 1, name="conv_11_1", activation=activation)
    self.conv_11_2 = convBNLayer(self.conv_11_1, use_batchnorm, is_training, 128, 256, 3, 1, name="conv_11_2", activation=activation, padding="VALID")


def extended_model(input_layer, use_batchnorm=False, is_training=True, activation=tf.nn.relu, lr_mult=1):
    # kernel_dim = [512, 256, 512, 128, 256, 128, 256, 128, 256]
    conv_6 = convBNLayer(input_layer, use_batchnorm, is_training, 512, 1024, 3, 1, name="conv_6", activation=activation)
    conv_7 = convBNLayer(conv_6, use_batchnorm, is_training, 1024, 1024, 1, 1, name="conv_7", activation=activation)
    conv_8_1 = convBNLayer(conv_7, use_batchnorm, is_training, 1024, 256, 1, 1, name="conv_8_1", activation=activation)
    conv_8_2 = convBNLayer(conv_8_1, use_batchnorm, is_training, 256, 512, 3, 2, name="conv_8_2", activation=activation)
    conv_9_1 = convBNLayer(conv_8_2, use_batchnorm, is_training, 512, 128, 1, 1, name="conv_9_1", activation=activation)
    conv_9_2 = convBNLayer(conv_9_1, use_batchnorm, is_training, 128, 256, 3, 2, name="conv_9_2", activation=activation)
    conv_10_1 = convBNLayer(conv_9_2, use_batchnorm, is_training, 256, 128, 1, 1, name="conv_10_1", activation=activation)
    conv_10_2 = convBNLayer(conv_10_1, use_batchnorm, is_training, 128, 256, 3, 1, name="conv_10_2", activation=activation, padding="VALID")
    conv_11_1 = convBNLayer(conv_10_2, use_batchnorm, is_training, 256, 128, 1, 1, name="conv_11_1", activation=activation)
    conv_11_2 = convBNLayer(conv_11_1, use_batchnorm, is_training, 128, 256, 3, 1, name="conv_11_2", activation=activation, padding="VALID")

    return conv_11_2


#!/usr/bin/env python3
import sys
sys.path.append("/Users/tsujiyuuki/env_python/code/my_code/Data_Augmentation")
import numpy as np
from base_vgg16 import Vgg16 as Vgg
import tensorflow as tf

def batch_norm(inputs, is_training, decay=0.9, eps=1e-5):
    """Batch Normalization

       Args:
           inputs: input data(Batch size) from last layer
           is_training: when you test, please set is_training "None"
       Returns:
           output for next layer
    """
    gamma = tf.Variable(tf.ones(inputs.get_shape()[1:]), name="gamma")
    beta = tf.Variable(tf.zeros(inputs.get_shape()[1:]), name="beta")
    pop_mean = tf.Variable(tf.zeros(inputs.get_shape()[1:]), trainable=False, name="pop_mean")
    pop_var = tf.Variable(tf.ones(inputs.get_shape()[1:]), trainable=False, name="pop_var")

    if is_training != None:
        batch_mean, batch_var = tf.nn.moments(inputs, [0])
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

        if use_batchnorm != None:
            bn = batch_norm(conv, is_training)
            if activation != None:
                return activation(conv, name="activation")
            return bn

        if activation != None:
            return activation(conv, name="activation")
        return conv

def maxpool2d(x, kernel=2, stride=1, name="", padding="SAME"):
    """define max pooling layer"""
    with tf.variable_scope("pool" + name):
        return tf.nn.max_pool(
            x,
            ksize = [1, kernel, kernel, 1],
            strides = [1, stride, stride, 1],
            padding=padding)

class ExtendedLayer(object):
    def __init__(self):
        pass

    def build_model(self, input_layer, use_batchnorm=None, is_training=True, atrous=False, \
                    rate=1, activation=tf.nn.relu, lr_mult=1):
        if atrous:
            self.pool_5 = maxpool2d(input_layer, kernel=3, stride=1, name="pool5", padding="SAME")
        else:
            self.pool_5 = maxpool2d(input_layer, kernel=2, stride=2, name="pool5", padding="VALID") #TODO: padding is valid or same

        kernel_size = 3
        if atrous:
            rate *= 6
            pad = int(((kernel_size + (rate - 1) * (kernel_size - 1)) - 1) / 2)
            self.conv_6 = convBNLayer(self.pool_5, use_batchnorm, is_training, 512, 1024, kernel_size, 1, \
                                      name="conv_6", activation=tf.nn.relu, atrous=atrous, rate=rate)
        else:
            rate *= 3
            pad = int(((kernel_size + (rate - 1) * (kernel_size - 1)) - 1) / 2)
            self.conv_6 = convBNLayer(self.pool_5, use_batchnorm, is_training, 512, 1024, kernel_size, 1, \
                                      name="conv_6", activation=tf.nn.relu, atrous=atrous, rate=rate)

        self.conv_7 = convBNLayer(self.conv_6, use_batchnorm, is_training, 1024, 1024, 1, 1, name="conv_7", activation=activation)
        self.conv_8_1 = convBNLayer(self.conv_7, use_batchnorm, is_training, 1024, 256, 1, 1, name="conv_8_1", activation=activation)
        self.conv_8_2 = convBNLayer(self.conv_8_1, use_batchnorm, is_training, 256, 512, 3, 2, name="conv_8_2", activation=activation)
        self.conv_9_1 = convBNLayer(self.conv_8_2, use_batchnorm, is_training, 512, 128, 1, 1, name="conv_9_1", activation=activation)
        self.conv_9_2 = convBNLayer(self.conv_9_1, use_batchnorm, is_training, 128, 256, 3, 2, name="conv_9_2", activation=activation)
        self.conv_10_1 = convBNLayer(self.conv_9_2, use_batchnorm, is_training, 256, 128, 1, 1, name="conv_10_1", activation=activation)
        self.conv_10_2 = convBNLayer(self.conv_10_1, use_batchnorm, is_training, 128, 256, 3, 1, name="conv_10_2", activation=activation, padding="VALID")
        self.conv_11_1 = convBNLayer(self.conv_10_2, use_batchnorm, is_training, 256, 128, 1, 1, name="conv_11_1", activation=activation)
        self.conv_11_2 = convBNLayer(self.conv_11_1, use_batchnorm, is_training, 128, 256, 3, 1, name="conv_11_2", activation=activation, padding="VALID")

def ssd_model(sess, images, labels=None, vggpath=None, image_shape=(300, 300), \
              is_training=None, use_batchnorm=None, activation=tf.nn.relu, \
              num_classes=0, normalization=[], atrous=False, rate=1):
    """
       1. input RGB images and labels
       2. edit images like [-1, image_shape[0], image_shape[1], 3]
       3. Create Annotate Layer?
       4. input x into Vgg16 architecture(pretrained)
       5.
    """
    images = tf.placeholder(tf.float32, [None, image_shape[0], image_shape[1], 3])
    vgg = Vgg(vgg16_npy_path=vggpath)
    vgg.build_model(images)

    with tf.variable_scope("extended_model") as scope:
        phase_train = tf.placeholder(tf.bool, name="phase_traing") if is_training else None
        batchnorm = tf.placeholder(tf.bool, name="batchnorm") if use_batchnorm else None
        extended_model = ExtendedLayer()
        extended_model.build_model(vgg.conv5_3, use_batchnorm=batchnorm, atrous=atrous, rate=rate, \
                                   is_training=phase_train, activation=activation, lr_mult=1)

    # with tf.variable_scope("multibox_layer"):
    #     from_layers = [vgg.conv4_3, extended_model.conv_7, extended_model.conv_8_2,
    #                    extended_model.conv_9_2, extended_model.conv_10_2, extended_model.conv_11_2]
    #     multibox_layer = MultiboxLayer()
    #     multibox_layer.build_model(from_layers, num_classes=0, normalization=normalization)
    #
    initialized_var = tf.get_collection(tf.GraphKeys.GLOBAL_VARIABLES, scope="extended_model")
    sess.run(tf.variables_initializer(initialized_var))

    return extended_model

class MultiboxLayer(object):
    def __init__(self):
        pass

    def l2_normalization(self, input_layer, scale=20):
        return tf.nn.l2_normalize(input_layer, dim) * scale

    def createMultiBoxHead(self, from_layers, num_classes=0, normalizations=[], \
                           use_batchnorm=False, is_training=None, activation=None, \
                           kernel_size=3, prior_boxes=[]):
        """
           # Args:
               from_layers(list)   : list of input layers
               num_classes(int)    : num of label's classes that this architecture detects
               normalizations(list): list of scale for normalizations
                                     if value <= 0, not apply normalization to the specified layer
        """
        assert num_classes > 0, "num of label's class  must be positive number"
        if normalizations:
            assert len(from_layers) == len(normalizations), "from_layers and normalizations should have same length"

        num_list = len(from_layers)
        for index, layer, norm in zip(range(num_list), from_layers, normalizations):
            input_layer = layer
            with tf.variable_scope("layer" + str(index+1)):
                if norm > 0:
                    scale = tf.get_variable("scale", trainable=True, initializer=tf.constant(norm))#initialize = norm
                    input_layer = self.l2_normalization(input_layer, scale)

                # create location prediction layer
                loc_output_dim = 4 * prior_num
                location_layer = convBNLayer(input_layer, use_batchnorm, is_training, input_layer.get_shape()[0], loc_output_dim, kernel_size, 1, name="loc_layer", activation=activation)

                # create confidence prediction layer
                conf_output_dim = num_classes * prior_num
                confidence_layer = convBNLayer(input_layer, use_batchnorm, is_training, input_layer.get_shape()[0], conf_output_dim, kernel_size, 1, name="conf_layer", activation=activation)

                # Flatten each output

                # append result of each results

        return None

if __name__ == '__main__':
    import sys
    import matplotlib.pyplot as plt
    from PIL import Image as im
    sys.path.append('/home/katou01/code/grid/DataAugmentation')
    from resize import resize

    image = im.open("./test_images/test1.jpg")
    image = np.array(image, dtype=np.float32)
    new_image = image[np.newaxis, :]
    batch_image = np.vstack((new_image, new_image))
    batch_image = resize(batch_image, size=(300, 300))

    with tf.Session() as sess:
        model = ssd_model(sess, batch_image, activation=None, atrous=True, rate=1)
        print(vars(model))
        # tf.summary.scalar('model', model)
