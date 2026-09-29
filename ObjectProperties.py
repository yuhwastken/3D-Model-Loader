import glfw
from glfw.GLFW import *
from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram, compileShader
import numpy as np
import pyrr
from PIL import Image
from TextureLoader import load_texture
from objloader import load_object
import time

#source
vertex_src = """
# version 330 core

layout(location = 0) in vec3 a_position;
layout(location = 1) in vec2 a_texture;
layout(location = 2) in vec3 a_color;
layout(location = 3) in vec3 a_normal;

uniform mat4 motion; //translation + rotation
uniform mat4 projection;
uniform mat4 view;

out vec2 v_texture;
out vec3 v_color;

void main(){
    gl_Position = projection * view * motion * vec4(a_position,1.0);
    v_texture = vec2(a_texture.s,1-a_texture.t);
    v_color = a_color;
}
"""

fragment_src = """
# version 330 core

in vec2 v_texture;
in vec3 v_color;

out vec4 out_color;

uniform sampler2D s_texture;
uniform int switcher;

void main(){
    if (switcher == 0){
        out_color = texture(s_texture,v_texture);
    } else if (switcher == 1){
        out_color = vec4(v_color,1.0);
    }
}
"""

def OpenGLInit():
    def window_resize(window,w,h):
        glViewport(0,0,w,h)
        projection = pyrr.matrix44.create_perspective_projection_matrix(100,w/h,0.1,100)
        glUniformMatrix4fv(proj_loc,1,GL_FALSE,projection)

    if not glfw.init(): raise Exception("cannot init")
    window = glfw.create_window(600,600,"test",None,None)
    if not window: glfw.terminate()

    glfw.set_window_size_callback(window,window_resize)
    glfw.make_context_current(window)

    shader = compileProgram(compileShader(vertex_src,GL_VERTEX_SHADER),compileShader(fragment_src,GL_FRAGMENT_SHADER))

    glUseProgram(shader)
    glClearColor(0,0,0,1) #RGBA background
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA,GL_ONE_MINUS_SRC_ALPHA)

    projection = pyrr.matrix44.create_perspective_projection_matrix(120,1,1,100) # (FOV,window ratio(width/height),near plane,far plane)
    view = pyrr.matrix44.create_look_at(pyrr.Vector3([0,0,3]),pyrr.Vector3([0,0,0]),pyrr.Vector3([0,1,0])) # eye , target , up

    proj_loc = glGetUniformLocation(shader,"projection")
    view_loc = glGetUniformLocation(shader,"view")

    glUniformMatrix4fv(proj_loc,1,GL_FALSE,projection)
    glUniformMatrix4fv(view_loc,1,GL_FALSE,view)
    return window

class Object:
    def LoadingObject(self,objfile:str,texturefile:str):
        self.vertices,self.indices = load_object(objfile)
        self.vertices = np.array(self.vertices,dtype = np.float32)
        self.indices = np.array(self.indices,dtype = np.uint32)

        # general VAO
        self.VAO = glGenVertexArrays(1) #3 arrays for 3 objects
        VBO = glGenBuffers(1)
        EBO = glGenBuffers(1)

        glBindVertexArray(self.VAO) #for cube
        glBindBuffer(GL_ARRAY_BUFFER,VBO) #vertex buffer object
        glBufferData(GL_ARRAY_BUFFER,self.vertices.nbytes,self.vertices,GL_STATIC_DRAW)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER,EBO) #element buffer object
        glBufferData(GL_ELEMENT_ARRAY_BUFFER,self.indices.nbytes,self.indices,GL_STATIC_DRAW)

        #glVertexAttribPointer(a_,numbers of variable belong to the a vertice row,type of variable,GL_FALSE,starting position of the variables)
        glEnableVertexAttribArray(0) #0 for a_postion
        glVertexAttribPointer(0,3,GL_FLOAT,GL_FALSE,self.vertices.itemsize*8,ctypes.c_void_p(0)) # byte 0 -> 12 is position
        glEnableVertexAttribArray(1) #1 for a_texture
        glVertexAttribPointer(1,2,GL_FLOAT,GL_FALSE,self.vertices.itemsize*8,ctypes.c_void_p(12)) # byte 12 -> 20 is texture coordinate

        self.texture = glGenTextures(1) # allocate for texture
        load_texture(texturefile,self.texture) #binding the texturefile into texture
        return self.vertices,self.indices,self.texture,self.VAO

    def ObjectMotion(self,shader,rotation_x,rotation_y,rotation_z,trans_x,trans_y,trans_z):
        rot_x = pyrr.Matrix44.from_x_rotation(rotation_x)
        rot_y = pyrr.Matrix44.from_y_rotation(rotation_y)
        rot_z = pyrr.Matrix44.from_z_rotation(rotation_z)
        rotation = pyrr.matrix44.multiply(pyrr.matrix44.multiply(rot_x,rot_y),rot_z)
        translation = pyrr.matrix44.create_from_translation(pyrr.Vector3([trans_x,trans_y,trans_z]))
        self.motion = pyrr.matrix44.multiply(rotation,translation)
        self.motion_loc = glGetUniformLocation(shader,"motion")
        return self.motion, self.motion_loc

    def ObjectRendering(self):
        glBindVertexArray(self.VAO)
        glBindTexture(GL_TEXTURE_2D,self.texture)
        glUniformMatrix4fv(self.motion_loc,1,GL_FALSE,self.motion)
        glDrawElements(GL_TRIANGLES,len(self.indices),GL_UNSIGNED_INT,None)


if __name__ == "__main__":

    window = OpenGLInit()

    model3d = Object()
    vertices,indices,texture,VAO = model3d.LoadingObject("chibi.obj","chibi.png")
    shader = compileProgram(compileShader(vertex_src,GL_VERTEX_SHADER),compileShader(fragment_src,GL_FRAGMENT_SHADER))


    FRAME_RATE = 30
    last_time = glfw.get_time()
    while not glfw.window_should_close(window):
        current_time = glfw.get_time()

        glfw.poll_events()

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        motion,motion_loc = model3d.ObjectMotion(shader,glfw.get_time(),glfw.get_time(),glfw.get_time(),0,0,-3)
        model3d.ObjectRendering()

        sleepTime=max(0,1/FRAME_RATE-glfw.get_time()+current_time)
        time.sleep(sleepTime)

        glfw.swap_buffers(window)

    glfw.terminate()
