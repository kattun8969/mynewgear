#!/usr/bin/env python3
"""Draw original editorial schematic of three drive-pedal directions."""
import sys
from PIL import Image,ImageDraw,ImageFont
FONT="/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc"
W,H=1440,760
def ft(n):return ImageFont.truetype(FONT,n)
im=Image.new("RGB",(W,H),"#0b1a34")
d=ImageDraw.Draw(im)
d.text((66,42),"3つの歪み、どう選ぶ？",font=ft(64),fill="#ffffff")
d.text((66,143),"手持ちのアンプと、欲しい音から比較",font=ft(32),fill="#c6d7ea")
products=[("BD-2","弾く強さ・反応","#2678cc"),("SD-1","中域・抜け","#ecad23"),("OD-3","低域・太さ","#bd4636")]
for i,(name,desc,color) in enumerate(products):
 x=76+i*456
 d.rounded_rectangle((x,230,x+380,670),radius=22,fill="#142847",outline="#304a69",width=4)
 d.rounded_rectangle((x+85,268,x+301,515),radius=23,fill=color,outline="#eff3ff",width=5)
 for ox in (x+144,x+246):d.ellipse((ox-26,290,ox+26,342),fill="#1e293a",outline="#e4e4e4",width=6)
 d.ellipse((x+178,426,x+215,464),fill="#0f2038",outline="#eeeeee",width=7)
 d.text((x+105,367),name,font=ft(44),fill="white")
 d.text((x+28,569),desc,font=ft(35),fill="#ffffff")
d.text((66,706),"編集部の比較イメージ｜実物の形状・色・寸法ではありません",font=ft(23),fill="#b6c6da")
im.save(sys.argv[1],optimize=True)
print("CREATED",W,H)
