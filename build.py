from pathlib import Path
import json,base64,html,math,shutil
ROOT=Path(__file__).resolve().parent;(ROOT/'screens').mkdir(exist_ok=True);(ROOT/'assets').mkdir(exist_ok=True);(ROOT/'figma-plugin').mkdir(exist_ok=True)
if not (ROOT/'assets/hero.png').exists():raise FileNotFoundError('assets/hero.png is required')
HERO=base64.b64encode((ROOT/'assets/hero.png').read_bytes()).decode()
BG='#FAF8F5';WHITE='#FFFFFF';INK='#23211F';MUTED='#77736E';LINE='#E5DFD7';WINE='#681E30';PALE='#F0EAE4';GREEN='#426F50'
PAGES=[('home','Главная'),('catalog','Каталог часов'),('men','Мужские часы'),('women','Женские часы'),('unisex','Унисекс'),('brands','Все бренды'),('brand','Коллекция бренда'),('product','Карточка товара'),('search','Результаты поиска'),('favorites','Избранное'),('compare','Сравнение'),('cart','Корзина'),('checkout','Оформление заказа'),('success','Заказ оформлен'),('login','Вход'),('register','Регистрация'),('reset','Восстановление пароля'),('account','Личный кабинет'),('profile','Мои данные'),('orders','История заказов'),('order','Детали заказа'),('addresses','Адреса доставки'),('loyalty','Бонусная программа'),('stores','Наши магазины'),('store','Страница магазина'),('service','Сервис и ремонт'),('service-request','Заявка в сервис'),('delivery','Доставка'),('payment','Оплата'),('returns','Возврат и обмен'),('warranty','Гарантия'),('about','О Big Ben'),('news','Журнал и новости'),('article','Статья'),('contacts','Контакты'),('faq','Вопросы и ответы'),('privacy','Политика конфиденциальности'),('terms','Условия продажи'),('consent','Согласие на обработку данных'),('404','Страница не найдена'),('empty','Пустая корзина'),('ui','Состояния интерфейса')]
ALL=[]
def esc(s):return html.escape(str(s),quote=True)
class Canvas:
 def __init__(self,slug,title,mobile):
  self.slug,self.title,self.mobile=slug,title,mobile;self.w=390 if mobile else 1440;self.pad=20 if mobile else 80;self.cw=self.w-self.pad*2;self.nodes=[];self.parts=[];self.y=0
 def r(self,x,y,w,h,fill=WHITE,r=0,stroke=None):
  n=dict(type='rect',x=x,y=y,w=w,h=h,fill=fill,r=r);n.update({'stroke':stroke} if stroke else {});self.nodes.append(n);self.parts.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" fill="{fill}"'+(f' stroke="{stroke}"' if stroke else '')+'/>')
 def t(self,x,y,text,size=16,fill=INK,weight=400,serif=False):
  self.nodes.append(dict(type='text',x=x,y=y,text=str(text),size=size,fill=fill,weight=weight,serif=serif));self.parts.append(f'<text x="{x}" y="{y+size*.86}" font-size="{size}" fill="{fill}" font-weight="{weight}" font-family="{("Georgia, serif" if serif else "Inter, Arial, sans-serif")}">{esc(text)}</text>')
 def line(self,x,y,w):self.r(x,y,w,1,LINE)
 def svg(self,x,y,w,h,content,label='Иконка'):
  raw=f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">{content}</svg>';self.nodes.append(dict(type='svg',x=x,y=y,w=w,h=h,svg=raw,name=label));self.parts.append(f'<g transform="translate({x} {y})">{content}</g>')
 def photo(self,x,y,w,h):
  self.nodes.append(dict(type='image',x=x,y=y,w=w,h=h,asset='hero'));self.parts.append(f'<image x="{x}" y="{y}" width="{w}" height="{h}" preserveAspectRatio="xMidYMid slice" href="data:image/png;base64,{HERO}"/>')
 def icon(self,x,y,name,color=INK):
  paths={'heart':'M12 21C7 17 2 13 2 8a5 5 0 0 1 10-2 5 5 0 0 1 10 2c0 5-5 9-10 13Z','search':'M10 18a8 8 0 1 1 0-16 8 8 0 0 1 0 16Zm6-2 6 6','bag':'M4 7h16l1 15H3L4 7Zm4 0V5a4 4 0 0 1 8 0v2','menu':'M2 5h20M2 12h20M2 19h20','user':'M12 12a5 5 0 1 0 0-10 5 5 0 0 0 0 10ZM3 23a9 9 0 0 1 18 0','arrow':'M3 12h18M15 6l6 6-6 6','check':'m5 12 4 4L20 5','pin':'M12 23S3 14 3 9a9 9 0 1 1 18 0c0 5-9 14-9 14Zm0-10a4 4 0 1 0 0-8 4 4 0 0 0 0 8Z','x':'M5 5l14 14M19 5 5 19'}
  self.svg(x,y,24,24,f'<path d="{paths.get(name,paths["arrow"])}" fill="none" stroke="{color}" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>',name)
 def wrap(self,x,y,text,width=None,size=16,fill=MUTED,maxchars=None):
  width=width or self.cw;chars=maxchars or max(8,int(width/(size*.54)));words=str(text).split();line='';lines=[]
  for word in words:
   if len(line+' '+word)>chars and line:lines.append(line);line=word
   else:line=(line+' '+word).strip()
  if line:lines.append(line)
  for i,line in enumerate(lines):self.t(x,y+i*size*1.55,line,size,fill)
  return len(lines)*size*1.55
 def button(self,x,y,label,w=190,outline=False):
  self.r(x,y,w,48,WHITE if outline else WINE,4,LINE if outline else None);self.t(x+18,y+15,label,14,INK if outline else WHITE,600)
 def field(self,x,y,label,w,value='',error=None):
  self.t(x,y,label,13,INK,500);self.r(x,y+24,w,48,WHITE,4,WINE if error else LINE);self.t(x+14,y+40,value or 'Введите '+label.lower(),14,MUTED)
  if error:self.t(x,y+80,error,12,WINE)
 def watch(self,x,y,w,h,color=WINE,strap='steel'):
  # Vector product illustration, every shape remains editable in Figma.
  cx=w/2;cy=h/2;radius=min(w*.23,h*.245);bw=radius*.88;top=cy-radius*1.92;bottom=cy+radius*.92
  body=f'<rect x="{cx-bw/2}" y="{top}" width="{bw}" height="{radius*3.84}" rx="{bw*.14}" fill="{("#B7B8B7" if strap=="steel" else "#4B3029")}"/>'
  if strap=='steel':
   for i in range(13):
    yy=top+i*radius*.285;body+=f'<path d="M{cx-bw/2} {yy}h{bw}" stroke="#E5E5E1" stroke-width="2"/>'
   body+=f'<rect x="{cx-bw*.2}" y="{top}" width="{bw*.4}" height="{radius*3.84}" fill="#DCDDD8" opacity=".6"/>'
  body+=f'<rect x="{cx+radius*.96}" y="{cy-7}" width="9" height="14" rx="2" fill="#989A97"/><circle cx="{cx}" cy="{cy}" r="{radius*1.09}" fill="#929793"/><circle cx="{cx}" cy="{cy}" r="{radius*1.035}" fill="#E4E5DE"/><circle cx="{cx}" cy="{cy}" r="{radius*.96}" fill="{color}"/>'
  for i in range(12):
   a=i*math.pi/6;xx=cx+math.sin(a)*radius*.77;yy=cy-math.cos(a)*radius*.77;body+=f'<circle cx="{xx}" cy="{yy}" r="1.7" fill="#F8F4E8"/>'
  body+=f'<path d="M{cx-radius*.37} {cy-radius*.3} {cx} {cy} {cx+radius*.38} {cy-radius*.48}" fill="none" stroke="#F8F4E8" stroke-width="3" stroke-linecap="round"/><path d="M{cx} {cy} {cx+radius*.14} {cy+radius*.57}" stroke="#C9A887" stroke-width="1"/><circle cx="{cx}" cy="{cy}" r="3" fill="#F8F4E8"/>'
  self.svg(x,y,w,h,body,'Часы — демонстрационная иллюстрация')
 def header(self):
  if self.mobile:
   self.r(0,0,self.w,30,WINE);self.t(52,8,'Южно-Сахалинск · Часы с характером',11,WHITE)
   self.r(0,30,self.w,66,WHITE);self.icon(20,52,'menu');self.t(115,43,'BIG BEN',25,INK,400,True);self.icon(306,52,'search');self.icon(346,52,'bag');self.line(0,95,self.w);self.y=120
  else:
   self.r(0,0,self.w,32,WINE);self.t(80,9,'Южно-Сахалинск',11,WHITE);self.t(585,9,'ВРЕМЯ БЫТЬ СОБОЙ',11,WHITE);self.t(1166,9,'Магазины и сервис',11,WHITE)
   self.r(0,32,self.w,92,WHITE);self.t(80,53,'BIG BEN',34,INK,400,True);self.t(81,93,'ЧАСЫ · СТИЛЬ · ХАРАКТЕР',8,MUTED,500)
   for i,n in enumerate(['Каталог','Бренды','Новинки','Журнал','О нас']):self.t(380+i*120,73,n,14,INK,500)
   for x,ic in [(1170,'search'),(1218,'heart'),(1266,'user'),(1314,'bag')]:self.icon(x,71,ic)
   self.line(0,123,self.w);self.y=162
 def heading(self,title=None,sub=None):
  if self.slug!='home':self.t(self.pad,self.y,'Главная  /  '+self.title,11,MUTED);self.y+=32
  heading=title or self.title
  if self.mobile and len(heading)>22:
   words=heading.split();lines=[];line=''
   for word in words:
    if len(line+' '+word)>22 and line:lines.append(line);line=word
    else:line=(line+' '+word).strip()
   if line:lines.append(line)
   for i,line in enumerate(lines):self.t(self.pad,self.y+i*40,line,32,INK,400,True)
   self.y+=len(lines)*40+18
  else:
   self.t(self.pad,self.y,heading,32 if self.mobile else 52,INK,400,True);self.y+=52 if self.mobile else 76
  if sub:self.y+=self.wrap(self.pad,self.y,sub,size=14 if self.mobile else 17)+18
 def section(self,title,link=None):
  self.t(self.pad,self.y,title,28 if self.mobile else 36,INK,400,True)
  if link and not self.mobile:self.t(self.w-260,self.y+11,link+'  →',13,WINE,600)
  self.y+=54 if self.mobile else 66
 def products(self,count=4,compact=False):
  cols=2 if self.mobile else 4;gap=12 if self.mobile else 24;w=(self.cw-gap*(cols-1))/cols;h=275 if self.mobile else 380;start=self.y
  names=['PRX Powermatic 80','Tsuyosa Automatic','Presage Cocktail','Classic St Mawes'];brands=['TISSOT','CITIZEN','SEIKO','DANIEL WELLINGTON'];prices=['79 900 ₽','42 900 ₽','59 900 ₽','18 900 ₽'];colors=[WINE,'#355B59','#26374B','#EAE0CD']
  for i in range(count):
   x=self.pad+(i%cols)*(w+gap);y=start+(i//cols)*(h+20);ih=168 if self.mobile else 250
   self.r(x,y,w,ih,PALE,6);self.watch(x+8,y+6,w-16,ih-12,colors[i%4],'leather' if i%4==3 else 'steel');self.icon(x+w-32,y+12,'heart')
   self.t(x,y+ih+18,brands[i%4],10 if self.mobile else 12,MUTED,600)
   self.t(x,y+ih+39,names[i%4][:19] if self.mobile else names[i%4],12 if self.mobile else 17,INK,500)
   self.t(x,y+ih+65,prices[i%4],15 if self.mobile else 19,INK,600)
   if not self.mobile:self.t(x+w-95,y+ih+69,'Подробнее →',11,WINE)
  self.y=start+math.ceil(count/cols)*(h+20)
 def tiles(self,items,cols=3):
  if self.mobile:cols=1
  gap=18;w=(self.cw-gap*(cols-1))/cols;start=self.y;hh=174
  for i,(a,b) in enumerate(items):
   x=self.pad+(i%cols)*(w+gap);y=start+(i//cols)*(hh+18);self.r(x,y,w,hh,WHITE,6,LINE);self.t(x+22,y+22,f'{i+1:02}',12,WINE,600);self.t(x+22,y+54,a,23,INK,400,True);self.wrap(x+22,y+91,b,w-44,14);self.icon(x+w-42,y+22,'arrow')
  self.y=start+math.ceil(len(items)/cols)*(hh+18)
 def form(self,fields,submit='Продолжить',intro=None):
  x=self.pad;w=min(self.cw,600);start=self.y
  if not self.mobile and self.slug not in ['checkout','profile','service-request']:
   w=440;x=220;self.r(810,start-10,430,460,PALE,8);self.watch(920,start+25,200,300);self.t(845,start+360,'Время для нового начала',28,INK,400,True)
  if intro:self.y+=self.wrap(x,self.y,intro,w,15)+24
  for label,value in fields:self.field(x,self.y,label,w,value);self.y+=96
  self.t(x,self.y,'□  Согласен с обработкой персональных данных',11,MUTED);self.y+=38;self.button(x,self.y,submit,w);self.y+=72
  if self.slug=='login':self.t(x,self.y,'Забыли пароль?       Создать аккаунт →',13,WINE);self.y+=46
  self.y=max(self.y,start+510 if not self.mobile and self.slug in ['login','register','reset'] else self.y)
 def textsections(self,items):
  if self.mobile:
   for title,body in items:
    self.t(self.pad,self.y,title,25,INK,400,True);self.y+=46;self.y+=self.wrap(self.pad,self.y,body,size=15)+35;self.line(self.pad,self.y,self.cw);self.y+=30
  else:
   for title,body in items:
    self.t(self.pad,self.y,title,27,INK,400,True);height=self.wrap(530,self.y,body,720,17);self.y+=max(height,70)+30;self.line(self.pad,self.y,self.cw);self.y+=36
 def accountnav(self):
  items=['Обзор','Мои данные','Заказы','Адреса','Бонусы']
  self.r(self.pad,self.y,self.cw,60,PALE,5)
  for i,item in enumerate(items[:3] if self.mobile else items):self.t(self.pad+16+i*(103 if self.mobile else 210),self.y+22,item,13,WINE if item=='Обзор' else INK,500)
  self.y+=88
 def footer(self):
  self.y+=40;y=self.y;h=330 if self.mobile else 250;self.r(0,y,self.w,h,'#242220');self.t(self.pad,y+32,'BIG BEN',31,'#F7F2E9',400,True)
  if self.mobile:
   self.t(self.pad,y+90,'Часы, которые становятся частью вас.',13,'#C5BDB2')
   self.t(self.pad,y+139,'Каталог     Бренды     Магазины',14,'#F7F2E9')
   self.t(self.pad,y+178,'Доставка     Оплата     Сервис',14,'#F7F2E9')
   self.t(self.pad,y+227,'Южно-Сахалинск · Написать нам →',13,'#C5BDB2');self.t(self.pad,y+285,'© BIG BEN   ·   Политика конфиденциальности',10,'#A69D92')
  else:
   self.t(self.pad,y+84,'Часы, которые становятся',15,'#C5BDB2');self.t(self.pad,y+109,'частью вашей истории.',15,'#C5BDB2')
   for x,title,links in [(450,'ПОКУПАТЕЛЯМ',['Доставка и оплата','Возврат и гарантия','Вопросы и ответы']),(770,'BIG BEN',['О компании','Наши магазины','Сервис и ремонт']),(1080,'НА СВЯЗИ',['Южно-Сахалинск','Контакты магазина','Написать нам →'])]:
    self.t(x,y+39,title,11,'#A69D92',600)
    for i,link in enumerate(links):self.t(x,y+78+i*29,link,14,'#F7F2E9')
   self.r(self.pad,y+181,self.cw,1,'#45413D');self.t(self.pad,y+208,'© BIG BEN 2026',11,'#A69D92');self.t(960,y+208,'Конфиденциальность     Условия продажи',11,'#A69D92')
  self.y+=h
 def finish(self):
  h=math.ceil(self.y);svg=f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="{self.w}" height="{h}" viewBox="0 0 {self.w} {h}"><title>{esc(self.title)}</title><rect width="100%" height="100%" fill="{BG}"/>'+''.join(self.parts)+'</svg>'
  name=f'{self.slug}-{("mobile" if self.mobile else "desktop")}';(ROOT/'screens'/f'{name}.svg').write_text(svg)
  ALL.append(dict(id=name,title=self.title,slug=self.slug,mobile=self.mobile,width=self.w,height=h,nodes=self.nodes))

def draw(c):
 s=c.slug;p=c.pad;w=c.cw;m=c.mobile;c.header()
 if s=='home':
  y=c.y;c.photo(p,y,w,215 if m else 435)
  if m:
   c.y+=241;c.t(p,c.y,'Время быть собой',35,INK,400,True);c.y+=55;c.y+=c.wrap(p,c.y,'Часы для ваших историй. Найдите модель, которую захочется носить каждый день.',size=15)+20;c.button(p,c.y,'Выбрать часы',w);c.y+=86
  else:
   c.t(p+48,y+65,'НОВАЯ ГЛАВА BIG BEN',11,WINE,600);c.t(p+48,y+112,'Время быть',60,INK,400,True);c.t(p+48,y+182,'собой',60,INK,400,True);c.wrap(p+48,y+268,'Часы для ваших историй.\nНайдите свой характер в деталях.',390,16,INK);c.button(p+48,y+344,'Выбрать часы',190);c.y+=478
  for i,text in enumerate((['Подбор в магазине','Сервис и забота'] if m else ['Подбор в магазине','Любимые мировые бренды','Сервис и забота','Самовывоз в Южно-Сахалинске'])):c.t(p+i*(w/(2 if m else 4)),c.y,text,11 if m else 13,MUTED)
  c.y+=74;c.section('У каждого времени свой стиль');c.tiles([('Для него','Характер в каждой детали'),('Для неё','Элегантность на каждый день'),('Для двоих','Стиль вне правил')]);c.y+=25;c.section('Новые истории','Все новинки');c.products(4)
  c.section('Бренды, которые знают время');brands=['TISSOT','SEIKO','CITIZEN','CASIO','ORIENT','FOSSIL'];cols=2 if m else 6;bw=w/cols
  for i,b in enumerate(brands):c.t(p+(i%cols)*bw,c.y+(i//cols)*57,b,18 if m else 21,INK,600)
  c.y+=math.ceil(6/cols)*57+40
  c.r(p,c.y,w,252 if m else 238,WINE,6);c.t(p+24,c.y+28,'БОЛЬШЕ, ЧЕМ ПОКУПКА',10,'#DDC4CC',600);c.t(p+24,c.y+68,'Ваши часы. Ваша история.',24 if m else 40,WHITE,400,True);c.wrap(p+24,c.y+118,'Поможем выбрать, примерить и сохранить любимые часы в отличной форме.',w-48 if m else 650,15,'#E4CDD4');c.button(p+24,c.y+185,'Узнать о Big Ben',190,True);c.y+=300 if m else 286
 elif s in ['catalog','men','women','unisex','brand','search','favorites']:
  titles={'brand':'Tissot — время традиций','search':'Поиск: «автоматические»'};c.heading(titles.get(s), 'Модели для жизни, работы и особенных моментов.' if s!='search' else 'Подобрали модели по вашему запросу.')
  c.r(p,c.y,w,52,WHITE,4,LINE);c.t(p+16,c.y+18,'Фильтры  +     '+('24 модели' if s=='favorites' else 'Бренд    ·    Цена    ·    Механизм'),12,INK);c.y+=72
  if s=='brand':
   c.wrap(p,c.y,'Новая глава швейцарского часового искусства: лаконичные линии, автоматические механизмы, выразительные циферблаты.',w,15);c.y+=100 if m else 66
  c.t(p,c.y,'Избранное · 4 модели' if s=='favorites' else 'Показано 8 моделей     ·     Сначала популярные',12,MUTED);c.y+=35;c.products(4 if s=='favorites' else 8);c.button(p,c.y,'Показать ещё',w if m else 240,True);c.y+=90
 elif s=='brands':
  c.heading(sub='Найдите бренд, близкий вашему характеру.');c.field(p,c.y,'Поиск бренда',w,'Название бренда');c.y+=112;c.t(p,c.y,'A   B   C   D   E   F   G   H   I   J   K   L   M',12,MUTED);c.y+=46
  c.tiles([(b,'Открыть коллекцию →') for b in ['Tissot','Seiko','Citizen','Casio','Orient','Fossil','Daniel Wellington','Certina','Hamilton']],3)
 elif s=='product':
  c.t(p,c.y,'Главная  /  Каталог  /  Tissot',11,MUTED);c.y+=34;y=c.y;pw=w if m else 680;ph=330 if m else 590;c.r(p,y,pw,ph,PALE,6);c.watch(p+20,y+18,pw-40,ph-36);c.icon(p+pw-40,y+18,'heart')
  if m:c.y+=ph+28;x=p;sw=w
  else:x=850;sw=510
  yy=c.y;c.t(x,yy,'TISSOT',12,WINE,600);yy+=32;c.t(x,yy,'PRX Powermatic 80',27 if m else 40,INK,400,True);yy+=58;c.t(x,yy,'Автоматические · 40 мм · Стальной браслет',11 if m else 14,MUTED);yy+=44;c.t(x,yy,'79 900 ₽',32,INK,600);yy+=48;c.t(x,yy,'Наличие уточняйте в выбранном магазине',12,GREEN);yy+=44;c.button(x,yy,'Добавить в корзину',sw);yy+=62;c.button(x,yy,'Примерить в магазине',sw,True);yy+=78;c.wrap(x,yy,'Доставка и самовывоз · Гарантия и сервис\nВозможность оплаты при получении',sw,14);yy+=92;c.y=max(y+ph+44,yy)
  c.section('Всё в деталях');c.textsections([('Описание','Чистая геометрия корпуса, тонкий профиль и выразительный циферблат. Модель легко становится частью повседневного гардероба.'),('Характеристики','Механизм: автоматический. Диаметр: 40 мм. Корпус и браслет: нержавеющая сталь. Стекло: сапфировое. Выберите размер и цвет, которые подходят вам.'),('Доставка и гарантия','Выберите самовывоз в магазине или доставку при оформлении. Условия и сроки отображаются после выбора города.')]);c.section('Вам могут понравиться');c.products(4)
 elif s=='compare':
  c.heading(sub='Сравните важные детали и выберите свои часы.');c.products(2 if m else 4);c.textsections([('Механизм','Tissot PRX: автоматический · Citizen Tsuyosa: автоматический'),('Размер корпуса','Tissot PRX: 40 мм · Citizen Tsuyosa: 40 мм'),('Материалы','Стальной корпус, браслет из стали, сапфировое стекло'),('Ваш выбор','Перейти к карточке модели и проверить наличие')])
 elif s in ['cart','checkout']:
  c.heading(sub='Ваш выбор — начало новой истории.');cw=w if m else 760;y=c.y
  for i,(name,price) in enumerate([('Tissot PRX Powermatic 80','79 900 ₽'),('Citizen Tsuyosa Automatic','42 900 ₽')]):
   cy=y+i*170;c.r(p,cy,cw,150,WHITE,6,LINE);c.r(p+12,cy+12,96,126,PALE,4);c.watch(p+17,cy+16,86,118,WINE if i==0 else '#355B59');c.t(p+124,cy+24,name[:21] if m else name,13 if m else 18,INK,500);c.t(p+124,cy+58,price,17,INK,600);c.t(p+124,cy+108,'−    1    +      Удалить',12,MUTED)
  c.y=y+352
  if s=='checkout':
   c.section('1. Контактные данные');c.form([('Имя',''),('Телефон','+7'),('Электронная почта','')],'Сохранить контакты');c.section('2. Получение');c.tiles([('Самовывоз','Выберите магазин и удобное время'),('Доставка','Адрес и срок уточняются при оформлении')],2);c.section('3. Оплата');c.tiles([('Банковская карта','Безопасная оплата заказа'),('СБП','Оплата через приложение банка')],2)
  c.r(p,c.y,w,290,PALE,6);c.t(p+22,c.y+22,'Ваш заказ',26,INK,400,True);c.t(p+22,c.y+73,'2 товара · 122 800 ₽',14,INK);c.t(p+22,c.y+110,'Доставка: после выбора адреса',12,MUTED);c.field(p+22,c.y+140,'Промокод',w-44 if m else 380,'');c.button(p+22,c.y+225,'Оформить заказ' if s=='cart' else 'Подтвердить и оплатить',w-44 if m else 380);c.y+=330
 elif s in ['success','empty','404']:
  c.heading({'success':'Спасибо за ваш выбор','empty':'Пока здесь нет часов','404':'Эта страница вне времени'}[s]);c.r(p,c.y,w,310,PALE,6);c.icon(p+24,c.y+26,'check' if s=='success' else 'search',WINE);c.t(p+24,c.y+80,'Заказ № BB-1024' if s=='success' else ('Начните свою историю' if s=='empty' else '404'),28,INK,400,True);c.wrap(p+24,c.y+133,'Статус и детали покупки появятся в личном кабинете.' if s=='success' else 'Откройте каталог и найдите часы, близкие вашему характеру.',w-48,16);c.button(p+24,c.y+230,'Мои заказы' if s=='success' else 'Открыть каталог',w-48 if m else 230);c.y+=355;c.section('Вдохновение рядом');c.products(4)
 elif s in ['login','register','reset']:
  c.heading({'login':'Рады видеть вас','register':'Ваша история начинается','reset':'Вернуть доступ'}[s]);fields={'login':[('Электронная почта',''),('Пароль','')],'register':[('Имя',''),('Электронная почта',''),('Телефон','+7'),('Пароль','')],'reset':[('Электронная почта','')]}[s];c.form(fields,{'login':'Войти','register':'Создать аккаунт','reset':'Получить письмо'}[s])
 elif s in ['account','profile','orders','order','addresses','loyalty']:
  c.heading();c.accountnav()
  if s=='profile':c.form([('Имя','Анна'),('Электронная почта','anna@example.com'),('Телефон','+7'),('Дата рождения','')],'Сохранить изменения')
  elif s=='addresses':c.tiles([('Дом','Южно-Сахалинск · Адрес покупателя'),('Добавить адрес','Сохраните адрес для следующих заказов')],2);c.form([('Город','Южно-Сахалинск'),('Улица, дом',''),('Квартира','')],'Сохранить адрес')
  elif s=='loyalty':
   c.r(p,c.y,w,230,WINE,8);c.t(p+24,c.y+28,'ВАШИ БОНУСЫ',11,'#E4CDD4',600);c.t(p+24,c.y+76,'1 250',54,WHITE,400,True);c.t(p+24,c.y+160,'История начислений и списаний →',14,WHITE);c.y+=274;c.textsections([('Как это работает','Получайте бонусы за покупки. Доступный баланс и условия списания отображаются при оформлении заказа.'),('История операций','Начисление за покупку · +1 250 бонусов. Посмотреть детали операции →')])
  elif s=='order':
   c.r(p,c.y,w,100,PALE,6);c.t(p+20,c.y+20,'Заказ BB-1024 · Собираем',24,INK,400,True);c.t(p+20,c.y+64,'Создан 9 октября · Самовывоз в магазине',13,MUTED);c.y+=140;c.products(2 if m else 4);c.textsections([('Получение','Магазин Big Ben · Южно-Сахалинск. Детали и время получения отображаются после подтверждения.'),('Оплата','Банковская карта · 122 800 ₽'),('Нужна помощь?','Напишите в магазин — поможем разобраться с заказом.')])
  elif s=='orders':c.tiles([('BB-1024','Собираем · 2 товара · 122 800 ₽'),('BB-0981','Получен · 1 товар · 18 900 ₽')],2)
  else:c.tiles([('Здравствуйте, Анна','Ваши часы и покупки в одном месте'),('Заказы','1 заказ ожидает получения'),('Бонусы','1 250 бонусов · Посмотреть историю')]);c.section('Ваше избранное');c.products(4)
 elif s in ['stores','store','contacts']:
  c.heading(sub='Будем рады познакомиться и помочь с выбором.');mh=260 if m else 340;c.r(p,c.y,w,mh,'#E8E3DA',6)
  for i in range(7):c.r(p+i*w/7,c.y,8,mh,'#FAF8F5')
  for i in range(4):c.r(p,c.y+i*mh/4,w,10,'#FAF8F5')
  c.icon(p+w*.52,c.y+mh*.48,'pin',WINE);c.r(p+18,c.y+18,190,38,WHITE,4);c.t(p+32,c.y+30,'Южно-Сахалинск',13,INK);c.y+=mh+38
  c.tiles([('Магазин Big Ben','Адрес и режим работы магазина'),('Связаться с нами','Позвонить · Написать сообщение'),('Записаться на примерку','Поможем выбрать удобное время')]);
  if s!='stores':c.section('Напишите нам');c.form([('Имя',''),('Телефон или email',''),('Ваш вопрос','')],'Отправить сообщение')
 elif s in ['service','service-request']:
  c.heading(sub='Чтобы любимые часы оставались с вами надолго.')
  if s=='service':c.tiles([('Диагностика','Оценим состояние и необходимые работы'),('Уход и обслуживание','Поможем сохранить точность и внешний вид'),('Браслет и ремешок','Подберём ремешок и удобную посадку')]);c.section('Расскажите о ваших часах')
  c.form([('Ваше имя',''),('Телефон','+7'),('Бренд и модель часов',''),('Что нужно сделать','')],'Отправить заявку');c.textsections([('Следующий шаг','После заявки специалист свяжется с вами, уточнит детали и согласует диагностику. Стоимость работ подтверждается до начала ремонта.')])
 elif s in ['news','article','about']:
  c.heading({'news':'Время читать','article':'Как выбрать первые часы','about':'Истории начинаются с деталей'}[s], 'Журнал Big Ben: люди, стиль и искусство времени.' if s=='news' else None);c.photo(p,c.y,w,230 if m else 380);c.y+=266 if m else 426
  if s=='news':c.tiles([('Как выбрать первые часы','Гид покупателя · 6 минут чтения'),('Механика или кварц?','Разбираемся в деталях · 4 минуты'),('Новая коллекция','Новости магазина · 3 минуты')]);c.tiles([('Часы и ваш стиль','Истории, которые вдохновляют'),('Забота о часах','Простые правила на каждый день'),('Встречаемся в Big Ben','События и новости магазинов')])
  elif s=='about':c.textsections([('Место встречи с вашим стилем','Big Ben — пространство для знакомства с часами, их характером и историей. Здесь можно спокойно выбрать, примерить и задать вопросы.'),('Выбор с вниманием к вам','Мы предлагаем дизайн, в котором покупателю легко сравнить модели, проверить наличие и выбрать удобный способ получения.'),('Продолжение истории','Сервис, уход и подбор аксессуаров помогают любимым часам оставаться частью вашей жизни.')]);c.tiles([('Наши магазины','Посмотреть адреса и выбрать магазин'),('Сервис','Забота о ваших часах'),('Связаться','Ответим на вопросы')])
  else:c.t(p,c.y,'ГИД ПОКУПАТЕЛЯ  ·  6 МИНУТ',11,WINE,600);c.y+=46;c.textsections([('Начните с того, что нравится','Хорошие часы — те, которые хочется носить. Обратите внимание на пропорции корпуса, цвет циферблата и ощущения от браслета.'),('Механика или кварц','Оба типа механизма подходят для ежедневного использования. Выбор зависит от привычек, интереса к устройству часов и удобства обслуживания.'),('Не пропускайте примерку','Даже точные размеры не заменяют примерку. Проверьте, как корпус лежит на запястье и подходит ли ремешок.'),('Выберите свои часы','Сравните несколько моделей в каталоге и запишитесь на примерку в Big Ben.')]);c.section('Часы для начала истории');c.products(4)
 elif s=='ui':
  c.heading(sub='Дополнительные состояния для разработки интерфейса.');c.button(p,c.y,'Добавить в корзину',w if m else 260);c.y+=68;c.r(p,c.y,w,58,'#EAF0E9',4);c.t(p+15,c.y+19,'✓ Товар добавлен в корзину',14,GREEN);c.y+=82;c.field(p,c.y,'Электронная почта',w if m else 540,'anna@','Проверьте адрес электронной почты');c.y+=116;c.r(p,c.y,w,80,'#F4E7E9',4);c.wrap(p+16,c.y+18,'Не удалось загрузить данные. Повторить →',w-32,14,WINE);c.y+=104
  c.section('Загрузка каталога');cols=2 if m else 4;gap=16;bw=(w-gap*(cols-1))/cols
  for i in range(cols):c.r(p+i*(bw+gap),c.y,bw,200,PALE,6);c.r(p+i*(bw+gap),c.y+219,bw*.75,12,LINE,3);c.r(p+i*(bw+gap),c.y+244,bw*.45,12,LINE,3)
  c.y+=300;c.section('Меню / фильтры');c.tiles([('Каталог','Мужские · Женские · Унисекс'),('Бренды','Поиск и алфавитный указатель'),('Фильтры','Цена · Механизм · Размер · Материал')]);c.textsections([('Пустой результат','По вашему запросу ничего не найдено. Сбросить фильтры или изменить запрос.'),('Нет в наличии','Сообщить о поступлении · Найти похожую модель'),('Валидация заказа','Заполните обязательные поля. Кнопка оплаты недоступна до подтверждения данных.')])
 else:
  c.heading()
  texts={
   'delivery':[('Получение в магазине','Выберите удобный магазин при оформлении заказа. Подтверждение готовности к выдаче появится в личном кабинете.'),('Доставка','Доступные способы, стоимость и срок рассчитываются после указания города и адреса.'),('После оформления','Магазин подтвердит наличие, согласует детали и сообщит об отправке или готовности к выдаче.')],
   'payment':[('Банковская карта','Выберите оплату картой при оформлении заказа. Перед оплатой вы увидите итоговую сумму и состав покупки.'),('Система быстрых платежей','Оплата через приложение банка. Пользователь видит итоговую сумму до перехода к оплате.'),('Безопасность','Сайт не хранит реквизиты банковской карты. Итоговый способ и статус оплаты отображаются в заказе.')],
   'returns':[('Возврат и обмен','Условия возврата зависят от категории товара и способа покупки. Свяжитесь с магазином — поможем уточнить порядок обращения.'),('Как обратиться','Подготовьте номер заказа и описание ситуации. Свяжитесь с магазином для проверки условий и согласования дальнейших действий.'),('Статус обращения','Ответ и решение по обращению доступны через выбранный канал связи.')],
   'warranty':[('Гарантия на часы','Срок и условия гарантии указываются для каждой модели. Сохраняйте документы о покупке.'),('Если нужна помощь','Свяжитесь с магазином, укажите модель и опишите неисправность. Специалист подскажет порядок обращения.'),('После диагностики','Решение о работах и сроках принимается после проверки состояния часов.')],
   'faq':[('Как выбрать часы?','Используйте фильтры по стилю, размеру и механизму. Для личного подбора запишитесь на примерку.'),('Как проверить наличие?','Наличие подтверждается для выбранной модели и магазина перед оплатой.'),('Можно ли заказать доставку?','Способы и сроки получения будут доступны после выбора города.'),('Как использовать бонусы?','Доступный баланс отображается в личном кабинете, а условия списания — при оформлении заказа.'),('Как обратиться в сервис?','Заполните заявку, указав модель часов и описание проблемы.')],
   'privacy':[('1. Оператор данных','Здесь описано, какие персональные данные используются для работы аккаунта, оформления и получения заказов.'),('2. Какие данные обрабатываются','Для работы с заказами используются данные аккаунта, контактная информация, адрес доставки и сведения о покупках.'),('3. Ваши права','Вы можете запросить сведения об обработке данных, исправить неточности или направить обращение через контакты магазина.')],
   'terms':[('1. Общие положения','Эти условия описывают порядок выбора товаров, подтверждения заказов, оплаты и получения покупок.'),('2. Оформление заказа','После оформления магазин подтверждает наличие товара и способ получения. Перед оплатой проверьте состав заказа и контактные данные.'),('3. Обращения покупателей','По вопросам заказа, возврата или обслуживания обратитесь в магазин через страницу «Контакты».')],
   'consent':[('Согласие покупателя','При отправке формы покупатель подтверждает согласие на обработку данных для выполнения указанного обращения или заказа.'),('Отдельные разрешения','Согласие на рекламные сообщения оформляется отдельно от необходимых действий по заказу.'),('Отзыв согласия','Для направления обращения об обработке данных используйте контакты магазина.')]
  }
  c.textsections(texts.get(s,[]));c.button(p,c.y,'Связаться с магазином',w if m else 270,True);c.y+=80
 c.footer();c.finish()
for slug,title in PAGES:
 for mobile in [False,True]:draw(Canvas(slug,title,mobile))
(ROOT/'design.json').write_text(json.dumps(dict(version=1,brand='BIG BEN',assets={'hero':HERO},screens=ALL),ensure_ascii=False))
(ROOT/'tokens.json').write_text(json.dumps({'colors':{'canvas':BG,'surface':WHITE,'text':INK,'muted':MUTED,'border':LINE,'primary':WINE,'soft':PALE,'success':GREEN},'typography':{'body':'Inter','display':'Playfair Display'},'breakpoints':{'mobile':390,'desktop':1440},'spacing':[4,8,12,16,20,24,32,40,48,64,80],'radius':[4,6,8],'motion':{'hover':'160ms ease-out, translateY(-3px)','entrance':'420ms cubic-bezier(.22,1,.36,1), opacity 0→1 / y 16→0','drawer':'280ms cubic-bezier(.22,1,.36,1)','reducedMotion':'Disable translations and parallax; show final states immediately'}},ensure_ascii=False,indent=2))
print('Generated',len(ALL),'screens')
