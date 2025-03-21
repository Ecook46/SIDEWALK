import cv2
from ultralytics import YOLO

# Load a pretrained YOLO model
model = YOLO("code/Model Training/model/best_yolo_model.pt")

# set the paths
source = "code/Processing/Videos/Raw_Video/test9.mp4"
output_path = "code/Processing/Videos/Processed_Video/outTest10.mp4"

# Open the video file using OpenCV
cap = cv2.VideoCapture(source)
fps = cap.get(cv2.CAP_PROP_FPS)
width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

# Define the codec and create a VideoWriter object to save the output video
fourcc = cv2.VideoWriter_fourcc(*'mp4v') 
out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

# Run inference on each frame of the video
while True:
    ret, frame = cap.read()
    if not ret:
        break
    
    # Perform inference on the frame
    results = model(frame)
    boxes = results[0].boxes
    scores = boxes.conf  # confidence scores
    labels = boxes.cls  # class labels
    filtered_boxes = []
    filtered_scores = []
    filtered_labels = []

    # Filter out detections below the 40% confidence threshold
    for i, score in enumerate(scores):
        if score > 0.4:
            filtered_boxes.append(boxes.xyxy[i].cpu().numpy())  # bounding box coordinates
            filtered_scores.append(score.item())  # confidence score
            filtered_labels.append(labels[i].item())  # label

    # Annotate the frame with filtered bounding boxes
    annotated_frame = frame.copy()
    for box, score, label in zip(filtered_boxes, filtered_scores, filtered_labels):
        x1, y1, x2, y2 = box
        # Draw bounding box
        cv2.rectangle(annotated_frame, (int(x1), int(y1)), (int(x2), int(y2)), (255, 0, 0), 2)
        cv2.putText(annotated_frame, f"{model.names[label]} {score:.2f}", 
                    (int(x1), int(y1) - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 0, 0), 2)

    # Write the frame to the output video
    out.write(annotated_frame)

# Release the video capture and writer objects
cap.release()
out.release()