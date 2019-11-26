from segmentation_models import Unet
import numpy as np
import config

class Model:
    def __init__(self):
        self.data_path = config.data_path
        self.model = self.resnet()

    def resnet(self):
        """
        Load model and weights

        :return: neural network model
        """
        #define model
        # model = Unet(backbone_name='resnet34', input_shape=(None, None, 3), encoder_weights=None, classes=1, encoder_freeze=False)
        # model.load_weights(self.data_path + '/weights/true_weights.hdf5')
        # model.compile('Adam', 'dice_loss', metrics=['iou_score'])

        model = Unet(backbone_name='resnet18', input_shape=(None, None, 3), decoder_filters=(64, 32, 32, 16, 4),
                     encoder_weights='imagenet', classes=1, encoder_freeze=True,)
        model.load_weights(self.data_path + '/weights/new.hdf5')
        model.compile('Adam', 'bce_jaccard_loss', metrics=['iou_score'])
        return model

    def predict(self, image):
        """
        Predict the image

        :param image: frame from camera in RGB
        :return: binary mask of the object
        """

        # predict image from the camera
        mask = self.model.predict(np.array([image]))[0]

        # if pixel >= 0.5, make it 255,else 0
        mask[mask >= 0.5] = 255
        mask[mask < 0.5] = 0

        return np.uint8(mask)