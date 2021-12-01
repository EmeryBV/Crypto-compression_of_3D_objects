import random


class Encrypton:
    print("coucou")

def randomGenerator(value, nTaille, result):
    random.seed(value)
    for i in range(nTaille) :
        result[i] = random.random()%  256



# def encode(MeshIn, meshOut,  nTaille, SID){
#
#     int result[nTaille];
#     randormGenerator(SID, nTaille,result);
#
#     for (int i = 0; i <nTaille ; ++i) {
#
#         int  bit1 = ImgIn[i] ;
#         int  bit2 = result[i] ;
#         ImgOut[i] = bit1 ^ bit2  ;
#
#     }
# }