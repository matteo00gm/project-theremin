"""
Orchestrates camera init, eye tracker, and gRPC client.
"""
import cv2
from core.tracker import GazeTracker
from network.grpc_client import GazeStreamer

def main():
    print("Initializing components...")
    tracker = GazeTracker()
    streamer = GazeStreamer(target_address='localhost:50051')
    
    # Start the background gRPC network thread
    streamer.start()

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("CRITICAL: Could not open the webcam.")
        return

    print("Sensor running. Press 'q' to quit.")

    while cap.isOpened():
        success, image = cap.read()
        if not success:
            continue

        # 1. Track Eyes
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        gaze_data = tracker.process_frame(image_rgb)

        if gaze_data:
            # For mouse control, we'll just stream the Left eye coordinates
            raw_lx, ly = gaze_data['left']
            
            # camera mirror effect (invert x axys)
            lx = 1.0 - raw_lx

            # 2. Stream data
            streamer.send_point(x=lx, y=ly, confidence=gaze_data['confidence'])

            # 3. Draw UI (for local debugging)
            h, w, _ = image.shape
            cv2.circle(image, (int(raw_lx * w), int(ly * h)), 4, (0, 255, 0), -1)
            cv2.circle(image, (int(gaze_data['right'][0] * w), int(gaze_data['right'][1] * h)), 4, (0, 255, 0), -1)

        cv2.imshow('Eye Tracker Sensor', cv2.flip(image, 1))

        if cv2.waitKey(5) & 0xFF == ord('q'):
            break

    # Cleanup
    cap.release()
    cv2.destroyAllWindows()
    streamer.stop()

if __name__ == "__main__":
    main()