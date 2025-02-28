import base64
import logging
import os
import torch
import transformers

from flask import Flask, request, jsonify
from flask_cors import CORS
from io import BytesIO
from PIL import Image
from qdrant_client import QdrantClient

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

INDEX_DIR = r"C:\Users\Photogauge\Desktop\Projects\CBIR\cbir_demo\demo\index"  # Directory where index images are stored
print(os.listdir(INDEX_DIR))

# Initialize Qdrant client
client = QdrantClient(
    url="https://9bb5d541-5abf-495a-b901-f76eaed98a9a.europe-west3-0.gcp.cloud.qdrant.io",
    api_key="6ldGC2tDMgl9JwVwwpiDcuuJsfIoWvDL60TDvSR4bXSpah4JqA1PkQ",
)

def img64_to_pil(img64):
    """Convert base64 image to PIL image."""
    try:
        if "," in img64:
            img64 = img64.split(",")[1]  # Remove header if present

        image_data = base64.b64decode(img64)
        image = Image.open(BytesIO(image_data))
        return image
    except Exception as e:
        logging.error(f"Error processing image: {e}")
        return None

def get_image_embedding(image, device):
    """Generate image embeddings using DINOv2."""
    embedding_processor = transformers.AutoImageProcessor.from_pretrained('facebook/dinov2-base')
    embedding_model = transformers.Dinov2Model.from_pretrained('facebook/dinov2-base', attn_implementation="eager").to(device)
    
    with torch.no_grad():
        inputs = embedding_processor(images=image, return_tensors="pt").to(device)
        outputs = embedding_model(**inputs, output_hidden_states=True)
        embedding = outputs.last_hidden_state.mean(dim=1).squeeze().cpu().numpy()
        
    return embedding

def retrieve_similar_images(query_image, device, collection_name='demo', top_k=10):
    """Search for similar images in Qdrant."""
    query_embedding = get_image_embedding(query_image, device)
    return client.search(
        collection_name=collection_name,
        query_vector=query_embedding,
        limit=top_k
    )

def get_index_image_base64(image_id):
    """Retrieve index image by ID and encode it as Base64."""
    image_path = INDEX_DIR + '/' + f"index_{image_id}.jpg"
    
    if not os.path.exists(image_path):
        logging.error(f"Image {image_path} not found.")
        return None

    try:
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode("utf-8")
    except Exception as e:
        logging.error(f"Error reading image {image_id}: {e}")
        return None

@app.route('/upload', methods=['POST'])
def upload_image():
    """Handle image upload, find similar images, and return a matching image if found."""
    try:
        data = request.json
        image_b64 = data.get("image")
        image_id = data.get("image_id")
        image_id = image_id.split("_")[-1].split(".")[0]  # Extract ID from filename
        # print(f"Uploaded Image ID: {image_id}")
        
        if not image_b64:
            return jsonify({"error": "No image provided"}), 400
        
        image = img64_to_pil(image_b64)
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        results = retrieve_similar_images(image, device)
        images = [point.payload['image_path'] for point in results]

        # image_path = images[0]
        # index_id = image_path.split('_')[-1].split('.')[0]
        # print(f"Matching Index ID: {index_id}")
        # base64_img = get_index_image_base64(index_id)
        # if base64_img:
        #     return jsonify({"results": f"index_{image_id}.jpg", "image_base64": base64_img})
        # else:
        #     return jsonify({"error": "Matched image not found"}), 404

        
        for image_path in images:
            index_id = image_path.split('_')[-1].split('.')[0]
            if index_id == image_id:
                print(f"Matching Index ID: {index_id}")
                base64_img = get_index_image_base64(index_id)
                if base64_img:
                    return jsonify({"results": f"index_{image_id}.jpg", "image_base64": base64_img})
                else:
                    return jsonify({"error": "Matched image not found"}), 404

        return jsonify({"results": "No match found"}), 200

    except Exception as e:
        logging.error(f"Error processing image: {e}")
        return jsonify({"error": "Internal server error"}), 500

if __name__ == '__main__':
    app.run(debug=True)
