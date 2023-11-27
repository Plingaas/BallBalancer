import cv2
import numpy as np

def detect_orange_circle_video():
    # Open a connection to the camera (you can change the argument to 0 if you have only one camera)
    cap = cv2.VideoCapture(0)

    # Check if the camera is opened successfully
    if not cap.isOpened():
        print("Error: Could not open camera.")
        return

    while True:
        # Read a frame from the camera
        ret, frame = cap.read()

        # Check if the frame is read successfully
        if not ret:
            print("Error: Could not read frame.")
            break

        # Convert the frame to HSV
        hsv_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        # Define a lower and upper range for orange colors
        lower_orange = np.array([5, 50, 50], dtype=np.uint8)
        upper_orange = np.array([15, 255, 255], dtype=np.uint8)

        # Create a mask for the orange color range
        mask_orange = cv2.inRange(hsv_frame, lower_orange, upper_orange)

        # Find contours in the mask
        contours, _ = cv2.findContours(mask_orange, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # Iterate through the contours and find circles
        for contour in contours:
            area = cv2.contourArea(contour)
            if area > 100:  # Adjust this threshold based on your specific case
                # Fit a circle to the contour
                (x, y), radius = cv2.minEnclosingCircle(contour)
                center = (int(x), int(y))
                radius = int(radius)

                # Draw the circle and its center
                cv2.circle(frame, center, radius, (0, 255, 0), 2)
                cv2.circle(frame, center, 2, (0, 255, 0), 3)

                # Print the x, y position
                print(f"Orange circle detected at position (x, y): ({int(x)}, {int(y)})")

        # Display the frame with detected circles
        cv2.imshow("Orange Circle Detection", frame)

        # Break the loop if 'q' key is pressed
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Release the camera and close the window
    cap.release()
    cv2.destroyAllWindows()

# Run the function
detect_orange_circle_video()
