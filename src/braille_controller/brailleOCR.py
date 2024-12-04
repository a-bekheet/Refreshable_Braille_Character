"""
OCR Module for Braille Controller
Handles text extraction from images using EasyOCR
"""

import logging
import easyocr
from typing import Optional

# Initialize the reader at module level
try:
    reader = easyocr.Reader(['en'])
    logging.info("EasyOCR initialized successfully")
except Exception as e:
    reader = None
    logging.error(f"Failed to initialize EasyOCR: {e}")

def extract_text_from_image(image_path: str, confidence_threshold: float = 0.5) -> str:
    """
    Extract text from an image using EasyOCR.
    
    Args:
        image_path: Path to the image file
        confidence_threshold: Minimum confidence score for text detection (0-1)
        
    Returns:
        str: Extracted text or error message
    """
    try:
        if reader is None:
            raise RuntimeError("EasyOCR not properly initialized")

        logging.debug(f"Processing image: {image_path}")
        result = reader.readtext(image_path)
        
        extracted_text = []
        for bbox, text, prob in result:
            if prob > confidence_threshold:
                extracted_text.append(text)
                logging.debug(f"Detected text '{text}' with confidence {prob:.2f}")
            else:
                logging.debug(f"Skipped text '{text}' due to low confidence {prob:.2f}")

        if extracted_text:
            final_text = ' '.join(extracted_text)
            logging.info(f"Successfully extracted text: {final_text}")
            return final_text
        else:
            logging.warning("No text found with sufficient confidence")
            return "No text found with sufficient confidence."

    except Exception as e:
        error_msg = f"Error processing image: {str(e)}"
        logging.error(error_msg)
        raise RuntimeError(error_msg)

def is_available() -> bool:
    """Check if OCR functionality is available."""
    return reader is not None