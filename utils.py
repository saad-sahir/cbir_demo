import logging
from LightGlue.lightglue import SuperPoint
import os

# Initialize SuperPoint extractor
extractor = SuperPoint(max_num_keypoints=2048).eval().to("cpu")

def extract_superpoint_features(image):
    """
    Extract SuperPoint keypoints and descriptors from an image tensor.

    Args:
        image (torch.Tensor): The input image tensor.

    Returns:
        dict: A dictionary containing keypoints and descriptors.
    """
    try:
        logging.info("Extracting SuperPoint features.")
        features = extractor.extract(image)
        keypoints, descriptors = features["keypoints"], features["descriptors"]
        logging.info("Feature extraction successful.")
        return {"keypoints": keypoints, "descriptors": descriptors}
    except Exception as e:
        logging.error(f"Error during feature extraction: {str(e)}", exc_info=True)
        raise