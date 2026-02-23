"""
Orchestrates camera init, hand tracker, and gRPC client with pure relative positioning.
"""
import cv2
import logging
from core.tracker import HandTracker
from network.grpc_client import GazeStreamer

SENSITIVITY_X = 2.5 
SENSITIVITY_Y = 2.5 
START_X, START_Y = 0.5, 0.5

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

def main():
    logging.info("Initializing components...")
    tracker = HandTracker()
    streamer = GazeStreamer(target_address='localhost:50051')
    streamer.start()

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        logging.error("Could not open the webcam.")
        return

    logging.info("Sensor running. Press 'q' to quit.")

    cursor_x, cursor_y = START_X, START_Y
    last_hand_x, last_hand_y = 0.0, 0.0
    was_pinched = False

    while cap.isOpened():
        success, image = cap.read()
        if not success:
            continue

        image = cv2.flip(image, 1)
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        hand_data = tracker.process_frame(image_rgb)

        if hand_data:
            current_pinch = hand_data['is_pinched']
            raw_x, raw_y = hand_data['x'], hand_data['y']

            if current_pinch:
                if not was_pinched:
                    # Anchor the starting position using raw data
                    last_hand_x, last_hand_y = raw_x, raw_y
                else:
                    # Apply instantaneous delta to the virtual cursor
                    dx, dy = raw_x - last_hand_x, raw_y - last_hand_y
                    
                    cursor_x = max(0.0, min(1.0, cursor_x + (dx * SENSITIVITY_X)))
                    cursor_y = max(0.0, min(1.0, cursor_y + (dy * SENSITIVITY_Y)))

                    streamer.send_point(x=cursor_x, y=cursor_y, confidence=1.0)
                    
                    # Reset anchor for the next frame
                    last_hand_x, last_hand_y = raw_x, raw_y

            was_pinched = current_pinch

            # --- VISUAL DEBUGGING ---
            color = (0, 255, 0) if current_pinch else (0, 0, 255)
            h, w, _ = image.shape
            tx, ty = hand_data['thumb_px']
            ix, iy = hand_data['index_px']
            
            cv2.circle(image, (int(tx * w), int(ty * h)), 6, color, -1)
            cv2.circle(image, (int(ix * w), int(iy * h)), 6, color, -1)
            cv2.line(image, (int(tx * w), int(ty * h)), (int(ix * w), int(iy * h)), color, 2)

        cv2.imshow('Hand Tracker Sensor', image)

        if cv2.waitKey(5) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
    streamer.stop()

if __name__ == "__main__":
    main()