import easyocr
import cv2
import numpy as np

reader = easyocr.Reader(['en'])
MIN_CONFIDENCE = 0.4


def preprocess(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    gray = cv2.bilateralFilter(gray, 11, 17, 17)
    edged = cv2.Canny(gray, 30, 200)

    return gray, edged


def detect_plate_region(image):
    gray, edged = preprocess(image)

    contours, _ = cv2.findContours(
        edged,
        cv2.RETR_TREE,
        cv2.CHAIN_APPROX_SIMPLE
    )

    contours = sorted(contours, key=cv2.contourArea, reverse=True)[:10]

    for contour in contours:
        approx = cv2.approxPolyDP(
            contour,
            0.018 * cv2.arcLength(contour, True),
            True
        )

        if len(approx) == 4:
            x, y, w, h = cv2.boundingRect(approx)

            ratio = w / float(h)

            # placas geralmente têm formato retangular
            if 2 < ratio < 6:
                plate = image[y:y + h, x:x + w]
                return plate, (x, y, w, h)

    return None, None


def read_plate(image):
    plate_img, coords = detect_plate_region(image)

    if plate_img is None:
        print("Placa não encontrada")
        return None, image

    # melhorar a imagem da placa
    gray = cv2.cvtColor(plate_img, cv2.COLOR_BGR2GRAY)
    gray = cv2.resize(gray, None, fx=2, fy=2)
    gray = cv2.threshold(gray, 0, 255,
                         cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]

    results = reader.readtext(
        gray,
        allowlist='ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
    )

    best_text = None
    best_prob = 0

    for (_, text, prob) in results:
        text = text.replace(" ", "").upper()

        print("OCR:", text, prob)

        if prob > best_prob and 6 <= len(text) <= 7:
            best_text = text
            best_prob = prob

    if best_text:
        x, y, w, h = coords

        cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 3)

        cv2.putText(
            image,
            best_text,
            (x, y - 10),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (0, 255, 0),
            2
        )

        print("PLACA FINAL:", best_text)

        return best_text, image

    return None, image