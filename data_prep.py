import os
import cv2
import numpy as np

from inference_sdk import InferenceHTTPClient

CLIENT = InferenceHTTPClient(
    api_url="https://detect.roboflow.com",
    api_key="nTDVCTv5Qb4iNEzfT1cX"
)


def get_img_path(dir_path):
    img_path = []
    for dirpath, dirnames, filenames in os.walk(dir_path):
        filenum = 0
        for file in filenames:
            if file.endswith(".jpg") or file.endswith(".png") or file.endswith(".jpeg"):
                img_path.append(os.path.join(dirpath, file))
                filenum = filenum + 1

    return img_path


def save_img(imageId, saveId):
    img = cv2.imread(img_path[imageId])
    img = cv2.resize(img, (WIN_W, WIN_H))
    img_save = img[drawBox[1]+2:drawBox[3]-1, drawBox[0]+2:drawBox[2]-1]
    img_save = cv2.cvtColor(img_save, cv2.COLOR_BGR2GRAY)
    img_save = cv2.resize(img_save, (100, 100))

    if not os.path.exists(f"pos_images"):
        os.makedirs(f"pos_images")

    cv2.imwrite(f"pos_images/{saveId}.jpg", img_save)


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
        print(f"drawBox: {drawBox}")
        mouseUp = True
        drawing = False


# Initialize the rectangle drawing variables
WIN_W = 800
WIN_H = 600
drawing = False
mouseUp = False
first = True
drawBox = [0, 0, 0, 0]
database = []
file = open("database.txt", "r")
for line in file.readlines():
    database.append(int(line))
file.close()
imageId = database[0]
saveId = database[1]
print(f"imageId: {imageId} | saveId: {saveId}")

img_path = get_img_path('datasets')

# Load the image
img = cv2.imread(img_path[imageId]) # 125 # 140
img = cv2.resize(img, (WIN_W, WIN_H))
cv2.imwrite(img_path[imageId], img)
print(img.shape)

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
        if mouseUp:
            save_img(imageId, saveId)
        if imageId < len(img_path) - 1:
            imageId += 1
            saveId += 1
            img = cv2.imread(img_path[imageId])  # 125 # 140
            img = cv2.resize(img, (WIN_W, WIN_H))
            cv2.imwrite(img_path[imageId], img)
            print(img_path[imageId])
            try:
                result = CLIENT.infer(img_path[imageId], model_id="drone-detection-a1tsf/6")
                drawBox = list(result["predictions"][0].values())[:4]
                drawBox = [int(i) for i in drawBox]
                drawBox[0] = int(drawBox[0] - drawBox[2] / 2)
                drawBox[1] = int(drawBox[1] - drawBox[3] / 2)
                drawBox[2] = drawBox[0] + drawBox[2]
                drawBox[3] = drawBox[1] + drawBox[3]
                print(f"drawBox: {drawBox}")
                mouseUp = True
            except Exception as e:
                print(e)
        print(f"ImageId: {imageId} | SaveId: {saveId}")
    elif key == ord('a'):
        if mouseUp:
            save_img(imageId, saveId)
        if imageId > 0:
            imageId -= 1
            saveId -= 1
            saveCurrId = 0
            mouseUp = False
        print(f"ImageId: {imageId} | SaveId: {saveId}")
    elif key == ord(' '):
        if mouseUp:
            save_img(imageId, saveId)
        saveId += 1
        print(f"ImageId: {imageId} | SaveId: {saveId}")
    elif key == ord("w"):
        img = cv2.imread(img_path[imageId])  # 125 # 140
        img = cv2.resize(img, (WIN_W, WIN_H))
        cv2.imwrite(img_path[imageId], img)
        print(img_path[imageId])
        try:
            result = CLIENT.infer(img_path[imageId], model_id="drone-detection-a1tsf/6")
            drawBox = list(result["predictions"][0].values())[:4]
            drawBox = [int(i) for i in drawBox]
            drawBox[0] = int(drawBox[0] - drawBox[2] / 2)
            drawBox[1] = int(drawBox[1] - drawBox[3] / 2)
            drawBox[2] = drawBox[0] + drawBox[2]
            drawBox[3] = drawBox[1] + drawBox[3]
            print(f"drawBox: {drawBox}")
            mouseUp = True
        except Exception as e:
            print(e)

file = open("database.txt", "w")
file.write(str(imageId) + "\n")
file.write(str(saveId))
file.close()
# Close the window
cv2.destroyAllWindows()
