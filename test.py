import cv2 as cv
import os
import face_recognition
import numpy as np

from datetime import date
import sqlite3



# Specify the directory path
directory = "saved_imgs"


# Check if the directory already exists
if not os.path.exists(directory):
    # Create the directory
    os.makedirs(directory)
    print("Directory created successfully!")

else:
    print("Directory already exists!")



# sqlite3 globals-----------------------------------

connector = sqlite3.connect("attPROJECT.db")
cur = connector.cursor()

today = date.today()
textdate = today.strftime("%B%d%Y")

print(textdate)

try:
    cur.execute(f"""
                ALTER TABLE attendance ADD COLUMN {textdate} VARCHAR(10) DEFAULT 'x' 
                """)
    cur.execute(f"""
                ALTER TABLE attendance ADD COLUMN {textdate}_time VARCHAR(10) DEFAULT 'x' 
                """)
    connector.commit()

except:
    pass

# --------------------------------------------------

def find_encodings():

    encoded_imgs = []
    for img in os_saved_imgs:
        img = cv.imread(f"{directory}/{img}")
        img = cv.cvtColor(img, cv.COLOR_BGR2RGB)
        encoded_imgs.append(face_recognition.face_encodings(img)[0])
    # print("len = ", len(encoded_imgs))
    
    return encoded_imgs

def match(cur_frame, enc_imgs):
    

    faces_cur_frame = face_recognition.face_locations(cur_frame)
    encode_cur_frame = face_recognition.face_encodings(cur_frame)

    for encode_face, face_loc in zip(encode_cur_frame, faces_cur_frame):
        matches = face_recognition.compare_faces(enc_imgs, encode_face)
        face_dist = face_recognition.face_distance(enc_imgs, encode_face)

        match_i = np.argmin(face_dist)
        # print("face_dist ->", len(face_dist))

        # print(face_dist)
        # print(f"{match_i=}")

        # print(len(matches))
        if matches[match_i]:
            name = os_saved_imgs[match_i]
            dot = name.index('.')

            name = name[:dot]

            mark_a(name)

            
            return (face_loc, name)
        
# --------------------------------------------------------------------------------------------------------

global os_saved_imgs
os_saved_imgs = os.listdir(directory)

dot = '.'

ids = []

for filename in os_saved_imgs:
    ids.append(int(filename[:filename.index(dot)]))


# --------------------------------------------------------------------------------------------------------

def recog(enc_imgs):
    
    cap = cv.VideoCapture(0)
    ret = True 

    while ret:

        ret, img = cap.read()

        imgS = cv.resize(img, (0, 0), None, 0.25, 0.25)
        imgS = cv.cvtColor(imgS, cv.COLOR_BGR2RGB)

        try:
            
            faceloc, name = match(imgS, enc_imgs)
            top, right, bottom, left = faceloc
            top, right, bottom, left = top * 4, right* 4, bottom* 4, left* 4

            cv.rectangle(img, (left, top), (right, bottom), (0, 255, 0), 2)
            cv.putText(img, name, (left, top - 10), cv.FONT_HERSHEY_SIMPLEX, 2, (0, 255, 0), 3)

            

        except TypeError:
            pass

        
        cv.imshow('face', img)

        if cv.waitKey(1) == ord('q'):
            ret = False

    cap.release()
    cv.destroyAllWindows()

    for i in range (1,5):
        cv.waitKey(1)

    print("DONE !!! ")
    return None
    



def register(id):
    
    
    # TODO:
    # check if id exists!!

    if id in ids:
        print("ID ALREADY EXISTS!")
        return None


    cap = cv.VideoCapture(0) 
    ret = True 

    filename = directory + '/' + str(id) + '.jpg'

    while ret:

        ret, img = cap.read()

        cv.putText(img, "Press s to save", (50, 50), cv.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 3)
        cv.imshow('face', img)
        

        if cv.waitKey(1) == ord('s'):
            cv.imwrite(filename, img)
            ret = False

    cap.release()
    cv.destroyAllWindows()
    for i in range (1,5):
        cv.waitKey(1)

    # insert id into db.
    insert(id)

    mark_a(id)

    print("DONE !!! ")

    return None

def insert(id):
    cur.execute(f"""
                INSERT INTO attendance(id) VALUES({id})
                """)
    connector.commit()

def mark_a(id):

    cur.execute(f"""
                UPDATE attendance SET {textdate} = 'A' where id = {id}
                """)
    cur.execute(f"""
                UPDATE attendance SET {textdate}_time = time('now', 'localtime') where id = {id}
                """)
    connector.commit()

def menu():
    print("""
          1. REGISTER AN ID
          2. START ATTENDANCE
          3. QUIT
          """)

def main():

    
    options = [1, 2, 3]
    enc_imgs = find_encodings()

    while True:
        menu()
        choice = int(input("ENTER YOUR CHOICE: "))
        if choice not in options:
            print("Enter a valid choice")
            continue
        

        if choice == 1:
            userid = int(input("Enter your ID: "))
            register(userid)
            enc_imgs = find_encodings()
        elif choice == 2:
            recog(enc_imgs)
        else:
            break



if __name__ == "__main__":
    main()

