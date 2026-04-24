import os
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
import io
import base64
import matplotlib
matplotlib.use('Agg')

def process_images(img1_path, img2_path, direction):
    """
    Склейка двух изображений и создание графиков распределения цветов.
    """
    img1 = Image.open(img1_path).convert("RGB")
    img2 = Image.open(img2_path).convert("RGB")
    img2_resized = None

    if direction == 'horizontal':
        h1 = img1.height
        w1 = img1.width
        aspect_ratio = img2.width / img2.height
        new_w2 = int(h1 * aspect_ratio)
        img2_resized = img2.resize((new_w2, h1))
        
        total_width = w1 + new_w2
        result_img = Image.new('RGB', (total_width, h1))
        result_img.paste(img1, (0, 0))
        result_img.paste(img2_resized, (w1, 0))
        
    else: # vertical
        w1 = img1.width
        h1 = img1.height
        aspect_ratio = img2.height / img2.width
        new_h2 = int(w1 * aspect_ratio)
        img2_resized = img2.resize((w1, new_h2))
        
        total_height = h1 + new_h2
        result_img = Image.new('RGB', (w1, total_height))
        result_img.paste(img1, (0, 0))
        result_img.paste(img2_resized, (0, h1))

    result_filename = "result_merged.jpg"
    save_path = os.path.join("static", "uploads", result_filename)

    os.makedirs(os.path.dirname(save_path), exist_ok=True)

    result_img.save(save_path)

    img2_for_graph = img2_resized

    if img2_for_graph is None:
        img2_for_graph = img2

    graph_base64 = generate_histograms(img1, img2_for_graph, result_img)

    return {
        "result_filename": result_filename, 
        "graph_base64": graph_base64
    }

def generate_histograms(img1, img2, result_img):
    """
    Создает фигуру с тремя наборами гистограмм и возвращает base64.
    """
    fig, axes = plt.subplots(1, 3, figsize=(18, 5))
    titles = ["Image 1", "Image 2", "Merged Result"]
    images = [img1, img2, result_img]

    for ax, img, title in zip(axes, images, titles):
        np_img = np.array(img)
        
        colors = ('red', 'green', 'blue')
        for i, color in enumerate(colors):
            hist = np.histogram(np_img[:, :, i], bins=256, range=(0, 256))[0]
            ax.plot(hist, color=color, label=color.capitalize())
        
        ax.set_title(title)
        ax.legend(loc='upper right')
        ax.set_xlim([0, 256])

    plt.tight_layout()

    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    plt.close(fig)

    image_base64 = base64.b64encode(buf.getvalue()).decode('utf-8')
    return image_base64