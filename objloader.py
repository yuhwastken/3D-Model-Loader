def load_object(file:str):
    vertices_position = []
    vertices_texture = []
    polygon_normal = []

    vertices = []
    indices = []

    cache = {}
    idx = 0
    with open(file,"r") as f:
        line = f.readline()
        while line:
            values = line.split()
            if (values[0]=="v"):
                vertices_position.append([float(i) for i in values[1:]])
            elif (values[0]=="vt"):
                vertices_texture.append([float(i) for i in values[1:]])
            elif (values[0]=="vn"):
                polygon_normal.append([float(i) for i in values[1:]])
            elif (values[0]=="f"):
                face_indices = []
                for x in values[1:]:
                    if x not in cache:
                        data = [int(i) for i in x.split("/")]
                        vertices.extend(vertices_position[data[0]-1])
                        vertices.extend(vertices_texture[data[1]-1])
                        vertices.extend(polygon_normal[data[2]-1])
                        cache[x]=idx
                        idx+=1
                    # if f line has more than 3 elements [0,1,2,3] -> [0,1,2] [0,2,3]
                    face_indices.append(cache[x])
                for i in range(1,len(face_indices)-1):
                    indices.extend([face_indices[0],face_indices[i],face_indices[i+1]])
            line = f.readline()

    return vertices,indices

def print_vertices(vertices,ver_len):
    for i in range(0,int(len(vertices)/ver_len)):
        print(vertices[i*ver_len:i*ver_len+ver_len])
    print()

def print_indices(indices):
    for i in range(0,int(len(indices)/3)):
        print(indices[i*3:i*3+3])
    print()

if __name__ == "__main__":
    vertices,indices = load_object("cube.obj")
    print(vertices)
    print(indices)
