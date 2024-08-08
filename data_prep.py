import os
import cv2
import numpy as np


def get_img_path(dir_path):
    img_path = []
    for dirpath, dirnames, filenames in os.walk(dir_path):
        filenum = 0
        for file in filenames:
            if file.endswith(".jpg") or file.endswith(".png") or file.endswith(".jpeg"):
                img_path.append(os.path.join(dirpath, file))
                filenum = filenum + 1

    return img_path


def save_img(idx):
    img = cv2.imread(img_path[idx])
    img = cv2.resize(img, (WIN_W, WIN_H))
    img_save = img[drawBox[1]+2:drawBox[3]-1, drawBox[0]+2:drawBox[2]-1]
    img_save = cv2.cvtColor(img_save, cv2.COLOR_BGR2GRAY)
    img_save = cv2.resize(img_save, (100, 100))

    if not os.path.exists(f"datasets/kaggle-drone/pos_images"):
        os.makedirs(f"datasets/kaggle-drone/pos_images")

    cv2.imwrite(f"datasets/kaggle-drone/pos_images/{idx}.jpg", img_save)


# Mouse callback function
def draw_rectangle(event, x, y, flags, param):
    global drawing, mouseUp, start_x, start_y, img, drawBox
    img = cv2.imread(img_path[imageId])
    img = cv2.resize(img, (WIN_W, WIN_H))

    cv2.line(img, (x, y), (WIN_W, y), (255, 0, 0), 1)
    cv2.line(img, (x, y), (x, WIN_H), (255, 0, 0), 1)
    cv2.line(img, (x, y), (0, y), (255, 0, 0), 1)
    cv2.line(img, (x, y), (x, 0), (255, 0, 0), 1)

    if event == cv2.EVENT_LBUTTONDOWN:
        drawing = True
        start_x, start_y = x, y
        drawBox[0] = start_x
        drawBox[1] = start_y
        drawBox[2] = start_x
        drawBox[3] = start_y
    elif event == cv2.EVENT_MOUSEMOVE:
        if drawing:
            if x > start_x:
                drawBox[2] = x
            else:
                drawBox[0] = x
                drawBox[2] = start_x
            if y > start_y:
                drawBox[3] = y
            else:
                drawBox[1] = y
                drawBox[3] = start_y
    elif event == cv2.EVENT_LBUTTONUP:
        mouseUp = True
        drawing = False


# Initialize the rectangle drawing variables
WIN_W = 800
WIN_H = 600
drawing = False
mouseUp = False
first = True
drawBox = [0, 0, 0, 0]
imageId = 0
saveId = 0
saveCurrId = 0

img_path = get_img_path('datasets')

# Load the image
img = cv2.imread(img_path[imageId])
img = cv2.resize(img, (WIN_W, WIN_H))

# Create a window and display the image
cv2.imshow('Image', img)


# Set the mouse callback function
cv2.setMouseCallback('Image', draw_rectangle)

# Wait for the user to press the 'esc' key
while True:
    # Draw the rectangle on the image
    if drawing:
        cv2.rectangle(img, (drawBox[0], drawBox[1]), (drawBox[2], drawBox[3]), (0, 255, 0), 2)
    elif mouseUp:
        cv2.rectangle(img, (drawBox[0], drawBox[1]), (drawBox[2], drawBox[3]), (0, 255, 0), 2)

    # Create a window and display the image
    cv2.imshow('Image', img)

    key = cv2.waitKey(1) & 0xFF

    if key == 27:  # 'esc' key
        break
    elif key == ord('d'):  # 'd' key
        save_img(imageId)
        if imageId < len(img_path) - 1:
            imageId += 1
            saveId += 1
            saveCurrId = 1
            mouseUp = False
    elif key == ord('a'):
        save_img(imageId)
        if imageId > 0:
            imageId -= 1
            saveId -= saveCurrId
            saveCurrId = 0
            mouseUp = False
    elif key == ord(' '):
        save_img(saveId)
        saveId += 1
        saveCurrId += 1
        mouseUp = False
# Close the window
cv2.destroyAllWindows()
