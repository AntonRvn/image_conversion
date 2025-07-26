from app.cartoongan.cartoongan import CartoonGAN
import os

# Путь к весам модели (замените на ваш)
MODEL_PATH = os.path.join(
    os.path.dirname(__file__),
    'cartoongan/pretrained_weights/generator_hayao.h5'  # Пример для аниме-стиля
)

# Глобальный объект модели (загружается 1 раз)
cartoongan = None

@app.on_after_configure.connect
def setup_model(**kwargs):
    global cartoongan
    cartoongan = CartoonGAN(MODEL_PATH)

@app.task(bind=True)
def process_image(self, image_id):
    with app.app_context():
        from app.models import Image, db
        try:
            img = Image.query.get(image_id)
            if not img:
                raise ValueError("Image not found")

            # Пути к файлам
            input_path = os.path.join(app.root_path, img.original_url)
            output_dir = os.path.join(app.root_path, 'static', 'cartoons')
            os.makedirs(output_dir, exist_ok=True)
            output_path = os.path.join(output_dir, img.filename)

            # Обработка изображения
            success = cartoongan.transform(input_path, output_path)
            if success:
                img.cartoon_url = f'static/cartoons/{img.filename}'
                db.session.commit()
                return {"status": "success"}
            else:
                raise RuntimeError("CartoonGAN failed")

        except Exception as e:
            self.retry(exc=e, countdown=60)