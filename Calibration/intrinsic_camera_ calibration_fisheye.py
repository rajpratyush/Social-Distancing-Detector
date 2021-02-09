import cv2
assert cv2.__version__[0] == '3', 'The fisheye module requires opencv version >= 3.0.0'
import numpy as np
import os
import glob
import argparse

if __name__ == "__main__":

    ap = argparse.ArgumentParser()
    ap.add_argument("-cw", "--chessboard_width", required=False, default="8", help="number of intersections in x axis")
    ap.add_argument("-ch", "--chessboard_height", required=False, default="6", help="number of intersections in y axis")
    ap.add_argument("-sd", "--square_dimension", required=False, default="0.035", help="square dimension in meters")
    ap.add_argument("-p", "--path", required=True, help="path to images folder")
    ap.add_argument("-e", "--file_extension", required=False, default=".jpg", help="extension of images")
    ap.add_argument("-a", "--auto_mode", required=False, default="True", \
                    help="automatic mode uses all images inside images folder to run calibration")
    args = vars(ap.parse_args())

    auto_mode = eval(args["auto_mode"])
    CHESSBOARD_WIDTH = int(args["chessboard_width"])
    CHESSBOARD_HEIGHT = int(args["chessboard_height"])
    CALIBRATION_SQUARE_DIMENSION = float(args["square_dimension"]) # meters

    path = args["path"] + "*" + args["file_extension"]
    chessboardDimension = (CHESSBOARD_WIDTH, CHESSBOARD_HEIGHT)

    # termination criteria
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.0001)

    # prepare object points, like (0,0,0), (1,0,0), (2,0,0) ....,(6,5,0)
    objp = np.zeros((1,CHESSBOARD_HEIGHT*CHESSBOARD_WIDTH, 3), np.float32)
    objp[0,:,:2] = np.mgrid[0:CHESSBOARD_WIDTH, 0:CHESSBOARD_HEIGHT].T.reshape(-1, 2)*CALIBRATION_SQUARE_DIMENSION

    # Arrays to store object points and image points from all the images.
    objPoints = [] # 3d point in real world space
    imgPoints = [] # 2d points in image plane.

    images = glob.glob(path)

    for fname in images:
        img = cv2.imread(fname)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # Find the chess board corners
        ret, corners = cv2.findChessboardCorners(gray, chessboardDimension,\
                                                 cv2.CALIB_CB_ADAPTIVE_THRESH+cv2.CALIB_CB_NORMALIZE_IMAGE)
        if ret:
            if not auto_mode:
                imgCopy = img.copy()

                corners2 = cv2.cornerSubPix(gray, corners, (3, 3), (-1, -1), criteria)
                imgCopy = cv2.drawChessboardCorners(imgCopy, chessboardDimension, corners2, ret)

                cv2.imshow('img', imgCopy)

                while True:
                    key = cv2.waitKey(10) & 0xFF
                    if ord('s') == key:
                        # imgPoints.append(corners)
                        objPoints.append(objp)
                        imgPoints.append(corners2)
                        break
                    elif ord('d') == key:
                        break
            else:
                objPoints.append(objp)
                corners2 = cv2.cornerSubPix(gray, corners, (3, 3), (-1, -1), criteria)
                imgPoints.append(corners2)

    if not auto_mode:
        cv2.destroyAllWindows()


    calibration_flags = cv2.fisheye.CALIB_RECOMPUTE_EXTRINSIC + cv2.fisheye.CALIB_FIX_SKEW
    K = np.zeros((3, 3))
    D = np.zeros((4, 1))
    rvecs = [np.zeros((1, 1, 3), dtype=np.float64) for i in range(len(objPoints))]
    tvecs = [np.zeros((1, 1, 3), dtype=np.float64) for i in range(len(objPoints))]
    cv2.fisheye.calibrate(objPoints, imgPoints, (640,480), K, D, rvecs, tvecs, calibration_flags,\
                              (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 1e-6))
    print(K)
    print(D)