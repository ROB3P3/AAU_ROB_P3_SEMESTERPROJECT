import os
import glob


path = "C:/FishProject/Test/TestThresholds/"

# take all images from path and take the number from the name. If the lenght of the number is more than 5, remove the first number
images = glob.glob(path + "*.png")
print(images)
for image in images:
    name = image.rsplit('\\', 1)[-1]
    print(name)
    # split the number from the names which look like 0005Final.png
    number = name.split("Final")[0]
    print(number)
    if len(number) > 5:
        number = number[1:]
        print(number)
    newFileName = path + number + "Final.png"
    print("Newname:", newFileName)
    os.rename(image, newFileName)



