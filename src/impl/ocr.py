"""
A module for OCR calls.
"""

import cv2
import pytesseract
import numpy

def basic_preproc(image):
    image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY);
    image = cv2.GaussianBlur(image, (3,3), 0);
    image = cv2.threshold(image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1];
    return image;

# skew correction
# Unused
# def deskew(image):
#     coords = np.column_stack(np.where(image > 0))
#     angle = cv2.minAreaRect(coords)[-1]
#      if angle < -45:
#         angle = -(90 + angle)
#     else:
#         angle = -angle
#     (h, w) = image.shape[:2]
#     center = (w // 2, h // 2)
#     M = cv2.getRotationMatrix2D(center, angle, 1.0)
#     rotated = cv2.warpAffine(image, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
#     return rotated

def ocr_string(image):
    opencvImage = cv2.cvtColor(numpy.array(image), cv2.COLOR_RGB2BGR);
    opencvImage = basic_preproc(opencvImage);
    return pytesseract.image_to_string(opencvImage, lang='eng', config='--psm 6');