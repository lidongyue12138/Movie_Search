# coding = utf-8
import os

def getFilenameID(filename):
    id_num = [i for i in filename if "0"<=i<="9"]
    id_num = "".join(id_num)
    return id_num

#main_part
save_movie = open("crawler/save_review.txt", "a")
for filename in os.listdir("review"):
    filename = os.path.join("review", filename)
    id_num = getFilenameID(filename)
    save_movie.write(id_num+"\n")
save_movie.close()
