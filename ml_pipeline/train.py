from ultralytics import YOLO
import os

def main():
    # Load a pre-trained YOLOv8 nano model for speed
    model = YOLO('yolov8n.pt')

    # Ensure the path to data.yaml is correct based on your folder structure
    # Update this absolute path if needed depending on where Roboflow extracted it
    yaml_path = os.path.abspath("dataset/data.yaml")

    print(f"Starting training using dataset config: {yaml_path}")

    # Fine-tune the model
    # Adjust epochs based on how much time you have. 20-30 is a good quick test.
    results = model.train(
        data=yaml_path,
        epochs=30,      
        imgsz=640,
        batch=16,
        project="runs",
        name="gauge_detector"
    )

    print("Training complete! Best weights saved in runs/gauge_detector/weights/best.pt")

if __name__ == '__main__':
    main()