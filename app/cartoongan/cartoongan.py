import tensorflow as tf
import numpy as np
from PIL import Image

class CartoonGAN:
    def __init__(self, model_path):
        """Инициализация с загрузкой модели"""
        self.model = tf.keras.models.load_model(model_path)

    def preprocess(self, image):
        """Подготовка изображения для модели"""
        image = image.resize((256, 256))
        image = np.array(image) / 127.5 - 1.0
        return tf.expand_dims(image, axis=0)

    def postprocess(self, tensor):
        """Преобразование выхода модели в изображение"""
        tensor = (tensor + 1.0) * 127.5
        return Image.fromarray(tensor.numpy().astype(np.uint8)[0])

    def transform(self, input_path, output_path):
        """Основной метод: загружает, обрабатывает, сохраняет"""
        try:
            img = Image.open(input_path).convert('RGB')
            input_tensor = self.preprocess(img)
            output_tensor = self.model(input_tensor)
            result = self.postprocess(output_tensor)
            result.save(output_path)
            return True
        except Exception as e:
            print(f"Error: {e}")
            return False