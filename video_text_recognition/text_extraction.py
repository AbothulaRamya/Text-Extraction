import cv2
import pytesseract

def extract_text_from_video(video_path, output_dir):
    # Initialize the video capture object
    cap = cv2.VideoCapture(video_path)
    frame_count = 0
    extracted_text = ""

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        frame_count += 1
        
        # Assuming you want to process every nth frame
        if frame_count % 30 == 0:  # Adjust this value based on your requirement
            # Convert the frame to grayscale (for better OCR performance)
            gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # Use pytesseract to extract text from the frame
            text = pytesseract.image_to_string(gray_frame)
            extracted_text += text + "\n"
    
    cap.release()

    return extracted_text