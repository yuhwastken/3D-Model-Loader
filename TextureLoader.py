from OpenGL.GL import glBindTexture,glTexParameteri,glTexImage2D,GL_TEXTURE_2D,GL_TEXTURE_WRAP_S,GL_TEXTURE_WRAP_T,GL_TEXTURE_MIN_FILTER,GL_TEXTURE_MAG_FILTER,GL_REPEAT,GL_LINEAR,GL_RGBA,GL_UNSIGNED_BYTE
from PIL import Image

def load_texture(dir:str,texture):
    glBindTexture(GL_TEXTURE_2D,texture)
    glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_WRAP_S,GL_REPEAT)
    glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_WRAP_T,GL_REPEAT)
    glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_MIN_FILTER,GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_MAG_FILTER,GL_LINEAR)

    image = Image.open(dir)
    img_data = image.convert("RGBA").tobytes()
    glTexImage2D(GL_TEXTURE_2D,0,GL_RGBA,image.width,image.height,0,GL_RGBA,GL_UNSIGNED_BYTE,img_data)
    return texture
