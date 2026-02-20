from flask import Flask, render_template, request
import cv2
import os
from ocr import read_plate
from database import insert_plate

app = Flask(__name__)

UPLOAD_FOLDER = "static/uploads"
RESULT_FOLDER = "static/images"

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["RESULT_FOLDER"] = RESULT_FOLDER

# cria as pastas se não existirem
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(RESULT_FOLDER, exist_ok=True)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/upload", methods=["POST"])
def upload():
    if "image" not in request.files:
        return "Nenhum arquivo enviado"

    file = request.files["image"]

    if file.filename == "":
        return "Arquivo inválido"

    # salvar upload original
    upload_path = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
    file.save(upload_path)

    print("Imagem recebida:", upload_path)

    image = cv2.imread(upload_path)

    if image is None:
        return "Erro ao abrir a imagem com OpenCV"

    # rodar OCR
    plate, image_with_box = read_plate(image)

    print("Placa detectada:", plate)

    # salvar imagem com detecção
    result_path = os.path.join(app.config["RESULT_FOLDER"], file.filename)
    cv2.imwrite(result_path, image_with_box)

    print("Imagem salva em:", result_path)

    # salvar no banco se encontrou placa
    if plate:
        insert_plate(plate)

    return render_template(
        "index.html",
        plate=plate,
        image_url="/" + result_path
    )


if __name__ == "__main__":
    app.run(debug=True)