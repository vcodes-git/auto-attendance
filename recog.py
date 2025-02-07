import os
import face_recognition
import numpy as np

# Specify the directory path
directory = "saved_imgs"


# Check if the directory already exists
if not os.path.exists(directory):
    # Create the directory
    os.makedirs(directory)
    print("Directory created successfully!")

else:
    print("Directory already exists!")

def find_encodings():
    os_saved_imgs = os.listdir(directory)

    encoded_imgs = []
    for img in os_saved_imgs:
        encoded_imgs.append(face_recognition.face_encodings(img))

    return encoded_imgs


def match(cur_frame, img_encodings):
    faces_cur_frame = face_recognition.face_locations(cur_frame)
    encode_cur_frame = face_recognition.face_encodings(cur_frame)

    for encode_face, face_loc in zip(encode_cur_frame, faces_cur_frame):
        matches = face_recognition.compare_faces(img_encodings, encode_face)
        face_dist = face_recognition.face_distance(img_encodings, encode_face)

        match_i = np.argmin(face_dist)

        if matches[match_i]:
            return face_loc
        
            






    