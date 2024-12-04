import braille_controller.brailleOCR as brailleOCR

image_path = "image_bank/image_01.jpg"

if __name__ == "__main__":
    image_path = "image_bank/image_01.jpg"
    text = brailleOCR.extract_text_from_image(image_path=image_path)
    print(text)