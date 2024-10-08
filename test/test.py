import os
from ultralytics import YOLO

# Load the trained model
model = YOLO('runs/classify/train/weights/best.pt')  # or 'last.pt' if you want the latest checkpoint

# Get a list of test images
plan_test_images = ["datasets/cian-911/test/plan/" + image for image in os.listdir('datasets/cian-911/test/plan')]
no_plan_test_images = ["datasets/cian-911/test/no_plan/" + image for image in os.listdir('datasets/cian-911/test/no_plan')]

# Function to perform inference and print results
def test_images(image_list, label):
    print(f"\nTesting images with {label}:")
    for image_path in image_list:
        try:
            results = model.predict(source=image_path, save=False, save_txt=False)
            for result in results:
                probs = result.probs.data  # Access the probabilities tensor
                plan_prob = probs[1].item()
                no_plan_prob = probs[0].item()
                prediction = 'Plan' if plan_prob > no_plan_prob else 'No Plan'
                print(f"Image: {image_path} | Prediction: {prediction} | Plan Probability: {plan_prob:.4f} | No Plan Probability: {no_plan_prob:.4f}")
        except Exception as e:
            print(f"Error processing image: {image_path} - {e}")

# Test images with plans
test_images(plan_test_images, "plans")

# Test images with no plans
test_images(no_plan_test_images, "no plans")