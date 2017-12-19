import numpy as np

print 'hello'

cmap = np.array([[ 0.        ,  0.        ,  0.5       ,  1.        ],
       [ 0.        ,  0.        ,  1.        ,  1.        ],
       [ 0.        ,  0.38888889,  1.        ,  1.        ],
       [ 0.        ,  0.83333333,  1.        ,  1.        ],
       [ 0.3046595 ,  1.        ,  0.66308244,  1.        ],
       [ 0.66308244,  1.        ,  0.3046595 ,  1.        ],
       [ 1.        ,  0.90123457,  0.        ,  1.        ],
       [ 1.        ,  0.48971193,  0.        ,  1.        ],
       [ 1.        ,  0.0781893 ,  0.        ,  1.        ],
       [ 0.5       ,  0.        ,  0.        ,  1.        ],
       [ 0.5       ,  0.        ,  0.        ,  1.        ],
       [ 0.5       ,  0.        ,  0.        ,  1.        ],
       [ 0.5       ,  0.        ,  0.        ,  1.        ],
       [ 0.5       ,  0.        ,  0.        ,  1.        ],
       [ 0.5       ,  0.        ,  0.        ,  1.        ],
       [ 0.5       ,  0.        ,  0.        ,  1.        ],
       [ 0.5       ,  0.        ,  0.        ,  1.        ],
       [ 0.5       ,  0.        ,  0.        ,  1.        ],
       [ 0.5       ,  0.        ,  0.        ,  1.        ],
       [ 0.5       ,  0.        ,  0.        ,  1.        ]])

cmap_doubled = []
for i in range(len(cmap)):
       x = cmap[i]
       cmap_doubled.append(x)
       if i+1 < len(cmap):
              interp = [np.mean([cmap[i][k],cmap[i+1][k]]) for k in range(len(x))]
              cmap_doubled.append(interp)
       else:
              cmap_doubled.append(x)
	#cmap_doubled.append(x)
	#cmap_doubled.append(x)
cmap_doubled = np.array(cmap_doubled)
idx =(4,6,14,24,29,34)#,44,54)
x = np.insert(cmap_doubled, idx, .95, axis=0)
#x[idx,3] = 1.
print x
np.save('cmap_cont.npy', x)