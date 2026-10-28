from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
from pathlib import Path
import math, textwrap, zipfile

ROOT=Path(__file__).parent
OUT=ROOT/'posters'
OUT.mkdir(exist_ok=True)
W=1400
SANS='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
BOLD='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
SERIF='/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf'
SERIFB='/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf'
MONO='/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf'

GOLD=(241,181,46); INK=(29,27,31); CREAM=(250,247,239); NAVY=(15,35,80); BLUE=(41,92,182); WHITE=(255,255,255)
LOGO=Image.open(ROOT/'SFC LOGO.jpg').convert('RGB').crop((50,165,675,565))
PORTRAIT=Image.open(ROOT/'veroni.jpg').convert('RGB')

FULL=[
'How do you honour those who have gone ahead of you? How do you treat the people whose sacrifices, wisdom, prayers, and labour have contributed to your becoming?',
'In a generation that is quick to desire greatness but sometimes slow to recognize those who came before them, God is calling us back to the culture of honour.',
'You can be gifted and still need guidance. You can be anointed and still need instruction. You can be rising and still owe gratitude to those who helped you along the way.',
'“Let the elders that rule well be counted worthy of double honour…” — 1 Timothy 5:17',
'Tonight, we are learning how to honour men, spiritual leaders, mentors, and those who have gone ahead of us without compromising our convictions or idolizing people.'
]
KEY='You cannot walk in the grace of honour while cultivating a culture of dishonour.'

def font(size,bold=False,serif=False,mono=False):
    f=MONO if mono else (SERIFB if serif and bold else SERIF if serif else BOLD if bold else SANS)
    return ImageFont.truetype(f,size)

def text_width(draw,s,f): return draw.textbbox((0,0),s,font=f)[2]
def wrap(draw, txt, f, width):
    words=txt.split(); lines=[]; line=''
    for word in words:
        test=(line+' '+word).strip()
        if text_width(draw,test,f)<=width or not line: line=test
        else: lines.append(line); line=word
    if line: lines.append(line)
    return lines

def para(draw, xy, txt, f, fill, width, leading=1.34, max_lines=None):
    x,y=xy; lines=wrap(draw,txt,f,width)
    if max_lines: lines=lines[:max_lines]
    step=int(f.size*leading)
    for i,line in enumerate(lines): draw.text((x,y+i*step),line,font=f,fill=fill)
    return y+len(lines)*step

def center_text(draw,xy,txt,f,fill):
    x,y=xy; draw.text((x-text_width(draw,txt,f)/2,y),txt,font=f,fill=fill)

def rr(draw,box,r,fill,outline=None,width=1): draw.rounded_rectangle(box,radius=r,fill=fill,outline=outline,width=width)

def gradient(size, top, bottom, vertical=True):
    w,h=size; im=Image.new('RGB',size); p=im.load()
    for y in range(h):
        for x in range(w):
            t=(y/(h-1)) if vertical else (x/(w-1)); p[x,y]=tuple(int(top[i]*(1-t)+bottom[i]*t) for i in range(3))
    return im

def crop_fill(im, size, focus=(.5,.5)):
    w,h=size; iw,ih=im.size; scale=max(w/iw,h/ih); im=im.resize((int(iw*scale),int(ih*scale)),Image.Resampling.LANCZOS)
    x=int((im.width-w)*focus[0]); y=int((im.height-h)*focus[1]); return im.crop((x,y,x+w,y+h))

def paste_photo(canvas,box,rad=28,focus=(.5,.28),tint=None):
    x,y,w,h=box; im=crop_fill(PORTRAIT,(w,h),focus)
    if tint:
        over=Image.new('RGB',im.size,tint); im=Image.blend(im,over,.12)
    mask=Image.new('L',(w,h)); ImageDraw.Draw(mask).rounded_rectangle((0,0,w-1,h-1),radius=rad,fill=255)
    canvas.paste(im,(x,y),mask)
    d=ImageDraw.Draw(canvas); d.rounded_rectangle((x,y,x+w,y+h),radius=rad,outline=(255,255,255,180),width=4)

def logo_on(canvas, box, dark=False):
    x,y,w,h=box
    im=LOGO.copy(); im.thumbnail((w,h),Image.Resampling.LANCZOS)
    # clean white backdrop keeps supplied raster logo readable on any design
    plate=Image.new('RGB',(w,h),(255,255,255)); px=(w-im.width)//2; py=(h-im.height)//2
    plate.paste(im,(px,py)); canvas.paste(plate,(x,y))

def brand_footer(d, y, width=1400, dark=False, small=False):
    c=(245,239,223) if dark else (42,47,57)
    d.line((80,y,width-80,y),fill=(GOLD if dark else (220,183,95)),width=2)
    f=font(20 if small else 23,bold=True); center_text(d,(width/2,y+20),'STREET FOR CHRIST  •  LOVE  |  PREACH  |  REACHOUT',f,c)

def header(d, small=False, dark=False):
    c=(255,246,221) if dark else INK
    d.text((70,52),'IGNITE',font=font(26 if small else 30,bold=True),fill=GOLD if dark else (171,119,21))
    d.text((70,88),'A STREET FOR CHRIST MESSAGE',font=font(14 if small else 16,bold=True),fill=c)

def save(im,name):
    im.save(OUT/name,quality=94,optimize=True)

# 1. Hero announcement: fiery square-inspired composition, with the whole written message.
def hero():
    n=1400; im=gradient((n,n),(20,25,20),(88,29,15)); d=ImageDraw.Draw(im)
    # warm glow + framing columns like the original title art
    glow=Image.new('RGBA',(n,n),(0,0,0,0)); gd=ImageDraw.Draw(glow)
    gd.ellipse((330,80,1110,910),fill=(235,105,15,78)); glow=glow.filter(ImageFilter.GaussianBlur(105)); im=Image.alpha_composite(im.convert('RGBA'),glow).convert('RGB'); d=ImageDraw.Draw(im)
    d.rectangle((80,220,225,880),fill=(237,112,31)); d.rectangle((1175,220,1320,880),fill=(237,112,31))
    logo_on(im,(550,30,300,145)); header(d)
    d.text((130,175),'THE GRACE CALLED',font=font(60,bold=True),fill=(255,237,196),stroke_width=2,stroke_fill=(83,30,11))
    d.text((130,240),'HONOUR!',font=font(104,bold=True),fill=(255,198,65),stroke_width=4,stroke_fill=(103,39,12))
    paste_photo(im,(495,365,410,425),30,(.5,.22))
    d=ImageDraw.Draw(im); rr(d,(90,835,1310,1275),28,(255,249,235))
    d.text((125,865),'VERON  •  EXCERPT | 15 OCTOBER 2026  •  10:00 PM',font=font(22,bold=True),fill=(110,61,20))
    y=910
    for p in FULL:
        y=para(d,(125,y),p,font(20),INK,1150,1.32)+7
    brand_footer(d,1303,dark=True,small=True)
    save(im,'01_ignite_grace_called_honour_full_message.png')

# 2. Notebook/editorial template: ruled page and headline notes.
def notebook():
    n=1400; im=Image.new('RGB',(n,n),(244,241,229)); d=ImageDraw.Draw(im)
    # wood header/footer, ruled paper field
    d.rectangle((0,0,n,195),fill=(94,53,31)); d.rectangle((0,1205,n,n),fill=(94,53,31))
    for y in range(335,1170,55): d.line((100,y,1300,y),fill=(188,196,184),width=2)
    d.line((190,300,190,1175),fill=(210,117,120),width=3)
    logo_on(im,(85,35,230,135)); d.text((390,50),'STREET FOR CHRIST PRESENTS',font=font(25,bold=True),fill=(255,255,255))
    d.text((385,92),'IGNITE  /  SERMON EXCERPT',font=font(18,bold=True),fill=(245,203,104))
    d.text((250,230),'THE GRACE CALLED HONOUR',font=font(51,bold=True),fill=(38,37,36))
    d.text((250,300),'VERON  •  15 OCTOBER 2026  •  10:00 PM',font=font(22,bold=True),fill=(148,49,38))
    d.text((260,385),'How do you honour those who came before you?',font=font(31,bold=True,serif=True),fill=(37,37,37))
    y=445
    for p in [FULL[0],FULL[1],FULL[2],FULL[3],KEY]:
        y=para(d,(260,y),p,font(22),INK,1020,1.3)+18
    # tiny hand-drawn accent underline
    d.line((255,1124,790,1124),fill=(179,47,38),width=5)
    d.text((260,1140),'WITH GRATITUDE. WITHOUT IDOLATRY.',font=font(18,bold=True),fill=(70,69,64))
    brand_footer(d,1240,dark=True,small=True)
    save(im,'02_notebook_ignite_excerpt.png')

# 3. Sermon excerpt split card: image left, oversized quote right.
def excerpt():
    n=1400; im=gradient((n,n),(248,239,246),(255,252,242)); d=ImageDraw.Draw(im)
    d.rectangle((0,0,35,n),fill=(221,196,226)); logo_on(im,(90,55,185,118))
    d.text((300,70),'STREET FOR CHRIST  /  IGNITE',font=font(21,bold=True),fill=(70,47,75))
    paste_photo(im,(80,270,505,700),24,(.5,.24))
    d.text((85,1000),'VERON',font=font(47,bold=True,serif=True),fill=(132,50,58))
    d.text((85,1060),'THE GRACE CALLED HONOUR',font=font(20,bold=True),fill=(74,54,67))
    d.text((660,240),'“',font=font(120,bold=True,serif=True),fill=(112,47,67))
    y=para(d,(665,365),'You cannot walk in the grace of honour while cultivating a culture of dishonour.',font(56,bold=True), (67,35,39),650,1.22)
    d.line((665,y+25,1270,y+25),fill=(189,127,62),width=4)
    para(d,(665,y+62),'You can be gifted and still need guidance. Anointed and still need instruction. Rising and still owe gratitude.',font(27), (74,58,67),650,1.35)
    d.text((665,1035),'1 TIMOTHY 5:17',font=font(25,bold=True),fill=(128,76,28))
    d.text((665,1075),'15 OCTOBER 2026  •  10:00 PM',font=font(21,bold=True),fill=(65,55,62))
    brand_footer(d,1280,small=True)
    save(im,'03_sermon_excerpt_quote.png')

# 4. Handwritten notes template: chalk/ink annotations around speaker portrait.
def notes():
    n=1400; im=Image.new('RGB',(n,n),(248,247,242)); d=ImageDraw.Draw(im)
    logo_on(im,(60,35,190,120)); d.text((325,48),'SERMON NOTES',font=font(58,bold=True,serif=True),fill=(28,65,68))
    d.text((330,117),'VERON  •  IGNITE  •  THE GRACE CALLED HONOUR',font=font(21,bold=True),fill=(55,47,48))
    rr(d,(910,190,1310,300),18,(99,56,56)); d.text((940,220),'CULTURE OF HONOUR',font=font(22,bold=True),fill=WHITE)
    # portrait sits in the lower middle, notes arranged around like the handwritten source
    paste_photo(im,(470,450,420,610),30,(.5,.18))
    notes_data=[
        ((48,245),'1. REMEMBER THOSE', 'Sacrifices, wisdom, prayers and labour.'),
        ((970,350),'2. HONOUR WELL', 'Spiritual leaders, mentors and elders.'),
        ((48,565),'3. RECEIVE GUIDANCE', 'Gifted? Still need guidance. Anointed? Still need instruction.'),
        ((970,735),'4. GIVE GRATITUDE', 'Rise without forgetting who helped you along.'),
        ((48,930),'KEEP CONVICTIONS', 'Honour without idolizing people or compromising.'),
    ]
    for (x,y),title,body in notes_data:
        d.ellipse((x,y,x+14,y+14),fill=(143,80,71)); d.text((x+22,y-7),title,font=font(17,bold=True),fill=(43,67,66))
        para(d,(x+22,y+28),body,font(16), (49,55,53),330 if x>900 else 350,1.28)
    d.text((490,1120),'“Let the elders that rule well be counted worthy of double honour…”',font=font(19,bold=True,serif=True),fill=(103,55,57))
    d.text((590,1152),'— 1 TIMOTHY 5:17',font=font(17,bold=True),fill=(60,80,79))
    d.text((425,1210),'15 OCTOBER 2026   •   10:00 PM',font=font(24,bold=True),fill=(41,55,57))
    brand_footer(d,1290,small=True)
    save(im,'04_sermon_notes_honour.png')

# 5. Minimal brush-stroke testimonial layout: central portrait, message below.
def brush():
    # Reinterpret the uploaded square brush-stroke sermon graphic while keeping
    # its original hierarchy: corner branding, central brush/photo, centered quote,
    # speaker band, and social footer.
    n=1400; im=Image.new('RGB',(n,n),(250,249,245)); d=ImageDraw.Draw(im)
    logo_on(im,(72,42,190,120))
    d.text((288,55),'IGNITE  •  STREET FOR CHRIST',font=font(24,bold=True),fill=(42,42,44))
    d.text((1060,50),'15 OCTOBER',font=font(18,bold=True),fill=(42,42,44))
    d.text((1095,78),'10:00 PM',font=font(18,bold=True),fill=(42,42,44))
    # Organic dry-brush patch (the reference's central black paint field).
    # Irregular polygon silhouette with several dry-brush streaks at the edges.
    d.polygon([(185,215),(290,185),(370,208),(455,180),(555,202),(650,174),(760,202),(855,181),(960,205),(1050,184),(1208,222),(1170,287),(1250,325),(1190,382),(1232,450),(1155,505),(1200,560),(1108,590),(1020,570),(930,608),(830,580),(730,612),(630,580),(535,605),(438,574),(340,600),(255,561),(180,575),(220,505),(150,458),(210,398),(160,342),(225,290)],fill=(29,27,40))
    # dry, tapered streaks on the outside of the brush shape
    for i in range(9):
        yy=242+i*39
        d.polygon([(120,yy),(250,yy-10),(220,yy+15),(135,yy+24)],fill=(29,27,40))
        d.polygon([(1140,yy-8),(1290,yy-20),(1260,yy+2),(1155,yy+18)],fill=(29,27,40))
    paste_photo(im,(410,190,580,460),0,(.5,.12))
    # Fine light border distinguishes the portrait from the paint swash.
    d=ImageDraw.Draw(im)
    d.rectangle((410,190,990,650),outline=(246,245,242),width=4)
    center_text(d,(700,715),'THE GRACE CALLED HONOUR!',font(45,bold=True), (35,35,38))
    quote='You cannot walk in the grace of honour while cultivating a culture of dishonour.'
    y=para(d,(170,790),quote,font(36), (46,46,48),1060,1.38)
    center_text(d,(700,y+10),'Honour those who went ahead—without compromising convictions or idolizing people.',font(22), (72,69,68))
    # Reference-inspired speaker/session strip.
    rr(d,(220,1015,1180,1125),3,(112,83,94))
    center_text(d,(700,1035),'VERON',font(30,bold=True),WHITE)
    center_text(d,(700,1075),'IGNITE  •  EXCERPT  •  15 OCTOBER 2026  •  10:00 PM',font(17,bold=True), (245,239,237))
    # Social row, using the supplied church name rather than inventing account handles.
    y0=1175
    for i,label in enumerate(('f','◎','▶')):
        x=515+i*52; d.ellipse((x,y0,x+36,y0+36),fill=(42,42,43))
        center_text(d,(x+18,y0+5),label,font(22,bold=True),WHITE)
    d.text((680,y0+6),'Street for Christ',font=font(23),fill=(52,51,52))
    brand_footer(d,1280,small=True)
    save(im,'05_brushstroke_excerpt.png')


def replica():
    # Faithful structural adaptation of download.jpeg: use the uploaded reference
    # itself for its paper texture and exact brush composition, replacing the
    # speaker, corner branding, excerpt, session strip and social footer.
    n=1400; base=Image.open(ROOT/'download.jpeg').convert('RGB').resize((n,n),Image.Resampling.LANCZOS)
    im=base.copy(); d=ImageDraw.Draw(im)
    scale=n/736
    def P(points): return [(int(x*scale),int(y*scale)) for x,y in points]
    def B(box): return tuple(int(v*scale) for v in box)
    # Softly neutralize the original speaker within the brush field. The feathered
    # ink patch matches the reference's deep paint and stays behind the new cutout.
    ink_mask=Image.new('L',(n,n),0); md=ImageDraw.Draw(ink_mask); md.ellipse((455,260,905,680),fill=255)
    ink_mask=ink_mask.filter(ImageFilter.GaussianBlur(9))
    ink=Image.new('RGB',(n,n),(35,32,46)); im.paste(ink,(0,0),ink_mask)
    # Patch the source speaker's visible hand/arm edges within the same ink field.
    edge_mask=Image.new('L',(n,n),0); ed=ImageDraw.Draw(edge_mask)
    ed.ellipse((438,590,555,790),fill=215); ed.ellipse((785,605,880,715),fill=225)
    edge_mask=edge_mask.filter(ImageFilter.GaussianBlur(8)); im.paste(ink,(0,0),edge_mask)
    # Clear just the original corner marks and lower copy, retaining the same paper tone.
    paper=base.getpixel((int(50*scale),int(500*scale)))
    d=ImageDraw.Draw(im)
    d.rectangle(B((20,15,145,96)),fill=base.getpixel((int(30*scale),int(30*scale))))
    d.rectangle(B((585,15,730,100)),fill=base.getpixel((int(600*scale),int(30*scale))))
    d.rectangle(B((0,470,736,736)),fill=paper)
    logo_on(im,(55,35,160,100))
    d=ImageDraw.Draw(im)
    d.text((1080,38),'IGNITE',font=font(32,bold=True),fill=(39,38,40))
    d.text((1005,77),'THE GRACE CALLED',font=font(19,bold=True),fill=(45,43,45))
    d.text((1060,103),'HONOUR!',font=font(27,bold=True,serif=True),fill=(45,43,45))
    # Central, cut-out speaker portrait, positioned as in the original design.
    person=Image.open(ROOT/'assets/veronica_sasha_cutout.png').convert('RGBA').crop((0,0,258,385))
    person=person.resize((435,646),Image.Resampling.LANCZOS)
    alpha=person.getchannel('A'); shadow=Image.new('RGBA',person.size,(0,0,0,0)); shadow.putalpha(alpha.point(lambda a:int(a*.2)))
    shadow=shadow.filter(ImageFilter.GaussianBlur(9))
    im.paste(shadow,(478,265),shadow); im.paste(person,(465,255),person)
    d=ImageDraw.Draw(im)
    center_text(d,(700,915),'You cannot walk in the grace of honour',font(34), (43,43,45))
    center_text(d,(700,960),'while cultivating a culture of dishonour.',font(34), (43,43,45))
    center_text(d,(700,1011),'Honour those who went ahead—with gratitude and conviction.',font(21), (57,57,59))
    center_text(d,(700,1050),'“Let the elders that rule well be counted worthy of double honour…” — 1 Timothy 5:17',font(16,bold=True,serif=True), (92,76,83))
    # Mauve speaker/session band and centered social row replicate the reference.
    d.rectangle(B((160,584,576,632)),fill=(143,120,132))
    center_text(d,(700,1120),'VERONICA SASHA',font(28,bold=True),WHITE)
    center_text(d,(700,1160),'IGNITE  •  15 OCTOBER 2026  •  10:00 PM',font(17), (250,246,247))
    y=1292
    for i,label in enumerate(('f','◎','▶')):
        x=535+i*48; d.ellipse((x,y,x+32,y+32),fill=(43,43,44))
        center_text(d,(x+16,y+4),label,font(20,bold=True),WHITE)
    d.text((690,y+5),'Street for Christ',font=font(21),fill=(51,50,52))
    save(im,'09_ignite_veronica_sasha_replica.png')

# 6. Sermon-on-stage style: deep spotlight, note fragments and speaker right.
def stage():
    n=1400; im=gradient((n,n),(31,33,57),(17,17,24)); d=ImageDraw.Draw(im)
    # soft light beams
    layer=Image.new('RGBA',(n,n),(0,0,0,0)); ld=ImageDraw.Draw(layer)
    ld.polygon([(420,0),(730,0),(1120,1100),(810,1100)],fill=(121,151,235,25)); ld.polygon([(890,0),(1020,0),(1250,1100),(1100,1100)],fill=(224,133,122,20))
    im=Image.alpha_composite(im.convert('RGBA'),layer.filter(ImageFilter.GaussianBlur(38))).convert('RGB'); d=ImageDraw.Draw(im)
    logo_on(im,(55,35,185,125)); d.text((300,45),'SERMON EXCERPT',font=font(50,bold=True),fill=(250,249,245))
    d.text((305,108),'VERON  /  IGNITE  /  15 OCTOBER 2026',font=font(20,bold=True),fill=(220,217,230))
    paste_photo(im,(830,340,480,840),18,(.5,.2))
    # notes to left in chalk-like text
    d.text((85,250),'“You cannot walk in the grace',font=font(28,bold=True,mono=True),fill=(245,245,243))
    d.text((85,295),'of honour while cultivating',font=font(28,bold=True,mono=True),fill=(245,245,243))
    d.text((85,340),'a culture of dishonour.”',font=font(28,bold=True,mono=True),fill=(245,245,243))
    d.line((85,390,695,390),fill=(240,239,233),width=3)
    para(d,(85,445),'You can be gifted and still need guidance. Anointed and still need instruction.',font(25), (239,239,244),650,1.42)
    para(d,(85,640),'Honour elders, mentors and spiritual leaders—without idolizing people.',font(25), (239,239,244),650,1.42)
    rr(d,(80,955,745,1125),22,(247,243,235))
    para(d,(115,980),'“Let the elders that rule well be counted worthy of double honour…”',font(23,bold=True), (38,39,44),590,1.3)
    d.text((118,1080),'1 TIMOTHY 5:17',font=font(17,bold=True),fill=(89,75,88))
    d.text((830,1190),'VERON',font=font(39,bold=True),fill=WHITE)
    d.text((80,1200),'THE GRACE CALLED HONOUR  •  10:00 PM',font=font(20,bold=True),fill=(248,225,168))
    brand_footer(d,1290,dark=True,small=True)
    save(im,'06_stage_sermon_notes.png')

# 7. Word capsule design: pale blue, white text card and speaker image to right.
def capsules():
    n=1400; im=gradient((n,n),(219,235,248),(246,248,252)); d=ImageDraw.Draw(im)
    logo_on(im,(65,45,165,110)); d.text((280,55),'STREET FOR CHRIST   •   IGNITE',font=font(22,bold=True),fill=(32,51,90))
    d.text((1095,60),'15 OCT 2026',font=font(17,bold=True),fill=(30,47,79))
    rr(d,(85,260,995,1030),20,(255,255,255))
    rr(d,(130,220,430,295),8,(32,52,108)); d.text((155,237),'WORD CAPSULES',font=font(24,bold=True),fill=WHITE)
    capsule_texts=['How do you honour those who went ahead of you?', 'Gifted and still guided. Anointed and still instructed.', 'Rise—and remember who helped you along the way.', 'Honour without compromise. Gratitude without idolatry.']
    y=350
    for i,t in enumerate(capsule_texts):
        y=para(d,(145,y),t,font(29), (29,56,110),790,1.25)+32
    paste_photo(im,(980,435,360,760),12,(.5,.2))
    d.text((110,1080),'THE GRACE CALLED HONOUR',font=font(43,bold=True),fill=(25,48,101))
    d.text((110,1140),'VERON  •  10:00 PM  •  1 TIMOTHY 5:17',font=font(21,bold=True),fill=(37,62,110))
    brand_footer(d,1280,small=True)
    save(im,'07_word_capsules.png')

# 8. Purple quote bubbles: several short statements, with name and event mark.
def bubbles():
    n=1400; im=gradient((n,n),(49,24,61),(27,22,44)); d=ImageDraw.Draw(im)
    # subtle grain dots
    for y in range(10,n,34):
        for x in range(10,n,34):
            if (x*7+y*3)%5==0: d.ellipse((x,y,x+2,y+2),fill=(107,74,112))
    logo_on(im,(60,45,170,115)); d.text((285,52),'IGNITE  /  STREET FOR CHRIST',font=font(22,bold=True),fill=WHITE)
    d.text((1070,55),'15 OCTOBER 2026',font=font(18,bold=True),fill=(237,220,185))
    d.text((80,205),'THE GRACE',font=font(46,bold=True),fill=WHITE)
    d.text((80,258),'CALLED HONOUR',font=font(49,serif=True),fill=(255,228,177))
    cards=[
        ((80,370,730,535),'How do you honour those who have gone ahead of you?'),
        ((110,570,760,735),'You can be gifted and still need guidance.'),
        ((80,770,730,935),'You can be rising and still owe gratitude.'),
        ((110,970,760,1135),'Honour without compromise or idolizing people.'),
    ]
    for box,txt in cards:
        rr(d,box,28,(246,235,244)); x1,y1,x2,y2=box
        for j in range(3): d.ellipse((x2-68+j*15,y1+17,x2-60+j*15,y1+25),fill=(111,76,112))
        para(d,(x1+34,y1+55),txt,font(25,bold=True),(36,31,40),x2-x1-68,1.28)
    paste_photo(im,(820,365,520,810),25,(.5,.2))
    d.text((855,1190),'VERON',font=font(40,bold=True,serif=True),fill=WHITE)
    d.text((80,1190),'1 TIMOTHY 5:17  •  10:00 PM',font=font(19,bold=True),fill=(249,226,187))
    brand_footer(d,1290,dark=True,small=True)
    save(im,'08_quote_bubbles.png')

for fn in [hero,notebook,excerpt,notes,brush,replica,stage,capsules,bubbles]: fn()

# Preview sheet for easy review and a portable bundle for delivery.
files=sorted(OUT.glob('*.png'))
thumb_w=420; thumb_h=420
sheet=Image.new('RGB',(thumb_w*4,thumb_h*((len(files)+3)//4)),(231,231,231))
for idx,f in enumerate(files):
    im=Image.open(f).convert('RGB'); im.thumbnail((thumb_w-18,thumb_h-40),Image.Resampling.LANCZOS)
    x=(idx%4)*thumb_w+(thumb_w-im.width)//2; y=(idx//4)*thumb_h+8
    sheet.paste(im,(x,y)); ImageDraw.Draw(sheet).text(((idx%4)*thumb_w+10,(idx//4+1)*thumb_h-26),f.stem,font=font(13,bold=True),fill=(35,35,35))
sheet.save(OUT/'00_poster_overview.jpg',quality=90)
# A print-friendly multipage PDF; each page keeps the square social-poster proportions.
pages=[Image.open(f).convert('RGB') for f in files]
pages[0].save(OUT/'Street_For_Christ_IGNITE_Posters.pdf',save_all=True,append_images=pages[1:],resolution=150)
with zipfile.ZipFile(OUT/'Street_For_Christ_IGNITE_Posters.zip','w',zipfile.ZIP_DEFLATED) as z:
    for f in files: z.write(f,f.name)
    z.write(OUT/'Street_For_Christ_IGNITE_Posters.pdf','Street_For_Christ_IGNITE_Posters.pdf')
    z.write(OUT/'00_poster_overview.jpg','00_poster_overview.jpg')
