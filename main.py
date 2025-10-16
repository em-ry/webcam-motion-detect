import cv2
import glob
import os
from send_email import send_email
from threading import Thread
import time

video = cv2.VideoCapture(0)
time.sleep(1)

# initializations
first_frame = None
status_list = []
count = 1


def clean_folder():
    images = glob.glob("images/*.png")
    for image in images:
        os.remove(image)


while True:
    status = 0
    check, frame = video.read()
    # convert to gray scale(for lower matrix numbers)
    gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2GRAY)
    # Apply gaussian blur(for more efficient calc)
    gray_frame_gau = cv2.GaussianBlur(gray_frame, (21,21), 0)

    if first_frame is None:
        first_frame = gray_frame_gau


    # Find absolute difference btw 1st frame & gray_frame_gau
    delta_frame = cv2.absdiff(first_frame, gray_frame_gau)

    # classify pictures based on threshold i.e.(returns list, choose second element)
    thresh_frame = cv2.threshold(delta_frame, 60, 255, cv2.THRESH_BINARY)[1]

    # To remove noise, we dilate* it
    dil_frame = cv2.dilate(thresh_frame, None, iterations=2)

    # find contours* around image and draw rectangle around them
    contours, check = cv2.findContours(dil_frame, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    for contour in contours:
        if cv2.contourArea(contour) < 10000:
            # i.e if img is < certain num of pixels, it's fake/abstract so "continue"(restart the search/loop)
            continue

        x, y, w, h = cv2.boundingRect(contour)
        # draw and apply rectangle to main frame(specifies:img, sequence, ", line color, line thickness)
        rectangle = cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 3)
        # logic for emailing tracked object
        if rectangle.any():
            status = 1
            # capture tracked object
            cv2.imwrite(f"images/{count}.png", frame)
            count = count + 1
            all_images = glob.glob("images/*.png")
            index = int(len(all_images)/ 2)
            img_with_obj = all_images[index]


    # logic for emailing tracked object contd.
    status_list.append(status)
    status_list = status_list[-2:]

    if status_list[0] == 1 and status_list[1] == 0:
        # create thread ibj/instance
        email_thread = Thread(target=send_email, args=(img_with_obj, ))
        email_thread.daemon = True

        clean_thread = Thread(target=clean_folder)
        clean_thread.daemon = True

        email_thread.start()
        email_thread.join()


    print(status_list)
    key = cv2.waitKey(1)

    cv2.imshow("my vid", frame)

    if key == ord("q"):
        break

video.release()
clean_thread.start()
