import pickle
from config import data_path

class K_Means:
    def __init__(self):
        self.path = data_path
        self.loaded_model = self.load()

    def load(self):
        loaded_model = pickle.load(open(self.path + 'k-means/k_means_colors.sav', 'rb'))
        return loaded_model

    def predict(self, mean):
        """
        Load k_means weights and predict object color

        :param mean: mean color of the object with parameters R,G,B
        :return: color in number format
        """
        result = self.loaded_model.predict(mean)

        return str(result[0])