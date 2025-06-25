import torch
import torchvision.transforms as transforms
from PIL import Image
import torchvision.models as models
import os
import numpy as np
import cv2

# Check if GPU is available
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# Load EfficientNet-B0 model
def load_model():

    weights=models.EfficientNet_B0_Weights.DEFAULT
    model = models.efficientnet_b0(weights=weights).to(device)
    model.classifier = torch.nn.Sequential(
        torch.nn.Dropout(p=0.4, inplace=True),
        torch.nn.Linear(in_features=1280, out_features=1, bias=True)
    ).to(device)

    # Load trained weights
    model_path = os.path.join(os.path.dirname(__file__), "Model/best_model.pth")
    model.load_state_dict(torch.load(model_path, map_location=device))

    # Move model to GPU (if available)
    model.to(device)
    model.eval()
    return model

# Load model once
model = load_model()

# Define image transformation
transform = transforms.Compose([
    transforms.Resize((224,224)),
    transforms.ToTensor()
])

class GradCAM:
    def __init__(self, model, target_layer):
        self.model = model
        self.target_layer = target_layer
        self.gradients = None
        self.activations = None
        
        # Register hooks
        self.target_layer.register_forward_hook(self.forward_hook)
        self.target_layer.register_backward_hook(self.backward_hook)

    def forward_hook(self, module, input, output):
        self.activations = output  # Save activations

    def backward_hook(self, module, grad_input, grad_output):
        self.gradients = grad_output[0]  # Save gradients

    def generate_cam(self, input_image, class_idx=None):
        self.model.zero_grad()
        output = self.model(input_image.unsqueeze(0))  # Forward pass
        
        if class_idx is None:
            class_idx = output.argmax().item()  # Get predicted class
        
        output[:, 0].backward()  # Compute gradients for the only output node
        
        # Compute Grad-CAM heatmap
        alpha = self.gradients.mean(dim=[2, 3], keepdim=True)  # Global Average Pooling
        cam = (alpha * self.activations).sum(dim=1, keepdim=True)  # Weight activations
        
        cam = torch.relu(cam)  # ReLU to remove negative values
        cam = cam.squeeze().detach().cpu().numpy()  # Convert to NumPy
        cam = cv2.resize(cam, (224, 224))  # Resize to match input image
        
        return cam


# Prediction function with Grad-CAM
def predict_image(image):

    grad_cam = GradCAM(model,model.features[-1])

    image = transform(image).unsqueeze(0).to(device)
    
    model.eval()
    with torch.no_grad():
        prediction = model(image)
        confidence = torch.sigmoid(prediction).item()
        label = "Fake" if confidence < 0.5 else "Real"
    
    # Generate Grad-CAM
    cam = grad_cam.generate_cam(image.squeeze(0))

    # Convert Grad-CAM heatmap to an image
    heatmap = cv2.applyColorMap(np.uint8(255 * cam), cv2.COLORMAP_JET)
    heatmap = cv2.cvtColor(heatmap, cv2.COLOR_BGR2RGB)

    # Overlay heatmap on input image
    input_image_resized = transforms.ToPILImage()(image.squeeze(0).cpu())
    input_image_resized = input_image_resized.resize((224, 224))  # Resize original image
    input_image_np = np.array(input_image_resized)  # Convert to numpy array
    overlayed_image = cv2.addWeighted(input_image_np, 0.6, heatmap, 0.4, 0)  # Blend

    
    return label, round(confidence, 2),Image.fromarray(overlayed_image)

