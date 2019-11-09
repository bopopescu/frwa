from os import path
import face_recognition

class Face:
    def __init__(self, app):
        self.storage = app.config["storage"]
        self.db = app.db
        self.faces = []  # storage all faces in caches array of face object
        self.known_encoding_faces = []  # faces data for recognition
        self.face_user_keys = {}
        self.load_all()

    def load_user_by_index_key(self, index_key=0):

        key_str = str(index_key)
        print (key_str)
        print("key str is : ")

        if key_str in self.face_user_keys:
            print("inside the loop")
            print (key_str)
            print(self.face_user_keys[key_str])
            return self.face_user_keys[key_str]

        return None

    def load_train_file_by_name(self, name):
        trained_storage = path.join(self.storage, 'trained')
        return path.join(trained_storage, name)

    def load_unknown_file_by_name(self, name):
        unknown_storage = path.join(self.storage, 'unknown')
        return path.join(unknown_storage, name)

    def load_all(self):

        results = self.db.query('SELECT id, user_id, filename, created FROM faces')
        print(results)

        print ("just checking for load call ")

        for row in results:

            user_id = row[1]
            filename = row[2]

            face = {
                "id": row[0],
                "user_id": user_id,
                "filename": filename,
                "created": row[3]
            }
            self.faces.append(face)

            face_image = face_recognition.load_image_file(self.load_train_file_by_name(filename))
            print("filename")
            print (filename)
            face_image_encoding = face_recognition.face_encodings(face_image)[0]
            index_key = len(self.known_encoding_faces)
            self.known_encoding_faces.append(face_image_encoding)
            index_key_string = str(index_key)
            self.face_user_keys['{0}'.format(index_key_string)] = user_id
            print("check jj")

    def load_specific(self,userId):

        results = self.db.select("SELECT id, user_id, filename, created FROM faces where user_id=%s",[userId])
        print(results)

        print("shjjjjjjj ")

        #for row in results:
        if(len(results)>0):
            print("inside if specific")
            user_id = results[0][1]
            filename = results[0][2]

            face = {
                    "id": results[0][0],
                    "user_id": user_id,
                    "filename": filename,
                    "created": results[0][3]
            }

            self.faces.append(face)
            print(face)
            print ("check")
            face_image = face_recognition.load_image_file(self.load_train_file_by_name(filename))
            face_image_encoding = face_recognition.face_encodings(face_image)[0]
            index_key = len(self.known_encoding_faces)
            self.known_encoding_faces.append(face_image_encoding)
            index_key_string = str(index_key)
            self.face_user_keys['{0}'.format(index_key_string)] = user_id

    def recognize(self, unknown_filename):
        unknown_image = face_recognition.load_image_file(self.load_unknown_file_by_name(unknown_filename))
        print(unknown_image)
        print("manp checks 2 ")
        unknown_encoding_image = face_recognition.face_encodings(unknown_image)[0]
        print(self.known_encoding_faces)
        print("manp checks jj 3")
        results = face_recognition.compare_faces(self.known_encoding_faces, unknown_encoding_image, 0.5);
        results2 = face_recognition.api.face_distance(self.known_encoding_faces, unknown_encoding_image);

        print("results", results)
        print("results2", results2)

        index_key = 0
        user_id = -1;
        prevmatch = 1.0

        for matched in results:

            if matched and results2[index_key]<prevmatch:
                user_id = self.load_user_by_index_key(index_key)
                prevmatch = results2[index_key]

            index_key = index_key + 1

        if(user_id == -1):
            return None
        return user_id
