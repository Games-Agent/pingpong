import asyncio,pygame,sys,math,random,io,wave,json,os
pygame.init()
master_volume=0.7;sound_enabled=True;mixer_initialized=False;_sound_cache={}
def init_mixer():
 global mixer_initialized
 if mixer_initialized:return True
 try:pygame.mixer.init(44100,-16,2,512);mixer_initialized=True;return True
 except:return False
def make_beep(f,d,v=0.5):
 try:
  sr=44100;n=int(sr*d/1000);buf=io.BytesIO();wv=wave.open(buf,"wb");wv.setnchannels(2);wv.setsampwidth(2);wv.setframerate(sr);amp=int(32767*v);fr=bytearray()
  for i in range(n):
   e=1.0-(i/n);x=int(amp*e*math.sin(2*math.pi*f*i/sr));lo=x&0xFF;hi=(x>>8)&0xFF
   fr.append(lo);fr.append(hi);fr.append(lo);fr.append(hi)
  wv.writeframes(bytes(fr));wv.close();buf.seek(0);return pygame.mixer.Sound(file=buf)
 except:return None
SOUND_DEFS={"paddle":(660,60,0.6),"wall":(440,50,0.5),"score":(330,220,0.6),"win":(880,400,0.6),"click":(550,40,0.4)}
def play_sound(n):
 if not sound_enabled:return
 if not init_mixer():return
 s=_sound_cache.get(n)
 if s is None:
  d=SOUND_DEFS[n];s=make_beep(d[0],d[1],d[2])
  if s is None:return
  try:s.set_volume(master_volume)
  except:pass
  _sound_cache[n]=s
 try:s.play()
 except:pass
def apply_volume():
 for s in _sound_cache.values():
  try:s.set_volume(master_volume)
  except:pass
W,H=360,720
screen=pygame.display.set_mode((W,H));pygame.display.set_caption("Ping Pong Arena");clock=pygame.time.Clock()
BG_TOP=(60,70,95);BG_BOT=(30,35,55);TABLE_DARK=(0,70,140);TABLE_LIGHT=(20,130,220);TABLE_EDGE=(200,165,60);LINE_COLOR=(255,255,255)
PADDLE_P_DARK=(140,30,30);PADDLE_P_LIGHT=(230,80,80);PADDLE_B_DARK=(30,30,140);PADDLE_B_LIGHT=(90,100,230)
SLIDER_BG=(60,65,85);SLIDER_FILL=(220,80,80);SLIDER_KNOB=(240,240,245);NET_COLOR=(240,240,240);GOLD=(255,215,0);GOLD_DARK=(180,140,30)
SKIN_TONES=[(255,224,196),(255,213,170),(240,195,155),(220,175,130),(200,150,110),(180,130,95),(150,105,75),(120,80,55),(95,60,40),(235,190,165),(245,205,175),(210,165,130)]
HAIR_COLORS=[(90,55,30),(140,90,50),(200,160,90),(220,200,140),(240,220,170),(200,80,60),(60,40,25)]
BALL_COLORS={"WHITE":(255,255,255),"YELLOW":(255,230,60),"RED":(240,70,70),"GREEN":(80,220,100),"CYAN":(90,220,230),"PURPLE":(190,100,230),"ORANGE":(255,150,50),"PINK":(255,130,200),"BLACK":(30,30,30)}
BALL_COLOR_ORDER=["WHITE","YELLOW","RED","GREEN","CYAN","PURPLE","ORANGE","PINK","BLACK"];ball_color_name="WHITE"
HEADER_TITLE_Y=int(H*0.015);HEADER_TITLE_H=int(H*0.05);HEADER_INFO_Y=HEADER_TITLE_Y+HEADER_TITLE_H+int(H*0.012);HEADER_INFO_H=int(H*0.045)
TABLE_X=int(W*0.20);TABLE_Y=HEADER_INFO_Y+HEADER_INFO_H+int(H*0.02);TABLE_W=W-2*TABLE_X;TABLE_H=int(H*0.62);TABLE_CX=TABLE_X+TABLE_W//2;TABLE_CY=TABLE_Y+TABLE_H//2
PW=int(TABLE_W*0.30);PH=max(10,int(TABLE_H*0.026));BALL_R=max(7,int(min(TABLE_W,TABLE_H)*0.022))
SLIDER_Y=TABLE_Y+TABLE_H+int(H*0.05);SLIDER_W=int(W*0.8);SLIDER_X=(W-SLIDER_W)//2;SLIDER_H=max(10,int(H*0.022));KNOB_R=max(14,int(H*0.03))
GEAR_R=int(H*0.025);GEAR_RECT=pygame.Rect(W-GEAR_R*2-8,HEADER_TITLE_Y+(HEADER_TITLE_H-GEAR_R*2)//2,GEAR_R*2,GEAR_R*2)
def cyrfont(s,bold=False):
 try:return pygame.font.SysFont("arial,dejavusans,liberationsans,notosans,roboto",s,bold=bold)
 except:return pygame.font.Font(None,s)
SCORE_FONT=cyrfont(int(H*0.03),True);BIG_FONT=cyrfont(int(H*0.06),True);HUGE_FONT=cyrfont(int(H*0.085),True);SMALL_FONT=cyrfont(int(H*0.022))
TIMER_FONT=cyrfont(int(H*0.03),True);TITLE_FONT=cyrfont(int(H*0.028),True);BTN_FONT=cyrfont(int(H*0.026),True);KEY_FONT=cyrfont(int(H*0.028),True);INPUT_FONT=cyrfont(int(H*0.045),True)
MAX_SCORE=5;SETTINGS_FILE="/tmp/pingpong_settings.json";NAME_MAX=8;wins_total=0;best_score=0;game_mode="NORMAL"
NAME_ALLOWED="abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
DIFFICULTIES={"EASY":{"bot_speed_mul":0.6,"ball_init_mul":0.85,"ball_max_mul":0.85,"accel_mul":0.7},"NORMAL":{"bot_speed_mul":1.0,"ball_init_mul":1.0,"ball_max_mul":1.0,"accel_mul":1.0},"HARD":{"bot_speed_mul":1.45,"ball_init_mul":1.15,"ball_max_mul":1.2,"accel_mul":1.3}}
TRANSLATIONS={"EN":{"title":"PING PONG","subtitle":"ARENA","player":"Player","play":"PLAY","difficulty":"DIFFICULTY","stats":"STATS","name":"NAME","set_name":"set name","quit":"QUIT","language":"LANGUAGE","back":"BACK","easy":"EASY","normal":"NORMAL","hard":"HARD","wins":"Wins","best":"Best score","reset":"RESET","reset_q":"Reset stats?","yes":"YES","no":"NO","enter_name":"ENTER NAME","name_rules":"English/digits, max 8","ok":"OK","del":"DELETE","clear":"CLEAR","paused":"PAUSED","volume":"Volume","resume":"RESUME","end":"END","quit_to_menu":"QUIT TO MENU","you":"YOU","bot":"BOT","you_win":"You Win!","bot_win":"Bot Wins!","tap_menu":"Tap to return to menu","rally":"Rally","slide_move":"<  SLIDE TO MOVE  >","english":"ENGLISH","russian":"RUSSIAN","ball":"BALL","sound":"SOUND","on":"ON","off":"OFF","rage":"RAGE!","new_record":"NEW RECORD!","mode":"MODE","mode_normal":"NORMAL","mode_infinite":"INFINITE"},"RU":{"title":"\u041f\u0418\u041d\u0413 \u041f\u041e\u041d\u0413","subtitle":"\u0410\u0420\u0415\u041d\u0410","player":"\u0418\u0433\u0440\u043e\u043a","play":"\u0418\u0413\u0420\u0410\u0422\u042c","difficulty":"\u0421\u041b\u041e\u0416\u041d\u041e\u0421\u0422\u042c","stats":"\u0421\u0422\u0410\u0422\u0418\u0421\u0422\u0418\u041a\u0410","name":"\u0418\u041c\u042f","set_name":"\u0432\u0432\u0435\u0441\u0442\u0438 \u0438\u043c\u044f","quit":"\u0412\u042b\u0425\u041e\u0414","language":"\u042f\u0417\u042b\u041a","back":"\u041d\u0410\u0417\u0410\u0414","easy":"\u041b\u0415\u0413\u041a\u041e","normal":"\u0421\u0420\u0415\u0414\u041d\u0415","hard":"\u0421\u041b\u041e\u0416\u041d\u041e","wins":"\u041f\u043e\u0431\u0435\u0434","best":"\u0420\u0435\u043a\u043e\u0440\u0434","reset":"\u0421\u0411\u0420\u041e\u0421","reset_q":"\u0421\u0431\u0440\u043e\u0441\u0438\u0442\u044c?","yes":"\u0414\u0410","no":"\u041d\u0415\u0422","enter_name":"\u0412\u0412\u0415\u0414\u0418 \u0418\u041c\u042f","name_rules":"\u0410\u043d\u0433\u043b. \u0431\u0443\u043a\u0432\u044b \u0438 \u0446\u0438\u0444\u0440\u044b, \u043c\u0430\u043a\u0441 8","ok":"\u041e\u041a","del":"\u0421\u0422\u0415\u0420\u0415\u0422\u042c","clear":"\u041e\u0427\u0418\u0421\u0422\u0418\u0422\u042c","paused":"\u041f\u0410\u0423\u0417\u0410","volume":"\u0413\u0440\u043e\u043c\u043a\u043e\u0441\u0442\u044c","resume":"\u041f\u0420\u041e\u0414\u041e\u041b\u0416\u0418\u0422\u042c","end":"\u041a\u041e\u041d\u0415\u0426","quit_to_menu":"\u0412 \u041c\u0415\u041d\u042e","you":"\u0422\u042b","bot":"\u0411\u041e\u0422","you_win":"\u041f\u043e\u0431\u0435\u0434\u0430!","bot_win":"\u0411\u043e\u0442 \u043f\u043e\u0431\u0435\u0434\u0438\u043b!","tap_menu":"\u041d\u0430\u0436\u043c\u0438 \u0432\u0435\u0440\u043d\u0443\u0442\u044c\u0441\u044f","rally":"\u0420\u043e\u0437\u044b\u0433\u0440\u044b\u0448","slide_move":"<  \u0412\u0415\u0414\u0418 \u041f\u041e\u041b\u0417\u0423\u041d\u041e\u041a  >","english":"\u0410\u041d\u0413\u041b\u0418\u0419\u0421\u041a\u0418\u0419","russian":"\u0420\u0423\u0421\u0421\u041a\u0418\u0419","ball":"\u041c\u042f\u0427","sound":"\u0417\u0412\u0423\u041a","on":"\u0412\u041a\u041b","off":"\u0412\u042b\u041a\u041b","rage":"\u042f\u0420\u041e\u0421\u0422\u042c!","new_record":"\u041d\u041e\u0412\u042b\u0419 \u0420\u0415\u041a\u041e\u0420\u0414!","mode":"\u0420\u0415\u0416\u0418\u041c","mode_normal":"\u041e\u0411\u042b\u0427\u041d\u042b\u0419","mode_infinite":"\u0411\u0415\u0421\u041a\u041e\u041d\u0415\u0427\u041d\u042b\u0419"}}
language="EN"
def T(k):return TRANSLATIONS.get(language,TRANSLATIONS["EN"]).get(k,k)
def load_settings():
 global language,master_volume,ball_color_name,sound_enabled,wins_total,best_score,game_mode
 try:
  with open(SETTINGS_FILE,"r") as f:
   d=json.load(f);language=d.get("language","EN");master_volume=float(d.get("volume",0.7))
   bc=d.get("ball_color","WHITE")
   if bc in BALL_COLORS:ball_color_name=bc
   sound_enabled=bool(d.get("sound",True));wins_total=int(d.get("wins_total",0));best_score=int(d.get("best_score",0))
   gm=d.get("mode","NORMAL")
   if gm in ("NORMAL","INFINITE"):game_mode=gm
 except:pass
def save_settings():
 try:
  with open(SETTINGS_FILE,"w") as f:json.dump({"language":language,"volume":master_volume,"ball_color":ball_color_name,"sound":sound_enabled,"wins_total":wins_total,"best_score":best_score,"mode":game_mode},f)
 except:pass
load_settings()
def update_record(s):
 global best_score
 if s>best_score:best_score=s;save_settings();return True
 return False
def vgrad(w,h,c1,c2):
 s=pygame.Surface((w,h))
 for y in range(h):
  t=y/max(1,h-1);c=(int(c1[0]+(c2[0]-c1[0])*t),int(c1[1]+(c2[1]-c1[1])*t),int(c1[2]+(c2[2]-c1[2])*t));pygame.draw.line(s,c,(0,y),(w,y))
 return s
fan_w=max(34,int(W*0.075));fan_h=int(fan_w*2.0)
def make_fan(shirt,mood,skin=None,hair=None):
 s=pygame.Surface((fan_w,fan_h),pygame.SRCALPHA)
 if skin is None:skin=random.choice(SKIN_TONES)
 if hair is None:hair=random.choice(HAIR_COLORS)
 hr=fan_w//3;cx=fan_w//2;hy=hr+4;pygame.draw.rect(s,skin,(cx-3,hy+hr-4,6,6));bt=hy+hr;bh=fan_h-bt-2
 pygame.draw.rect(s,shirt,(3,bt,fan_w-6,bh),border_radius=6);dk=(max(0,shirt[0]-50),max(0,shirt[1]-50),max(0,shirt[2]-50))
 pygame.draw.rect(s,dk,(3,bt+bh*2//3,fan_w-6,bh//3),border_radius=6);pygame.draw.polygon(s,dk,[(cx-5,bt),(cx+5,bt),(cx,bt+7)])
 nm=random.randint(1,99);nf=cyrfont(max(10,fan_w//4),True);nt=nf.render(str(nm),True,(255,255,255));s.blit(nt,(cx-nt.get_width()//2,bt+bh//3))
 pygame.draw.circle(s,skin,(cx,hy),hr);pygame.draw.circle(s,hair,(cx,hy-2),hr);pygame.draw.rect(s,skin,(cx-hr,hy,hr*2,hr+2))
 pygame.draw.circle(s,skin,(cx,hy+1),hr-1);pygame.draw.circle(s,skin,(cx-hr+1,hy+1),3);pygame.draw.circle(s,skin,(cx+hr-1,hy+1),3)
 pygame.draw.arc(s,hair,(cx-hr,hy-hr,hr*2,hr+4),0,math.pi,3);ey=hy+1;e1=cx-hr//2;e2=cx+hr//2
 if mood=="wow":
  pygame.draw.circle(s,(255,255,255),(e1,ey),4);pygame.draw.circle(s,(255,255,255),(e2,ey),4);pygame.draw.circle(s,(40,40,60),(e1,ey),2);pygame.draw.circle(s,(40,40,60),(e2,ey),2)
  pygame.draw.line(s,(40,30,20),(e1-3,ey-6),(e1+3,ey-7),2);pygame.draw.line(s,(40,30,20),(e2-3,ey-7),(e2+3,ey-6),2)
  pygame.draw.ellipse(s,(40,20,20),(cx-4,ey+hr//2-2,8,8));pygame.draw.ellipse(s,(200,80,80),(cx-3,ey+hr//2,6,5))
 elif mood=="sad":
  pygame.draw.circle(s,(40,40,60),(e1,ey+1),2);pygame.draw.circle(s,(40,40,60),(e2,ey+1),2)
  pygame.draw.line(s,(40,30,20),(e1-4,ey-6),(e1+3,ey-3),2);pygame.draw.line(s,(40,30,20),(e2-3,ey-3),(e2+4,ey-6),2)
  pygame.draw.arc(s,(40,20,20),(cx-7,ey+hr//2,14,10),math.pi,2*math.pi,2);pygame.draw.circle(s,(100,180,255),(e1,ey+6),2)
 else:
  pygame.draw.circle(s,(40,40,60),(e1,ey),2);pygame.draw.circle(s,(40,40,60),(e2,ey),2)
  pygame.draw.line(s,(40,30,20),(e1-3,ey-5),(e1+3,ey-5),2);pygame.draw.line(s,(40,30,20),(e2-3,ey-5),(e2+3,ey-5),2)
  pygame.draw.arc(s,(60,30,30),(cx-5,ey+4,10,5),math.radians(200),math.radians(340),1)
  pygame.draw.circle(s,(255,180,180),(e1-1,ey+4),2);pygame.draw.circle(s,(255,180,180),(e2+1,ey+4),2)
 if mood=="wow":
  pygame.draw.line(s,shirt,(5,bt+4),(-2,hy-8),5);pygame.draw.line(s,shirt,(fan_w-5,bt+4),(fan_w+2,hy-8),5)
  pygame.draw.circle(s,skin,(-2,hy-8),3);pygame.draw.circle(s,skin,(fan_w+2,hy-8),3);pygame.draw.rect(s,GOLD,(-6,hy-14,8,6))
 else:
  pygame.draw.line(s,shirt,(5,bt+4),(1,bt+16),5);pygame.draw.line(s,shirt,(fan_w-5,bt+4),(fan_w-1,bt+16),5)
 return s
crowd_rows=[]
for i in range(4):
 ry=TABLE_Y+int(TABLE_H*0.08)+i*int(TABLE_H*0.22)
 cl=(random.randint(180,240),random.randint(40,90),random.randint(40,90));sl=random.choice(SKIN_TONES);hl=random.choice(HAIR_COLORS)
 crowd_rows.append({"side":"L","x":TABLE_X//2,"y":ry,"happy":make_fan(cl,"happy",sl,hl),"wow":make_fan(cl,"wow",sl,hl),"sad":make_fan(cl,"sad",sl,hl),"phase":random.uniform(0,math.pi*2)})
 cr=(random.randint(40,90),random.randint(40,90),random.randint(180,240));sr=random.choice(SKIN_TONES);hr2=random.choice(HAIR_COLORS)
 crowd_rows.append({"side":"R","x":TABLE_X+TABLE_W+(W-TABLE_X-TABLE_W)//2,"y":ry,"happy":make_fan(cr,"happy",sr,hr2),"wow":make_fan(cr,"wow",sr,hr2),"sad":make_fan(cr,"sad",sr,hr2),"phase":random.uniform(0,math.pi*2)})
def build_playfield():
 pf=vgrad(W,H,BG_TOP,BG_BOT);br=pygame.Rect(int(W*0.10),HEADER_TITLE_Y,int(W*0.70),HEADER_TITLE_H)
 pygame.draw.rect(pf,(30,30,50),br,border_radius=10);pygame.draw.rect(pf,GOLD,br,2,border_radius=10)
 t=TITLE_FONT.render("PING PONG ARENA",True,GOLD);pf.blit(t,(br.centerx-t.get_width()//2,br.centery-t.get_height()//2))
 ir=pygame.Rect(int(W*0.05),HEADER_INFO_Y,int(W*0.90),HEADER_INFO_H);pygame.draw.rect(pf,(20,25,45),ir,border_radius=8);pygame.draw.rect(pf,(90,90,120),ir,1,border_radius=8)
 sw=ir.width//3;pygame.draw.line(pf,(90,90,120),(ir.x+sw,ir.y+6),(ir.x+sw,ir.bottom-6),1);pygame.draw.line(pf,(90,90,120),(ir.x+2*sw,ir.y+6),(ir.x+2*sw,ir.bottom-6),1)
 ft=TABLE_Y-15;fb=TABLE_Y+TABLE_H+30;fl=vgrad(W,fb-ft,(90,95,115),(50,55,75));pf.blit(fl,(0,ft))
 sh=pygame.Surface((TABLE_W+20,TABLE_H+20),pygame.SRCALPHA);pygame.draw.rect(sh,(0,0,0,100),(0,0,TABLE_W+20,TABLE_H+20),border_radius=14);pf.blit(sh,(TABLE_X-5,TABLE_Y+5))
 tg=vgrad(TABLE_W,TABLE_H,TABLE_LIGHT,TABLE_DARK);mk=pygame.Surface((TABLE_W,TABLE_H),pygame.SRCALPHA);pygame.draw.rect(mk,(255,255,255),(0,0,TABLE_W,TABLE_H),border_radius=10)
 tg.blit(mk,(0,0),special_flags=pygame.BLEND_RGBA_MIN);pf.blit(tg,(TABLE_X,TABLE_Y))
 hh=(TABLE_H-12)//2;bz=pygame.Surface((TABLE_W-12,hh),pygame.SRCALPHA);bz.fill((60,80,220,90));pf.blit(bz,(TABLE_X+6,TABLE_Y+6))
 rz=pygame.Surface((TABLE_W-12,hh),pygame.SRCALPHA);rz.fill((255,90,90,170));pf.blit(rz,(TABLE_X+6,TABLE_Y+6+hh))
 pygame.draw.rect(pf,GOLD_DARK,(TABLE_X-5,TABLE_Y-5,TABLE_W+10,TABLE_H+10),4,border_radius=14);pygame.draw.rect(pf,GOLD,(TABLE_X-3,TABLE_Y-3,TABLE_W+6,TABLE_H+6),2,border_radius=12)
 pygame.draw.rect(pf,TABLE_EDGE,(TABLE_X,TABLE_Y,TABLE_W,TABLE_H),4,border_radius=10);pygame.draw.rect(pf,LINE_COLOR,(TABLE_X+6,TABLE_Y+6,TABLE_W-12,TABLE_H-12),2,border_radius=8)
 pygame.draw.line(pf,NET_COLOR,(TABLE_X+10,TABLE_CY),(TABLE_X+TABLE_W-10,TABLE_CY),3)
 for x in range(TABLE_X+18,TABLE_X+TABLE_W-12,18):pygame.draw.rect(pf,(180,180,180),(x,TABLE_CY-2,12,4),border_radius=2)
 pygame.draw.circle(pf,GOLD,(TABLE_CX,TABLE_CY),int(TABLE_W*0.20),3);pygame.draw.circle(pf,LINE_COLOR,(TABLE_CX,TABLE_CY),int(TABLE_W*0.20)-4,1);pygame.draw.circle(pf,GOLD,(TABLE_CX,TABLE_CY),6)
 pygame.draw.rect(pf,(20,20,30),(SLIDER_X-4,SLIDER_Y-4,SLIDER_W+8,SLIDER_H+8),border_radius=10);pygame.draw.rect(pf,SLIDER_BG,(SLIDER_X,SLIDER_Y,SLIDER_W,SLIDER_H),border_radius=6)
 hi=SMALL_FONT.render(T("slide_move"),True,(200,200,220));pf.blit(hi,((W-hi.get_width())//2,SLIDER_Y+SLIDER_H+KNOB_R+8))
 return pf
playfield=build_playfield()
def make_gear(r):
 sf=pygame.Surface((r*2+4,r*2+4),pygame.SRCALPHA);cx=r+2;cy=r+2
 for i in range(8):
  a=i*2*math.pi/8;x1=cx+math.cos(a)*r;y1=cy+math.sin(a)*r;pygame.draw.circle(sf,GOLD,(int(x1),int(y1)),max(3,r//3))
 pygame.draw.circle(sf,GOLD,(cx,cy),r);pygame.draw.circle(sf,(40,40,60),(cx,cy),int(r*0.5));pygame.draw.circle(sf,GOLD,(cx,cy),int(r*0.3))
 return sf
gear_surf=make_gear(GEAR_R)
def _decor_paddle(cd,cl):
 pw=int(W*0.20);ph=int(W*0.05);s=pygame.Surface((pw+6,ph+6),pygame.SRCALPHA);pygame.draw.rect(s,(0,0,0,100),(3,5,pw,ph),border_radius=8)
 g=vgrad(pw,ph,cl,cd);m=pygame.Surface((pw,ph),pygame.SRCALPHA);pygame.draw.rect(m,(255,255,255),(0,0,pw,ph),border_radius=8)
 g.blit(m,(0,0),special_flags=pygame.BLEND_RGBA_MIN);s.blit(g,(3,3));pygame.draw.rect(s,GOLD,(3,3,pw,ph),2,border_radius=8);return s
menu_bg=vgrad(W,H,(30,40,80),(10,15,30))
for i in range(-H,W+H,50):pygame.draw.line(menu_bg,(255,255,255,12),(i,0),(i+H,H),3)
random.seed(42)
for _ in range(50):
 sx=random.randint(0,W);sy=random.randint(0,H);srr=random.randint(2,5);a=random.randint(40,130)
 st=pygame.Surface((srr*2,srr*2),pygame.SRCALPHA);pygame.draw.circle(st,(255,255,255,a),(srr,srr),srr);menu_bg.blit(st,(sx-srr,sy-srr))
random.seed()
_pr=pygame.transform.rotate(_decor_paddle(PADDLE_P_DARK,PADDLE_P_LIGHT),-25);_pb=pygame.transform.rotate(_decor_paddle(PADDLE_B_DARK,PADDLE_B_LIGHT),25)
menu_bg.blit(_pr,(-int(W*0.04),int(H*0.01)));menu_bg.blit(_pb,(W-_pb.get_width()+int(W*0.04),int(H*0.01)))
def make_ball_surface(cn):
 c=BALL_COLORS.get(cn,(255,255,255));sf=pygame.Surface((BALL_R*2+6,BALL_R*2+6),pygame.SRCALPHA)
 pygame.draw.circle(sf,(0,0,0,100),(BALL_R+4,BALL_R+4),BALL_R);pygame.draw.circle(sf,c,(BALL_R+3,BALL_R+3),BALL_R)
 ed=(255,255,255) if cn=="BLACK" else (max(0,c[0]-60),max(0,c[1]-60),max(0,c[2]-60))
 pygame.draw.circle(sf,ed,(BALL_R+3,BALL_R+3),BALL_R,1);pygame.draw.circle(sf,(255,255,255),(BALL_R+3-BALL_R//3,BALL_R+3-BALL_R//3),max(2,BALL_R//3));return sf
def make_ball_trail(cn):
 c=BALL_COLORS.get(cn,(255,255,255));tr=[]
 for a in (90,55,25):
  s=pygame.Surface((BALL_R*2+4,BALL_R*2+4),pygame.SRCALPHA)
  pygame.draw.circle(s,(c[0],c[1],c[2],a),(BALL_R+2,BALL_R+2),BALL_R-1)
  tr.append(s)
 return tr
ball_surf=make_ball_surface(ball_color_name)
trail_surfs=make_ball_trail(ball_color_name)
def make_paddle(cd,cl,dt=True):
 s=pygame.Surface((PW+4,PH+4),pygame.SRCALPHA);pygame.draw.rect(s,(0,0,0,100),(2,4,PW,PH),border_radius=6)
 g=vgrad(PW,PH,cd,cl) if dt else vgrad(PW,PH,cl,cd)
 m=pygame.Surface((PW,PH),pygame.SRCALPHA);pygame.draw.rect(m,(255,255,255),(0,0,PW,PH),border_radius=6);g.blit(m,(0,0),special_flags=pygame.BLEND_RGBA_MIN);s.blit(g,(2,2))
 if dt:pygame.draw.rect(s,(255,255,255,90),(4,2+PH//2,PW-4,PH//2),border_radius=4)
 else:pygame.draw.rect(s,(255,255,255,90),(4,3,PW-4,PH//2),border_radius=4)
 pygame.draw.rect(s,GOLD,(2,2,PW,PH),2,border_radius=6);return s
paddle_p_surf=make_paddle(PADDLE_P_DARK,PADDLE_P_LIGHT,True);paddle_b_surf=make_paddle(PADDLE_B_DARK,PADDLE_B_LIGHT,False)
def draw_button(sf,r,lb,fn,base=(60,120,200),hover=False):
 c=(90,160,240) if hover else base;pygame.draw.rect(sf,c,r,border_radius=12);pygame.draw.rect(sf,GOLD,r,2,border_radius=12)
 tx=fn.render(lb,True,(255,255,255));sf.blit(tx,(r.centerx-tx.get_width()//2,r.centery-tx.get_height()//2))
def point_in(r,p):return r.collidepoint(p)
state="menu";player_name="";name_from_play=False;difficulty="NORMAL";player_x=TABLE_CX;bot_x=TABLE_CX;player_score=0;bot_score=0
ball_x=float(TABLE_CX);ball_y=float(TABLE_CY);ball_vx=0.0;ball_vy=0.0
base_ball_init=TABLE_H*0.012;base_ball_max=TABLE_H*0.024;base_accel=0.6;base_bot_speed=TABLE_W*0.013
BALL_SPEED_INIT=base_ball_init;BALL_SPEED_MAX=base_ball_max;BALL_ACCEL=base_accel;BOT_SPEED=base_bot_speed;ball_speed=BALL_SPEED_INIT
serving=True;serve_timer=0;rally=0;slider_val=0.5;dragging=False;vol_dragging=False;winner_text=""
match_start_ticks=0;end_ticks=0;left_mood="happy";right_mood="happy";mood_until=0;score_saved=False
pause_started_at=0;total_paused=0;pause_snapshot=None;new_record_until=0
rage_off=False;bot_aim_dir=0;bot_aim_offset=0;bot_aim_skip=False
ball_prev1=(TABLE_CX,TABLE_CY);ball_prev2=(TABLE_CX,TABLE_CY)
_csp=[None,-1];_csb=[None,-1];_ct=[None,-1];_cr=[None,-1]
def render_cached_score_p():
 if _csp[1]!=player_score:
  nm=(player_name or T("you"))[:8];_csp[0]=SCORE_FONT.render(nm+"  "+str(player_score),True,(255,140,140));_csp[1]=player_score
 return _csp[0]
def render_cached_score_b():
 if _csb[1]!=bot_score:
  _csb[0]=SCORE_FONT.render(T("bot")+"  "+str(bot_score),True,(140,160,255));_csb[1]=bot_score
 return _csb[0]
def render_cached_timer(e):
 if _ct[1]!=e:
  _ct[0]=TIMER_FONT.render("{:02d}:{:02d}".format(e//60,e%60),True,(255,220,100));_ct[1]=e
 return _ct[0]
def render_cached_rally():
 if _cr[1]!=rally:
  rd=rally if rally<10000 else 9999;_cr[0]=SMALL_FONT.render(T("rally")+": "+str(rd),True,(255,220,100));_cr[1]=rally
 return _cr[0]
def apply_difficulty():
 global BALL_SPEED_INIT,BALL_SPEED_MAX,BALL_ACCEL,BOT_SPEED
 d=DIFFICULTIES[difficulty];BALL_SPEED_INIT=base_ball_init*d["ball_init_mul"];BALL_SPEED_MAX=base_ball_max*d["ball_max_mul"];BALL_ACCEL=base_accel*d["accel_mul"];BOT_SPEED=base_bot_speed*d["bot_speed_mul"]
def reset_ball():
 global ball_x,ball_y,ball_vx,ball_vy,ball_speed,serving,serve_timer,rally,ball_prev1,ball_prev2
 ball_x=float(TABLE_CX);ball_y=float(TABLE_CY);ball_vx=0.0;ball_vy=0.0;ball_speed=BALL_SPEED_INIT;serving=True;serve_timer=pygame.time.get_ticks();rally=0
 ball_prev1=(ball_x,ball_y);ball_prev2=(ball_x,ball_y)
def launch_ball(d):
 global ball_vx,ball_vy,serving
 a=random.uniform(-0.5,0.5);ball_vx=ball_speed*math.sin(a);ball_vy=ball_speed*d*math.cos(a);serving=False
def clamp(v,lo,hi):return max(lo,min(hi,v))
def set_moods(l,r,du=2000):
 global left_mood,right_mood,mood_until
 left_mood=l;right_mood=r;mood_until=pygame.time.get_ticks()+du
def start_new_match():
 global player_score,bot_score,state,match_start_ticks,score_saved,total_paused,rage_off,bot_aim_dir
 player_score=0;bot_score=0;state="play";match_start_ticks=pygame.time.get_ticks();total_paused=0;score_saved=False;rage_off=False;bot_aim_dir=0;apply_difficulty();reset_ball()
def menu_buttons():
 bw=int(W*0.7);bh=int(H*0.05);cx=W//2;y0=int(H*0.28);gp=int(H*0.06);ks=["play","diff","mode","stats","name","ball","lang","sound","quit"]
 return {k:pygame.Rect(cx-bw//2,y0+gp*i,bw,bh) for i,k in enumerate(ks)}
def diff_buttons():
 bw=int(W*0.6);bh=int(H*0.07);cx=W//2;y0=int(H*0.30)
 return {"EASY":pygame.Rect(cx-bw//2,y0,bw,bh),"NORMAL":pygame.Rect(cx-bw//2,y0+int(H*0.10),bw,bh),"HARD":pygame.Rect(cx-bw//2,y0+int(H*0.20),bw,bh),"back":pygame.Rect(cx-bw//2,int(H*0.85),bw,bh)}
def lang_buttons():
 bw=int(W*0.6);bh=int(H*0.07);cx=W//2;y0=int(H*0.35)
 return {"EN":pygame.Rect(cx-bw//2,y0,bw,bh),"RU":pygame.Rect(cx-bw//2,y0+int(H*0.10),bw,bh),"back":pygame.Rect(cx-bw//2,int(H*0.85),bw,bh)}
def mode_buttons():
 bw=int(W*0.6);bh=int(H*0.07);cx=W//2;y0=int(H*0.35)
 return {"NORMAL":pygame.Rect(cx-bw//2,y0,bw,bh),"INFINITE":pygame.Rect(cx-bw//2,y0+int(H*0.10),bw,bh),"back":pygame.Rect(cx-bw//2,int(H*0.85),bw,bh)}
def stats_buttons():
 bw=int(W*0.6);bh=int(H*0.07);cx=W//2
 return {"reset":pygame.Rect(cx-bw//2,int(H*0.65),bw,bh),"back":pygame.Rect(cx-bw//2,int(H*0.85),bw,bh)}
def confirm_buttons():
 bw=int(W*0.35);bh=int(H*0.07);cx=W//2;y=int(H*0.55)
 return {"yes":pygame.Rect(cx-bw-8,y,bw,bh),"no":pygame.Rect(cx+8,y,bw,bh)}
def name_buttons():
 bw=int(W*0.4);bh=int(H*0.06);cx=W//2;y=int(H*0.27)
 return {"ok":pygame.Rect(cx-bw-8,y,bw,bh),"back":pygame.Rect(cx+8,y,bw,bh)}
def ball_buttons():
 cw=int(W*0.22);ch=cw;cx=W//2;y0=int(H*0.20);rs={}
 for i,n in enumerate(BALL_COLOR_ORDER):
  cl=i%3;rw=i//3;x=cx-cw*3//2-8+cl*(cw+8);y=y0+rw*(ch+12);rs[n]=pygame.Rect(x,y,cw,ch)
 rs["back"]=pygame.Rect(cx-int(W*0.3),int(H*0.85),int(W*0.6),int(H*0.07));return rs
def pause_layout():
 pw=int(W*0.85);ph=int(H*0.55);pn=pygame.Rect((W-pw)//2,(H-ph)//2,pw,ph)
 vt=pygame.Rect(pn.x+30,pn.y+int(ph*0.30),pn.width-60,max(10,int(H*0.022)))
 bw=pn.width-60;bh=int(H*0.06)
 bs={"resume":pygame.Rect(pn.x+30,pn.y+int(ph*0.55),bw,bh),"end":pygame.Rect(pn.x+30,pn.y+int(ph*0.70),bw,bh),"menu":pygame.Rect(pn.x+30,pn.y+int(ph*0.85),bw,bh)}
 return pn,vt,bs
KB_ROWS=["ABCDEFGHIJ","KLMNOPQRST","UVWXYZ","0123456789"]
def keyboard_layout():
 kw=int(W*0.082);kh=int(H*0.045);sy=int(H*0.36);rs=[]
 for ri,row in enumerate(KB_ROWS):
  rww=len(row)*(kw+4);x=W//2-rww//2
  for ch in row:
   rs.append((ch,pygame.Rect(x,sy+ri*(kh+5),kw,kh)));x+=kw+4
 bw=int(W*0.30);bh=int(H*0.05);by=sy+len(KB_ROWS)*(kh+5)+8
 return rs,pygame.Rect(W//2-bw-4,by,bw,bh),pygame.Rect(W//2+4,by,bw,bh)
def draw_menu(mp):
 screen.blit(menu_bg,(0,0));bc=BALL_COLORS.get(ball_color_name,(255,255,255))
 pygame.draw.circle(screen,(0,0,0),(W//2+2,int(H*0.13)+3),int(H*0.05));pygame.draw.circle(screen,bc,(W//2,int(H*0.13)),int(H*0.05));pygame.draw.circle(screen,GOLD,(W//2,int(H*0.13)),int(H*0.05),3)
 t2=HUGE_FONT.render(T("title"),True,GOLD);screen.blit(t2,(W//2-t2.get_width()//2+2,int(H*0.03)+2))
 t2b=HUGE_FONT.render(T("title"),True,(255,240,100));screen.blit(t2b,(W//2-t2b.get_width()//2,int(H*0.03)))
 sb=TITLE_FONT.render(T("subtitle"),True,(220,220,240));screen.blit(sb,(W//2-sb.get_width()//2,int(H*0.20)))
 stt=SMALL_FONT.render(T("wins")+": "+str(wins_total)+"   "+T("best")+": "+str(best_score),True,(255,220,100));screen.blit(stt,(W//2-stt.get_width()//2,int(H*0.245)))
 bs=menu_buttons()
 draw_button(screen,bs["play"],T("play"),BTN_FONT,(40,160,80),point_in(bs["play"],mp))
 draw_button(screen,bs["diff"],T("difficulty")+": "+T(difficulty.lower()),BTN_FONT,(60,120,200),point_in(bs["diff"],mp))
 draw_button(screen,bs["mode"],T("mode")+": "+T("mode_"+game_mode.lower()),BTN_FONT,(120,80,180),point_in(bs["mode"],mp))
 draw_button(screen,bs["stats"],T("stats"),BTN_FONT,(60,120,200),point_in(bs["stats"],mp))
 draw_button(screen,bs["name"],T("name")+": "+(player_name or T("set_name")),BTN_FONT,(60,120,200),point_in(bs["name"],mp))
 draw_button(screen,bs["ball"],T("ball")+": "+ball_color_name,BTN_FONT,(180,100,60),point_in(bs["ball"],mp))
 ll=T("english") if language=="EN" else T("russian")
 draw_button(screen,bs["lang"],T("language")+": "+ll,BTN_FONT,(120,80,180),point_in(bs["lang"],mp))
 sl=T("on") if sound_enabled else T("off");sc=(80,120,80) if sound_enabled else (120,80,80)
 draw_button(screen,bs["sound"],T("sound")+": "+sl,BTN_FONT,sc,point_in(bs["sound"],mp))
 draw_button(screen,bs["quit"],T("quit"),BTN_FONT,(160,60,60),point_in(bs["quit"],mp))
def draw_diff(mp):
 screen.blit(menu_bg,(0,0));t=BIG_FONT.render(T("difficulty"),True,GOLD);screen.blit(t,(W//2-t.get_width()//2,int(H*0.15)));bs=diff_buttons()
 for d in ("EASY","NORMAL","HARD"):
  bse=(40,160,80) if d=="EASY" else (60,120,200) if d=="NORMAL" else (200,80,60)
  if d==difficulty:bse=(255,200,50)
  draw_button(screen,bs[d],T(d.lower()),BTN_FONT,bse,point_in(bs[d],mp))
 draw_button(screen,bs["back"],T("back"),BTN_FONT,(90,140,180),point_in(bs["back"],mp))
def draw_mode(mp):
 screen.blit(menu_bg,(0,0));t=BIG_FONT.render(T("mode"),True,GOLD);screen.blit(t,(W//2-t.get_width()//2,int(H*0.18)));bs=mode_buttons()
 for m in ("NORMAL","INFINITE"):
  bse=(255,200,50) if game_mode==m else ((60,120,200) if m=="NORMAL" else (180,80,180))
  draw_button(screen,bs[m],T("mode_"+m.lower()),BTN_FONT,bse,point_in(bs[m],mp))
 draw_button(screen,bs["back"],T("back"),BTN_FONT,(90,140,180),point_in(bs["back"],mp))
def draw_lang(mp):
 screen.blit(menu_bg,(0,0));t=BIG_FONT.render(T("language"),True,GOLD);screen.blit(t,(W//2-t.get_width()//2,int(H*0.18)));bs=lang_buttons()
 for cd,lk in (("EN","english"),("RU","russian")):
  bse=(255,200,50) if language==cd else (60,120,200);draw_button(screen,bs[cd],T(lk),BTN_FONT,bse,point_in(bs[cd],mp))
 draw_button(screen,bs["back"],T("back"),BTN_FONT,(90,140,180),point_in(bs["back"],mp))
def draw_ball_picker(mp):
 screen.blit(menu_bg,(0,0));t=BIG_FONT.render(T("ball"),True,GOLD);screen.blit(t,(W//2-t.get_width()//2,int(H*0.08)));rs=ball_buttons()
 for n in BALL_COLOR_ORDER:
  r=rs[n];pygame.draw.rect(screen,(30,30,50),r,border_radius=10)
  if n==ball_color_name:pygame.draw.rect(screen,GOLD,r,3,border_radius=10)
  else:pygame.draw.rect(screen,(90,90,120),r,1,border_radius=10)
  cx=r.centerx;cy=r.centery-int(H*0.01);cl=BALL_COLORS[n];rd=int(min(r.width,r.height)*0.30)
  pygame.draw.circle(screen,(0,0,0),(cx+2,cy+3),rd);pygame.draw.circle(screen,cl,(cx,cy),rd)
  ed=(255,255,255) if n=="BLACK" else (max(0,cl[0]-60),max(0,cl[1]-60),max(0,cl[2]-60));pygame.draw.circle(screen,ed,(cx,cy),rd,2)
  lb=SMALL_FONT.render(n,True,(220,220,240));screen.blit(lb,(cx-lb.get_width()//2,r.bottom-lb.get_height()-6))
 draw_button(screen,rs["back"],T("back"),BTN_FONT,(90,140,180),point_in(rs["back"],mp))
def draw_stats(mp):
 screen.blit(menu_bg,(0,0));t=BIG_FONT.render(T("stats"),True,GOLD);screen.blit(t,(W//2-t.get_width()//2,int(H*0.08)))
 bx=pygame.Rect(int(W*0.10),int(H*0.22),int(W*0.80),int(H*0.30));pygame.draw.rect(screen,(20,25,45),bx,border_radius=12);pygame.draw.rect(screen,GOLD,bx,2,border_radius=12)
 lf=BIG_FONT.render(T("wins")+":",True,(220,220,240));vf=BIG_FONT.render(str(wins_total),True,(255,220,100))
 screen.blit(lf,(bx.x+24,bx.y+24));screen.blit(vf,(bx.right-vf.get_width()-24,bx.y+24))
 bv=str(best_score) if best_score>=MAX_SCORE+1 else str(best_score)+"/"+str(MAX_SCORE)
 lf2=BIG_FONT.render(T("best")+":",True,(220,220,240));vf2=BIG_FONT.render(bv,True,(255,220,100))
 screen.blit(lf2,(bx.x+24,bx.y+int(H*0.13)));screen.blit(vf2,(bx.right-vf2.get_width()-24,bx.y+int(H*0.13)))
 bs=stats_buttons()
 draw_button(screen,bs["reset"],T("reset"),BTN_FONT,(160,60,60),point_in(bs["reset"],mp))
 draw_button(screen,bs["back"],T("back"),BTN_FONT,(90,140,180),point_in(bs["back"],mp))
def draw_confirm_reset(mp):
 screen.blit(menu_bg,(0,0));t=BIG_FONT.render(T("reset_q"),True,GOLD);screen.blit(t,(W//2-t.get_width()//2,int(H*0.30)));bs=confirm_buttons()
 draw_button(screen,bs["yes"],T("yes"),BTN_FONT,(160,60,60),point_in(bs["yes"],mp))
 draw_button(screen,bs["no"],T("no"),BTN_FONT,(60,120,200),point_in(bs["no"],mp))
def draw_name_input(mp):
 screen.blit(menu_bg,(0,0));t=BIG_FONT.render(T("enter_name"),True,GOLD);screen.blit(t,(W//2-t.get_width()//2,int(H*0.04)))
 ru=SMALL_FONT.render(T("name_rules"),True,(220,220,240));screen.blit(ru,(W//2-ru.get_width()//2,int(H*0.11)))
 bw=int(W*0.7);bh2=int(H*0.085);bx=pygame.Rect(W//2-bw//2,int(H*0.16),bw,bh2)
 pygame.draw.rect(screen,(20,25,45),bx,border_radius=10);pygame.draw.rect(screen,GOLD,bx,2,border_radius=10)
 cu="_" if (pygame.time.get_ticks()//500)%2==0 else " ";tx=INPUT_FONT.render(player_name+cu,True,(255,255,255));screen.blit(tx,(bx.centerx-tx.get_width()//2,bx.centery-tx.get_height()//2))
 bs=name_buttons();ok=len(player_name)>0;okb=(40,160,80) if ok else (60,80,60)
 draw_button(screen,bs["ok"],T("ok"),BTN_FONT,okb,point_in(bs["ok"],mp) and ok);draw_button(screen,bs["back"],T("back"),BTN_FONT,(90,140,180),point_in(bs["back"],mp))
 rs,br,cr2=keyboard_layout()
 for ch,r in rs:
  hv=point_in(r,mp);pygame.draw.rect(screen,(90,120,200) if hv else (60,80,130),r,border_radius=6);pygame.draw.rect(screen,GOLD,r,1,border_radius=6)
  kt=KEY_FONT.render(ch,True,(255,255,255));screen.blit(kt,(r.centerx-kt.get_width()//2,r.centery-kt.get_height()//2))
 pygame.draw.rect(screen,(60,120,200),br,border_radius=6);pygame.draw.rect(screen,GOLD,br,1,border_radius=6)
 bt2=KEY_FONT.render(T("del"),True,(255,255,255));screen.blit(bt2,(br.centerx-bt2.get_width()//2,br.centery-bt2.get_height()//2))
 pygame.draw.rect(screen,(180,60,60),cr2,border_radius=6);pygame.draw.rect(screen,GOLD,cr2,1,border_radius=6)
 ct2=KEY_FONT.render(T("clear"),True,(255,255,255));screen.blit(ct2,(cr2.centerx-ct2.get_width()//2,cr2.centery-ct2.get_height()//2))
 return rs,br,cr2,bs
def draw_game():
 screen.blit(playfield,(0,0));tm=pygame.time.get_ticks()/500.0
 for f in crowd_rows:
  bb=int(math.sin(tm+f["phase"])*4);md=left_mood if f["side"]=="L" else right_mood;screen.blit(f[md],(f["x"]-fan_w//2,f["y"]+bb-fan_h//2))
 sw=int(W*0.90)//3;sx=int(W*0.05);ic=HEADER_INFO_Y+HEADER_INFO_H//2
 bt=render_cached_score_b();screen.blit(bt,(sx+sw//2-bt.get_width()//2,ic-bt.get_height()//2))
 if state=="play":el=(pygame.time.get_ticks()-match_start_ticks-total_paused)//1000
 else:el=(end_ticks-match_start_ticks-total_paused)//1000
 tt=render_cached_timer(el);screen.blit(tt,(sx+sw+sw//2-tt.get_width()//2,ic-tt.get_height()//2))
 pt=render_cached_score_p();screen.blit(pt,(sx+2*sw+sw//2-pt.get_width()//2,ic-pt.get_height()//2))
 if rally>2 and not serving:
  rt=render_cached_rally();screen.blit(rt,((W-rt.get_width())//2,TABLE_Y+TABLE_H+5))
 ra=(player_score-bot_score)>=3 and not rage_off and state=="play"
 if ra:
  fl=(pygame.time.get_ticks()//250)%2==0;rc=(255,80,60) if fl else (255,200,80);rt2=SMALL_FONT.render(T("rage"),True,rc);screen.blit(rt2,((W-rt2.get_width())//2,TABLE_Y-rt2.get_height()-4))
 if pygame.time.get_ticks()<new_record_until:
  nrt=BIG_FONT.render(T("new_record"),True,(255,220,100));screen.blit(nrt,((W-nrt.get_width())//2,TABLE_CY-nrt.get_height()//2))
 by=TABLE_Y+int(TABLE_H*0.06);py=TABLE_Y+TABLE_H-int(TABLE_H*0.06)
 screen.blit(paddle_b_surf,(round(bot_x)-PW//2-2,by-PH//2-2));screen.blit(paddle_p_surf,(round(player_x)-PW//2-2,py-PH//2-2))
 if not serving:
  for i,(px,py2) in enumerate((ball_prev2,ball_prev1)):
   ts=trail_surfs[2-i] if i==0 else trail_surfs[1]
   screen.blit(ts,(round(px)-BALL_R-2,round(py2)-BALL_R-2))
  screen.blit(ball_surf,(round(ball_x)-BALL_R-3,round(ball_y)-BALL_R-3))
 elif state=="play" and (pygame.time.get_ticks()//250)%2==0:screen.blit(ball_surf,(round(ball_x)-BALL_R-3,round(ball_y)-BALL_R-3))
 fw=int(slider_val*SLIDER_W);pygame.draw.rect(screen,SLIDER_FILL,(SLIDER_X,SLIDER_Y,fw,SLIDER_H),border_radius=6)
 kx=SLIDER_X+fw;kc=SLIDER_Y+SLIDER_H//2
 bcc=BALL_COLORS.get(ball_color_name,(240,240,245));ed2=(255,255,255) if ball_color_name=="BLACK" else (max(0,bcc[0]-60),max(0,bcc[1]-60),max(0,bcc[2]-60))
 pygame.draw.circle(screen,bcc,(kx,kc),KNOB_R);pygame.draw.circle(screen,GOLD,(kx,kc),KNOB_R,2);pygame.draw.circle(screen,ed2,(kx,kc),KNOB_R-3,1)
 screen.blit(gear_surf,(GEAR_RECT.x-2,GEAR_RECT.y-2))
 if state=="over":
  ov=pygame.Surface((W,H//3));ov.fill((20,20,40));ov.set_alpha(230);screen.blit(ov,(0,H//2-H//6));pygame.draw.rect(screen,GOLD,(0,H//2-H//6,W,H//3),3)
  wt=BIG_FONT.render(winner_text,True,GOLD);screen.blit(wt,((W-wt.get_width())//2,H//2-int(H*0.08)))
  sct=SCORE_FONT.render(str(player_score)+" - "+str(bot_score),True,(220,220,220));screen.blit(sct,((W-sct.get_width())//2,H//2))
  tp=SMALL_FONT.render(T("tap_menu"),True,(200,200,200));screen.blit(tp,((W-tp.get_width())//2,H//2+int(H*0.05)))
def draw_pause(mp):
 if pause_snapshot is not None:screen.blit(pause_snapshot,(0,0))
 else:draw_game()
 pn,vt,bs=pause_layout();pygame.draw.rect(screen,(25,30,55),pn,border_radius=14);pygame.draw.rect(screen,GOLD,pn,2,border_radius=14)
 t=BIG_FONT.render(T("paused"),True,GOLD);screen.blit(t,(pn.centerx-t.get_width()//2,pn.y+20))
 vl=SMALL_FONT.render(T("volume")+": "+str(int(master_volume*100))+"%",True,(220,220,240));screen.blit(vl,(vt.x,vt.y-28))
 pygame.draw.rect(screen,SLIDER_BG,vt,border_radius=6);fw=int(master_volume*vt.width);pygame.draw.rect(screen,(60,160,220),(vt.x,vt.y,fw,vt.height),border_radius=6)
 kx=vt.x+fw;kc=vt.y+vt.height//2;pygame.draw.circle(screen,SLIDER_KNOB,(kx,kc),KNOB_R);pygame.draw.circle(screen,GOLD,(kx,kc),KNOB_R,2)
 draw_button(screen,bs["resume"],T("resume"),BTN_FONT,(40,160,80),point_in(bs["resume"],mp))
 draw_button(screen,bs["end"],T("end"),BTN_FONT,(200,140,40),point_in(bs["end"],mp))
 draw_button(screen,bs["menu"],T("quit_to_menu"),BTN_FONT,(160,60,60),point_in(bs["menu"],mp))
def enter_pause():
 global state,pause_started_at,pause_snapshot
 draw_game();sn=screen.copy();ov=pygame.Surface((W,H),pygame.SRCALPHA);ov.fill((0,0,0,160));sn.blit(ov,(0,0));pause_snapshot=sn;state="pause";pause_started_at=pygame.time.get_ticks()
async def main():
 global state,player_name,name_from_play,difficulty,player_x,bot_x,player_score,bot_score,ball_x,ball_y,ball_vx,ball_vy,ball_speed,serving,serve_timer,rally,slider_val,dragging,vol_dragging,winner_text,match_start_ticks,end_ticks,left_mood,right_mood,mood_until,score_saved,pause_started_at,total_paused,pause_snapshot,new_record_until,rage_off,bot_aim_dir,bot_aim_offset,bot_aim_skip,ball_prev1,ball_prev2,sound_enabled,language,ball_color_name,ball_surf,trail_surfs,master_volume,wins_total,best_score,playfield,game_mode
 running=True
 while running:
  clock.tick(60);now=pygame.time.get_ticks();mp=pygame.mouse.get_pos()
  if state=="play" and now>mood_until:left_mood="happy";right_mood="happy"
  events=pygame.event.get()
  for e in events:
   if e.type==pygame.QUIT:running=False
   elif e.type==pygame.KEYDOWN and e.key==pygame.K_ESCAPE:
    if state=="play":enter_pause()
    elif state=="pause":total_paused+=now-pause_started_at;state="play";pause_snapshot=None
    elif state=="name_input":state="menu"
    else:running=False
  if state=="menu":
   for e in events:
    if e.type==pygame.MOUSEBUTTONDOWN:
     bs=menu_buttons()
     if point_in(bs["play"],e.pos):
      play_sound("click")
      if not player_name:name_from_play=True;state="name_input"
      else:start_new_match()
     elif point_in(bs["diff"],e.pos):play_sound("click");state="difficulty"
     elif point_in(bs["mode"],e.pos):play_sound("click");state="mode"
     elif point_in(bs["stats"],e.pos):play_sound("click");state="stats"
     elif point_in(bs["name"],e.pos):play_sound("click");name_from_play=False;state="name_input"
     elif point_in(bs["ball"],e.pos):play_sound("click");state="ball_picker"
     elif point_in(bs["lang"],e.pos):play_sound("click");state="language"
     elif point_in(bs["sound"],e.pos):
      sound_enabled=not sound_enabled
      if sound_enabled:init_mixer()
      save_settings()
     elif point_in(bs["quit"],e.pos):running=False
   draw_menu(mp)
  elif state=="difficulty":
   for e in events:
    if e.type==pygame.MOUSEBUTTONDOWN:
     bs=diff_buttons()
     for d in ("EASY","NORMAL","HARD"):
      if point_in(bs[d],e.pos):difficulty=d;play_sound("click")
     if point_in(bs["back"],e.pos):play_sound("click");state="menu"
   draw_diff(mp)
  elif state=="mode":
   for e in events:
    if e.type==pygame.MOUSEBUTTONDOWN:
     bs=mode_buttons()
     for m in ("NORMAL","INFINITE"):
      if point_in(bs[m],e.pos):game_mode=m;save_settings();play_sound("click")
     if point_in(bs["back"],e.pos):play_sound("click");state="menu"
   draw_mode(mp)
  elif state=="language":
   for e in events:
    if e.type==pygame.MOUSEBUTTONDOWN:
     bs=lang_buttons()
     if point_in(bs["EN"],e.pos):language="EN";save_settings();playfield=build_playfield();play_sound("click")
     elif point_in(bs["RU"],e.pos):language="RU";save_settings();playfield=build_playfield();play_sound("click")
     elif point_in(bs["back"],e.pos):play_sound("click");state="menu"
   draw_lang(mp)
  elif state=="ball_picker":
   for e in events:
    if e.type==pygame.MOUSEBUTTONDOWN:
     rs=ball_buttons()
     for n in BALL_COLOR_ORDER:
      if point_in(rs[n],e.pos):ball_color_name=n;ball_surf=make_ball_surface(ball_color_name);trail_surfs=make_ball_trail(ball_color_name);save_settings();play_sound("click")
     if point_in(rs["back"],e.pos):play_sound("click");state="menu"
   draw_ball_picker(mp)
  elif state=="stats":
   for e in events:
    if e.type==pygame.MOUSEBUTTONDOWN:
     bs=stats_buttons()
     if point_in(bs["reset"],e.pos):play_sound("click");state="confirm_reset"
     elif point_in(bs["back"],e.pos):play_sound("click");state="menu"
   draw_stats(mp)
  elif state=="confirm_reset":
   for e in events:
    if e.type==pygame.MOUSEBUTTONDOWN:
     bs=confirm_buttons()
     if point_in(bs["yes"],e.pos):wins_total=0;best_score=0;save_settings();play_sound("click");state="stats"
     elif point_in(bs["no"],e.pos):play_sound("click");state="stats"
   draw_confirm_reset(mp)
  elif state=="name_input":
   kbr,bsr,clr,nb=draw_name_input(mp)
   for e in events:
    if e.type==pygame.MOUSEBUTTONDOWN:
     h=False
     if point_in(nb["ok"],e.pos) and player_name:
      play_sound("click")
      if name_from_play:name_from_play=False;start_new_match()
      else:state="menu"
      h=True
     elif point_in(nb["back"],e.pos):play_sound("click");name_from_play=False;state="menu";h=True
     if not h:
      for ch,r in kbr:
       if point_in(r,e.pos):
        if len(player_name)<NAME_MAX:player_name+=ch;play_sound("click")
        h=True;break
     if not h:
      if point_in(bsr,e.pos):player_name=player_name[:-1];play_sound("click")
      elif point_in(clr,e.pos):player_name="";play_sound("click")
    elif e.type==pygame.KEYDOWN:
     if e.key==pygame.K_BACKSPACE:player_name=player_name[:-1]
     elif e.key==pygame.K_RETURN and player_name:state="menu"
     else:
      ch=e.unicode
      if ch and ch in NAME_ALLOWED and len(player_name)<NAME_MAX:player_name+=ch
  elif state=="play" or state=="over":
   for e in events:
    if state=="play":
     if e.type==pygame.MOUSEBUTTONDOWN:
      if point_in(GEAR_RECT.inflate(20,20),e.pos):enter_pause();continue
      mx,my=e.pos;kc=SLIDER_Y+SLIDER_H//2
      if abs(my-kc)<KNOB_R*3 and SLIDER_X-KNOB_R<=mx<=SLIDER_X+SLIDER_W+KNOB_R:dragging=True;slider_val=clamp((mx-SLIDER_X)/SLIDER_W,0.0,1.0)
     elif e.type==pygame.MOUSEBUTTONUP:dragging=False
     elif e.type==pygame.MOUSEMOTION and dragging:slider_val=clamp((e.pos[0]-SLIDER_X)/SLIDER_W,0.0,1.0)
    elif state=="over":
     if e.type==pygame.MOUSEBUTTONDOWN:state="menu"
   if state=="play":
    player_x=TABLE_X+PW//2+int(slider_val*(TABLE_W-PW))
    if serving:
     if now-serve_timer>700:launch_ball(1 if random.random()>0.5 else -1)
    else:
     ball_prev2=ball_prev1;ball_prev1=(ball_x,ball_y)
     ball_x+=ball_vx;ball_y+=ball_vy
     if ball_x-BALL_R<TABLE_X:ball_x=TABLE_X+BALL_R;ball_vx=-ball_vx;play_sound("wall")
     elif ball_x+BALL_R>TABLE_X+TABLE_W:ball_x=TABLE_X+TABLE_W-BALL_R;ball_vx=-ball_vx;play_sound("wall")
     pcy=TABLE_Y+TABLE_H-int(TABLE_H*0.06)
     if ball_vy>0 and ball_y+BALL_R>=pcy-PH//2 and ball_y-BALL_R<=pcy+PH//2:
      if abs(ball_x-player_x)<PW//2+BALL_R:
       ball_y=pcy-PH//2-BALL_R;of=(ball_x-player_x)/(PW/2);ball_vx=ball_speed*of*0.8;ball_vy=-abs(ball_vy);rally+=1
       ball_speed=min(BALL_SPEED_MAX,BALL_SPEED_INIT+rally*BALL_ACCEL);sp=math.hypot(ball_vx,ball_vy)
       if sp>0:ball_vx=ball_vx/sp*ball_speed;ball_vy=ball_vy/sp*ball_speed
       play_sound("paddle");set_moods("wow","happy",1200)
     bcy=TABLE_Y+int(TABLE_H*0.06)
     rg=(player_score-bot_score)>=3 and not rage_off
     if rg:
      sm=1.05
      if ball_vy<0 and ball_vy!=0:
       if bot_aim_dir!=-1:
        bot_aim_dir=-1;bot_aim_offset=random.uniform(-PW*0.85,PW*0.85);bot_aim_skip=random.random()<0.5
       if bot_aim_skip:tg=ball_x
       else:
        tt2=max(0,(ball_y-bcy)/-ball_vy);tg=ball_x+ball_vx*tt2+bot_aim_offset
      else:
       bot_aim_dir=1;tg=ball_x
     else:
      bot_aim_dir=0;sm=1.0;tg=ball_x if ball_vy<0 else TABLE_CX
     df=tg-bot_x;bot_x+=clamp(df,-BOT_SPEED*sm,BOT_SPEED*sm);bot_x=clamp(bot_x,TABLE_X+PW//2,TABLE_X+TABLE_W-PW//2)
     if ball_vy<0 and ball_y-BALL_R<=bcy+PH//2 and ball_y+BALL_R>=bcy-PH//2:
      if abs(ball_x-bot_x)<PW//2+BALL_R:
       ball_y=bcy+PH//2+BALL_R;of=(ball_x-bot_x)/(PW/2);ball_vx=ball_speed*of*0.8;ball_vy=abs(ball_vy);rally+=1
       ball_speed=min(BALL_SPEED_MAX,BALL_SPEED_INIT+rally*BALL_ACCEL);sp=math.hypot(ball_vx,ball_vy)
       if sp>0:ball_vx=ball_vx/sp*ball_speed;ball_vy=ball_vy/sp*ball_speed
       play_sound("paddle");set_moods("happy","wow",1200)
     if ball_y<TABLE_Y-BALL_R*3:
      player_score+=1;play_sound("score");set_moods("wow","sad",1800);rage_off=False
      if update_record(player_score):new_record_until=now+1500
      if game_mode=="NORMAL" and player_score>=MAX_SCORE:
       state="over";winner_text=T("you_win");end_ticks=now;play_sound("win")
       if not score_saved:
        wins_total=wins_total+1;save_settings();score_saved=True
      else:reset_ball()
     elif ball_y>TABLE_Y+TABLE_H+BALL_R*3:
      bot_score+=1;play_sound("score");set_moods("sad","wow",1800);rage_off=True
      if game_mode=="NORMAL" and bot_score>=MAX_SCORE:
       state="over";winner_text=T("bot_win");end_ticks=now;play_sound("win")
       if not score_saved:
        if update_record(player_score):new_record_until=now+1500
        score_saved=True
      else:reset_ball()
   draw_game()
  elif state=="pause":
   pn,vt,bs=pause_layout()
   for e in events:
    if e.type==pygame.MOUSEBUTTONDOWN:
     mx,my=e.pos
     if point_in(bs["resume"],e.pos):play_sound("click");total_paused+=now-pause_started_at;state="play";pause_snapshot=None;vol_dragging=False
     elif point_in(bs["end"],e.pos):
      play_sound("click");end_ticks=now
      if not score_saved:
       if update_record(player_score):new_record_until=now+1500
       score_saved=True
      state="menu";pause_snapshot=None;vol_dragging=False
     elif point_in(bs["menu"],e.pos):play_sound("click");state="menu";pause_snapshot=None;vol_dragging=False
     else:
      kc=vt.y+vt.height//2
      if abs(my-kc)<=KNOB_R+4 and vt.x-KNOB_R<=mx<=vt.x+vt.width+KNOB_R:vol_dragging=True;master_volume=clamp((mx-vt.x)/vt.width,0.0,1.0)
    elif e.type==pygame.MOUSEBUTTONUP:
     if vol_dragging:vol_dragging=False;apply_volume();save_settings()
    elif e.type==pygame.MOUSEMOTION and vol_dragging:master_volume=clamp((e.pos[0]-vt.x)/vt.width,0.0,1.0)
   draw_pause(mp)
  pygame.display.flip()
  await asyncio.sleep(0)
 pygame.quit()
asyncio.run(main())
