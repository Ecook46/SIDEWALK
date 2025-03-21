import cv2
import matplotlib.pyplot as plt
from ultralytics import YOLO

# Load the model
model = YOLO("code/Model Training/trainingData/results/weights/last.pt")

# Load the image
image_path = 'code/Processing/Videos/testPhoto/test7.jpg'
image = cv2.imread(image_path)

# Convert the image to rgb to plot with .plt
image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

# Perform inference on the image
results = model(image_rgb)

# Plot the image with bounding boxes
plt.imshow(results[0].plot())
plt.axis('off')
plt.show()
