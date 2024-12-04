"""
OCR Module for Braille Controller
Handles text extraction from images using EasyOCR
"""
import logging
import easyocr
import numpy as np
from PIL import Image
from typing import Optional, List, Tuple

# Initialize the reader at module level with specific parameters
try:
    reader = easyocr.Reader(
        ['en'],
        gpu=False,
        model_storage_directory=None,
        download_enabled=True,
        recog_network='english_g2'
    )
    logging.info("EasyOCR initialized successfully")
except Exception as e:
    reader = None
    logging.error(f"Failed to initialize EasyOCR: {e}")

def preprocess_image(image_path: str) -> Image.Image:
    """
    Preprocess image for better OCR results.
    """
    try:
        # Open image and convert to grayscale
        img = Image.open(image_path).convert('L')
        
        # Convert to numpy array for processing
        img_array = np.array(img)
        
        # Basic contrast enhancement
        p2 = np.percentile(img_array, 2)
        p98 = np.percentile(img_array, 98)
        img_array = np.clip(img_array, p2, p98)
        img_array = ((img_array - p2) / (p98 - p2) * 255).astype(np.uint8)
        
        # Convert back to PIL Image
        enhanced_img = Image.fromarray(img_array)
        logging.debug("Image preprocessing completed")
        return enhanced_img
        
    except Exception as e:
        logging.error(f"Error during image preprocessing: {e}")
        raise

def extract_text_from_image(image_path: str, confidence_threshold: float = 0.3) -> str:
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
        
        # Preprocess image
        try:
            preprocessed_image = preprocess_image(image_path)
            logging.debug("Image preprocessing successful")
        except Exception as e:
            logging.error(f"Image preprocessing failed: {e}")
            # Fall back to original image if preprocessing fails
            preprocessed_image = image_path
        
        # Run OCR with multiple detection parameters
        result = reader.readtext(
            preprocessed_image,
            paragraph=True,  # Group text into paragraphs
            contrast_ths=0.1,  # Lower contrast threshold
            adjust_contrast=0.5,  # Adjust image contrast
            width_ths=0.7,  # Width threshold for text boxes
            height_ths=0.7,  # Height threshold for text boxes
        )
        
        extracted_text = []
        for bbox, text, prob in result:
            logging.debug(f"Found text: '{text}' with confidence {prob:.3f}")
            if prob > confidence_threshold:
                cleaned_text = text.strip()
                if cleaned_text:
                    extracted_text.append(cleaned_text)
                    logging.debug(f"Accepted text: '{cleaned_text}' (confidence: {prob:.3f})")
            else:
                logging.debug(f"Rejected text: '{text}' due to low confidence {prob:.3f}")
        
        if extracted_text:
            final_text = ' '.join(extracted_text)
            # Clean up the text
            final_text = ' '.join(final_text.split())  # Remove extra whitespace
            final_text_ascii = final_text.encode('ascii', 'ignore').decode('ascii')
            logging.info(f"Successfully extracted text: {final_text_ascii}")
            return final_text_ascii
        else:
            logging.warning("No text found with sufficient confidence")
            return ""
            
    except Exception as e:
        error_msg = f"Error processing image: {str(e)}"
        logging.error(error_msg)
        raise RuntimeError(error_msg)

def is_available() -> bool:
    """Check if OCR functionality is available."""
    return reader is not None