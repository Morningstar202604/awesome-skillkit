from PIL import Image, ImageEnhance
import sys
def cinematic(p): im=Image.open(p); im=ImageEnhance.Contrast(im).enhance(1.2); im=ImageEnhance.Color(im).enhance(0.6); im.save(p+'.moody.jpg'); print('done',p+'.moody.jpg')
if __name__=='__main__':
    cinematic(sys.argv[1])
