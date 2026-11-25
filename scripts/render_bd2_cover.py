#!/usr/bin/env python3
"""Create a brand-native ORIGINAL BD-2 guide graphic (not a product photograph).

The pedal shape is intentionally schematic to avoid implying exact product
appearance. Japanese title is rendered with Noto CJK when present.
"""
import argparse
import math
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W,H=1600,900
def find_font():
    import glob
    candidates=[
      "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc",
      "/usr/share/fonts/truetype/noto/NotoSansCJK-Bold.ttc",
      "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
    ]
    for p in candidates:
        try:
            ImageFont.truetype(p,70)
            return p
        except (OSError,ValueError):
            continue
    raise RuntimeError("Install fonts-noto-cjk; do not substitute a font that cannot render Japanese")

def font(p,n):
    return ImageFont.truetype(p,n)
def text(draw,xy,value,f,fill,stroke_width=0,stroke_fill=None):
    draw.text(xy,value,font=f,fill=fill,stroke_width=stroke_width,stroke_fill=stroke_fill)
def main(path):
    fp=find_font()
    im=Image.new("RGB",(W,H),(7,20,41));px=im.load()
    for y in range(H):
        for x in range(W):
            v=(x/W)*0.18+(y/H)*0.13
            px[x,y]=(int(9+17*v),int(22+36*v),int(43+47*v))
    d=ImageDraw.Draw(im)
    # Navy/blue diagonal zones with restrained orange accent.
    d.polygon([(0,650),(W,190),(W,900),(0,900)],fill=(9,37,69))
    d.polygon([(900,0),(1015,0),(W,505),(W,595)],fill=(15,69,101))
    d.line([(40,730),(1090,410)],fill=(246,132,46),width=12)
    # Subtle blue light around schematic pedal.
    light=Image.new("RGBA",(W,H),(0,0,0,0))
    ld=ImageDraw.Draw(light)
    ld.ellipse((865,116,1520,860),fill=(40,116,210,35))
    light=light.filter(ImageFilter.GaussianBlur(78))
    im=Image.alpha_composite(im.convert("RGBA"),light)
    d=ImageDraw.Draw(im)
    # Tilted abstract pedal, not a photographic rendering.
    d.polygon([(1107,180),(1450,220),(1494,778),(1020,741)],fill=(15,66,128),outline=(65,138,205),width=12)
    d.polygon([(1126,202),(1435,240),(1455,526),(1087,496)],fill=(28,91,159),outline=(89,163,222),width=5)
    for x,y in [(1180,305),(1370,329),(1272,435)]:
        d.ellipse((x-38,y-38,x+38,y+38),fill=(13,25,42),outline=(236,235,219),width=6)
        d.ellipse((x-20,y-20,x+20,y+20),fill=(169,179,186))
        d.line([(x,y),(x+4,y-23)],fill=(14,35,52),width=6)
    d.ellipse((1240,610,1364,734),fill=(7,25,48),outline=(228,231,227),width=11)
    d.ellipse((1273,642,1332,700),fill=(145,154,163))
    d.ellipse((1316,504,1339,527),fill=(251,131,47))
    # Overlays; keep the title on a safe left side.
    d.rounded_rectangle((78,91,650,164),radius=17,fill=(251,137,54))
    text(d,(106,100),"オーバードライブ購入ガイド",font(fp,43),(12,28,47))
    text(d,(75,208),"BOSS BD-2",font(fp,116),(252,252,248))
    text(d,(71,352),"買う前に比較",font(fp,101),(253,159,73))
    d.rounded_rectangle((76,525,820,635),radius=16,fill=(7,22,47),outline=(60,171,225),width=5)
    text(d,(112,540),"SD-1 / OD-3 と何が違う？",font(fp,54),(244,249,250))
    text(d,(86,784),"音作り・代替機材・選び方",font(fp,45),(224,235,246))
    im.convert("RGB").save(path,"PNG",optimize=True)
    print("CREATED "+path+" "+str(W)+"x"+str(H)+" original abstract art")
if __name__=="__main__":
    parser=argparse.ArgumentParser();parser.add_argument("output")
    main(parser.parse_args().output)
