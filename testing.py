import numpy as np
x = np.ones((460,640))
x = x.reshape(-1)
val = 442240.
x = np.concatenate((np.zeros(val), x))
x = np.concatenate((x, np.zeros(val)))
print x.shape



def make_acceleration_field(x,y,mass):
    field = np.zeros((640,460))
    dx = np.zeros(field.shape)
    dy = np.zeros(field.shape)
    pot = np.zeros(field.shape)
    for i in range(field.shape[0]):
        for j in range(field.shape[1]):
            try:
                dx[i,j]=(1./(i-x)**2)
            except:
                dx[i,j]=(1./(i+1-x)**2)
            try:
                dy[i,j]=(1./(j-y)**2)
            except:
                dy[i,j]=(1./(j+1-y)**2)
            pot[i,j] = -(1/np.sqrt((j-y)**2 + (i-x)**2))
    pot[x,y] = 0
    #field[x,y] = field[x+1,y+1] #remove singularity
    dx[x,y] = dx[x+1,y]
    dy[x,y] = dy[x,y+1]
    return dx,dy, pot
