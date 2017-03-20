import string

def load_wisdom():
    f = open('forward_plan.txt','r')
    plan = ''
    for l in f.readlines():
        plan = plan+l
    return plan


def read_wisdom(fname):
    f = open(fname+'_0.txt')
    lines = f.readlines()
    part1 = '' 
    for l in lines:
        part1 = part1+l
    f.close()
    
    f = open(fname+'_1.txt')
    lines = f.readlines()
    part2 ='' 
    for l in lines:
        part2 = part2+l
    f.close()
   
    f = open(fname+'_2.txt')
    lines = f.readlines()
    part3 = '' 
    for l in lines:
        part3 = part3+l
    f.close()

    return [part1,part2,part3]
#print read_wisdom()
#print part1
#print part2
#print part3

