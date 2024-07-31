import cv2
from datetime import datetime
import time
import os
from cv2 import VideoCapture, imshow, destroyAllWindows, imwrite, waitKey, createBackgroundSubtractorMOG2, countNonZero
from utils import log, Configuration, force_stop_camera



class Camera:
    def __init__(self, config_data):
        # savepath, framerate=8, width=512, height=512, camera_index=0 , debug=False, logpath='./log'
        self.camera_index = config_data.camera_index
        self.debug = config_data.debug
        self.log = log(config_data.logpath)
        self.framerate = config_data.framerate

        #motion detection initilzation
        self.bg_update_interval = 30  # in seconds, adjust as needed
        self.last_bg_update = time.time()
        self.bg_model_initialized = False
        self.fgbg = createBackgroundSubtractorMOG2(detectShadows=False)

        force_stop_camera() #quit all camera-process of open
        self.cam = VideoCapture(self.camera_index)
        if not self.cam.isOpened():
            # self.log.printDebug('Camera did not initialise.', self.debug)
            raise Exception('Camera did not initialise, restart.')
        self.cam.set(3, config_data.width)
        self.cam.set(4, config_data.height)
        self.folderpath = config_data.savepath # still needs to add the name, now it has only the directory to be saved

        if not(os.path.exists(config_data.logpath)):
            os.mkdir(config_data.logpath)
            

    def test_camera(self):
        print("Press 'q' to exit the live feed.")
        while True:
            ret, frame = self.cam.read()
            if not ret:
                self.log.printDebug("Error: Can't receive frame (stream end?). Exiting ...", self.debug)
                print("Error: Can't receive frame (stream end?). Exiting ...")
                break
            cv2.imshow('Live Feed', frame)
            if cv2.waitKey(1) == ord('q'):
                break
        cv2.destroyAllWindows()

    def run(self):
        while True:
            ret, frame = self.cam.read()
            if not ret:
                break

            # Check if background model needs to be updated
            dif_time = time.time() - self.last_bg_update
            if dif_time >= self.bg_update_interval:
                # print(f"{time.strftime('%Y-%m-%d %H:%M:%S')} Commencing background refresh after {dif_time}...")
                self.log.printDebug(f"{time.strftime('%Y-%m-%d %H:%M:%S')} Commencing background refresh after {dif_time}...", self.debug)
                self.fgbg = cv2.createBackgroundSubtractorMOG2(detectShadows=True)
                self.last_bg_update = time.time()
                self.bg_model_initialized = False

            # Initialize background model for first 3 seconds
            if not self.bg_model_initialized:
                for _ in range(int(3 * self.framerate)):
                    ret, frame = self.cam.read()
                    fgmask = self.fgbg.apply(frame)
                    time.sleep(1 / self.framerate)
                self.bg_model_initialized = True

            # Apply background subtraction
            fgmask = self.fgbg.apply(frame)

            # Check if there is significant foreground (i.e., change from background)
            foreground_area = cv2.countNonZero(fgmask)
            total_area = frame.shape[0] * frame.shape[1]
            if foreground_area > 0.01 * total_area:
                # Save current frame to disk
                timestamp = datetime.now().strftime("%Y%m%d-%H%M%S-%f")
                # output_dir_folder = os.path.join(self.output_dir, 'D' + timestamp[:8], 'H' + timestamp[9:11])
                output_dir_folder = os.path.join(self.folderpath,timestamp[:8],timestamp[9:13])
                filename = os.path.join(output_dir_folder, f"{timestamp}.png")
                if not os.path.exists(output_dir_folder):
                    os.makedirs(output_dir_folder)

                cv2.imwrite(filename, frame)
                # print(f"{time.strftime('%Y-%m-%d %H:%M:%S')} Motion detected! Initiated file capture and storage protocol. File {filename} saved successfully.")
                self.log.printDebug(f"{time.strftime('%Y-%m-%d %H:%M:%S')} Motion detected! Initiated file capture and storage protocol. File {filename} saved successfully.", self.debug)
                # Print debug message if debug mode is on
                if self.debug:
                    # Show the current frame with the foreground mask
                    cv2.imshow('frame', frame)
                    cv2.imshow('fgmask', fgmask)

            # Check for quit key
            if cv2.waitKey(1) == ord('q'):
                break

        # Release video capture device and close all windows
        self.release_camera()


    def release_camera(self):
        self.cam.release()
        cv2.destroyAllWindows()

# Usage example
if __name__ == "__main__":
    config_path = "/home/pepper/InsectAI-SDM/spyder-insect-cameratrap/spyder-code/config/config.json"
    config_data = Configuration(config_path)
    # print(config_data.camera_index)
    camera_trap = Camera(config_data)
    camera_trap.run()
