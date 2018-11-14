# coding:utf-8
import kivy
kivy.require('1.7.2') # replace with your current kivy version !
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition
from kivy.properties import ListProperty, ObjectProperty, StringProperty, NumericProperty
from kivy.factory import Factory
from kivy.uix.button import Button
from kivy.uix.tabbedpanel import TabbedPanel, TabbedPanelItem
from kivy.uix.spinner import Spinner
from kivy.uix.dropdown import DropDown
from kivy.uix.checkbox import CheckBox
from kivy.lang import Builder
from kivy.uix.popup import Popup
from kivy.uix.textinput import TextInput
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.stacklayout import StackLayout
from kivy.uix.label import Label
#from kivy.clock import Clock
from kivy.uix.progressbar import ProgressBar
from kivy.storage.jsonstore import JsonStore
from kivy.uix.gridlayout import GridLayout
from functools import partial
#from kivy.uix.treeview import TreeView, TreeViewNode
#from kivy.uix.treeview import TreeViewLabel
from kivy.uix.scrollview import ScrollView
try:
	from plyer import sms
except:
	pass
#Declaration of global variables:
settingdata = JsonStore('settingdata.json')

Builder.load_string('''
<MainScreen>:
    name: 'mainscreen'
    canvas.before:
        Color:
            rgba: 1, 1, 1, 1
        Rectangle:
            pos: self.pos
            size: self.size
    GridLayout:
        row_default_height:root.height / 8
		cols:1
        orientation: 'vertical'
        ActionBar:
            width:root.width
            height:root.height / 8
            background_color:125,125,125,1,1
            pos_hint: {'top':1}
            ActionView:
                use_separator: True
                ActionPrevious:
                    app_icon: 'emadrs.png'
                    title: ''
                    with_previous: False
                ActionGroup:
                    mode: 'spinner'
                    text: 'Meny'
                    #color: 0,0,0,1
                    ActionButton:
                        text: 'SMS-nr'
                        on_release: root.settings()
        GridLayout:
			cols:1
			id: megabox
        BoxLayout:
            #width:root.width
            #height:root.height / 8
            orientation: 'horizontal'
            size_hint: None,None
            size:root.width, .1*root.height
            id:checkboxes
''')  

class MainScreen(Screen):
	nownr=0
	qlist=(
	"Här ber vi dig beskriva din sinnesstämning, om du känner dig ledsen, tungsint eller dyster till mods. Tänk efter hur du har känt dig de senaste tre dagarna, om du har skiftat i humöret eller om det har varit i stort sett detsamma hela tiden, och försök särskilt komma ihåg om du har känt dig lättare till sinnes om det har hänt något positivt.",
	"Här ber vi dig markera i vilken utsträckning du haft känslor av inre spänning, olust och ångest eller odefinierad rädsla under de senaste tre dagarna. Tänk särskilt på hur intensiva känslorna varit, och om de kommit och gått eller funnits hela tiden.",
	"Här ber vi Dig beskriva hur bra du sover. Tänk efter hur länge du sovit och hur god sömnen varit under de senaste tre nätterna. Bedömningen skall avse hur du faktiskt sovit, oavsett om du tagit sömnmedel eller ej. Om du sover mer än vanligt, sätt din markering vid 0.",
	"Här ber vi dig ta ställning till hur din aptit är, och tänka efter om den på något sätt skilt sig från vad som är normalt för dig. Om du skulle ha bättre aptit än normalt, markera då det på 0.",
	"Här ber vi dig ta ställning till din förmåga att hålla tankarna samlade och koncentrera dig på olika aktiviteter. Tänk igenom hur du fungerar vid olika sysslor som kräver olika grad av koncentrationsförmåga, t ex läsning av komplicerad text, lätt tidningstext och TV-tittande.",
	"Här ber vid dig försöka värdera din handlingskraft. Frågan gäller om du har lätt eller svårt för att komma igång med sådant du tycker du bör göra, och i vilken utsträckning du måste över vinna ett inre motstånd när du skall ta itu med något.",
	"Här ber vi dig ta ställning till hur du upplever ditt intresse för omvärlden och för andra människor, och för sådana aktiviteter som brukar bereda dig nöje och glädje.",
	"Frågan gäller hur du ser på din egen framtid och hur du uppfattar ditt eget värde. Tänk efter i vilken utsträckning du ger dig självförebråelser, om du plågas av skuldkänslor, och om du oroat dig oftare än vanligt för t ex din ekonomi eller din hälsa.",
	"Frågan gäller din livslust, och om du känt livsleda. Har du tankar på självmord, och i så fall, i vilken utsträckning upplever du detta som en verklig utväg?"
	)
	dscrptn=(
		(
			"0 Jag kan känna mig glad eller ledsen, allt efter omständigheterna.",
			"1",
			"2 Jag känner mig nedstämd för det mesta, men ibland kan det kännas lättare.",
			"3",
			"4 Jag känner mig genomgående nedstämd och dyster. Jag kan inte glädja mig åt sådant som vanligen skulle göra mig glad.",
			"5",
			"6 Jag är totalt nedstämd och olycklig att jag inte kan tänka mig värre."
		),
		(
			"0 Jag känner mig mestadels lugn.",
			"1",
			"2 Ibland har jag obehagliga känslor av inre oro.",
			"3",
			"4 Jag har ofta en känsla av inre oro som ibland kan bli mycket stark, och som jag måste anstränga mig för att bemästra.",
			"5",
			"6 Jag har fruktansvärda, långvariga eller outhärdliga ångestkänslor.",
		),
		(
			"0 Jag sover lugnt och bra och tillräckligt länge för mina behov. Jag har inga särskilda svårigheter att somna.",
			"1",
			"2 Jag har vissa sömnsvårigheter. Ibland har jag svårt att somna eller sover ytligare eller oroligare än vanligt.",
			"3",
			"4 Jag sover minst två timmar mindre per natt än normalt. Jag vaknar ofta under natten, även om jag inte blir störd.",
			"5",
			"6 Jag sover mycket dåligt, inte mer än 2-3 timmar per natt."
		),
		(
			"0 Min aptit är som den brukar vara.",
			"1",
			"2 Min aptit är sämre än vanligt.",
			"3",
			"4 Jag har påtagligt svårt att koncentrera mig på sådant som normalt inte kräver någon ansträngning från min sida (t ex läsning eller samtal med andra människor).",
			"5",
			"6 Jag kan överhuvudtaget inte koncentrera mig på någonting."
		),
		(
			"0 Jag har inga koncentrationssvårigheter.",
			"1",
			"2 Jag har tillfälligt svårt att hålla tankarna samlade på sådant som normalt skulle fånga min uppmärksamhet (t ex läsning eller TV-tittande).",
			"3",
			"4 Jag har påtagligt svårt att koncentrera mig på sådant som normalt inte kräver någon ansträngning från min sida (t ex läsning eller samtal med andra människor).",
			"5",
			"6 Jag kan överhuvudtaget inte koncentrera mig på någonting."
		),
		(
			"0 Jag har inga svårigheter med att ta itu med nya uppgifter.",
			"1",
			"2 När jag skall ta itu med något, tar det emot på ett sätt som inte är normalt för mig.",
			"3",
			"4 Det krävs en stor ansträngning för mig att ens komma igång med enkla uppgifter som jag vanligtvis utför mer eller mindre rutinmässigt.",
			"5",
			"6 Jag kan inte förmå mig att ta itu med de enklaste vardagssysslor."
		),
		(
			"0 Jag är intresserad av omvärlden och engagerar mig i den, och det bereder mig både nöje och glädje.",
			"1",
			"2 Jag känner mindre starkt för sådant som brukar engagera mig. Jag har svårare än vanligt att bli glad eller svårare att bli arg när det är befogat.",
			"3",
			"4 Jag kan inte känna något intresse för omvärlden, inte ens för vänner och bekanta.",
			"5",
			"6 Jag har slutat uppleva några känslor. Jag känner mig smärtsamt likgiltig även för mina närmaste."
		),
		(
			"0 Jag ser på framtiden med tillförsikt. Jag är på det hela taget ganska nöjd med mig själv.",
			"1",
			"2 Ibland klandrar jag mig själv och tycker att jag är mindre värd än andra.",
			"3",
			"4 Jag grubblar ofta över mina misslyckanden och känner mig mindervärdig eller dålig, även om andra tycker annorlunda.",
			"5",
			"6 Jag ser allting i svart och kan inte se någon ljusning. Det känns som om jag var en alltigenom dålig människa, och som om jag aldrig skulle kunna få någon förlåtelse för det hemska jag gjort."
		),
		(
			"0 Jag har normal aptit på livet.",
			"1",
			"2 Livet känns inte särskilt meningsfullt men jag önskar ändå inte att jag vore död.",
			"3",
			"4 Jag tycker ofta det vore bättre att vara död, och trots att jag egentligen inte önskar det, kan självmord ibland kännas som en möjlig utväg.",
			"5",
			"6 Jag är egentligen övertygad om att min enda utväg är att dö, och jag tänker mycket på hur jag bäst skall gå tillväga för att ta mitt eget liv."
		)
	)
	valuetuple=(0,0,0,0,0,0,0,0,0)
	bttns=(0,0,0,0,0,0,0,0,0)
	bigheight=NumericProperty()
	fontheight=15
	linelen=30
	def __init__ (self,**kwargs):
		super (MainScreen, self).__init__(**kwargs)
		self.planupdate()
		
	def planupdate(self):
		self.bigheight=0
		thescroll=ScrollView(size= self.size, bar_pos_x="top")
		bigbox=GridLayout(
                cols=1,
                orientation='vertical',
                #height=self.minimum_height,
                #height=root.bigheight,
                #padding= (thescroll.width * 0.02, thescroll.height * 0.02),
                #spacing= (thescroll.width * 0.02, thescroll.height * 0.02),
                size_hint_y= None,
                size_hint_x= 1,
                do_scroll_x= False,
                do_scroll_y= True,
                )
		#self.linelen=self.ids.bigbox.width/sp(self.fontheight)
		try:
			self.ids.checkboxes.clear_widgets()
			self.ids.megabox.clear_widgets()
		except:
			pass
		for i in range(0,9):
			if self.fontheight*(len(self.qlist[i])/self.linelen) > self.fontheight :
				qheight=0*self.fontheight+self.fontheight*(len(self.qlist[i])/self.linelen)
			else:
				qheight=self.fontheight
			newq=Label(color=(0,0,0,1), size_hint_y=None, size_hint_x=1, size=(bigbox.width, "%ssp"%str(qheight)))#, font_size=self.fontheight)
			newq.bind(width=lambda s, w:
				   s.setter('text_size')(s, (self.width, None)))
			newq.bind(height=newq.setter('texture_size[1]')) 
			newq.bind(height=newq.setter('self.minimum_height'))	
			newbox=Button(id="box%s"%str(i))
			txt=''
			if self.bttns[i]==1:
				txt=str(self.valuetuple[i])
				newbox.color=(1,1,1,1)
			elif self.bttns[i]==0:
				txt="*"
				newbox.color=(0,0,0,1)
			newbox.text=txt
			if i==self.nownr:
				newbox.background_color= (.25, .75, 1.0, 1.0)
				newq.text=str("%s"%self.qlist[i])
				self.bigheight=self.bigheight+2*newq.height
				bigbox.add_widget(newq)
				for j in range(0,7):
					if self.fontheight*(len(self.dscrptn[i][j])/self.linelen) > 3*self.fontheight :
						bttnheight=2*self.fontheight+self.fontheight*(len(self.dscrptn[i][j])/self.linelen)
					else:
						bttnheight=3*self.fontheight
					smallLabel=Button(text="%s"%self.dscrptn[i][j],size_hint=(1,None), height="%ssp"%str(bttnheight))#, font_size=self.fontheight)
					smallLabel.bind(width=lambda s, w:
						s.setter('text_size')(s, (self.width-100, None)))
					smallLabel.bind(height=smallLabel.setter('texture_size[1]'))
					smallLabel.bind(height=smallLabel.setter('self.minimum_height'))
					smallLabel.bind(on_press=partial(self.radiobox, i, j))
					if self.valuetuple[i] == j and self.bttns[i]==1:
						smallLabel.background_color = (.25, .75, 1.0, 1.0)
					else:
						smallLabel.background_color = (1.0, 1.0, 1.0, 1.0)
					bigbox.add_widget(smallLabel)
					self.bigheight=self.bigheight+smallLabel.height
		
			newbox.bind(on_release=partial(self.chng_bttn, i))
			self.ids.checkboxes.add_widget(newbox)
		
		bigbox.height=self.bigheight
		
		thescroll.bar_pos_x="top"
		thescroll.add_widget(bigbox)
		self.ids.megabox.add_widget(thescroll)
		
		sendbox=Button(id="sendbox", text=">>")
		sendbox.bind(on_release=(lambda store_btn: self.Submit()))
		self.ids.checkboxes.add_widget(sendbox)
		
		
	def	radiobox(self, i,j,*args):
		listV = list(self.valuetuple)
		listV[i]=j
		listB = list(self.bttns)
		listB[i]=1
		#self.ids.eval("chckbx%set%s"%(str(i),str(j)))
		#myCheckBox1.value = True
		self.valuetuple = tuple(listV)
		self.bttns = tuple(listB)
		maxloops=2*len(self.bttns)-1
		loops=0
		number=i
		while self.bttns[number] == 1 :
			loops += 1
			if number == len(self.bttns)-1:
				number=0
			if loops==maxloops:
				self.nownr=i
				break
			number += 1
			self.nownr=number
		self.planupdate()
		
	def chng_bttn(self,number, *args):
		self.nownr=number
		self.planupdate()
		
	def settings(self):
		box = BoxLayout(orientation='vertical')
		popup1 = Popup(title='SMS-nr', content=box, size_hint=(.90, .90))
		biggerbox=BoxLayout(orientation='horizontal')
		biggerbox.add_widget(Label(text='SMS-mottagarens nummer:'))
		#inpt=TextInput(multiline=False,input_type='number')
		try:
			inpt=TextInput(multiline=False,input_type='number',text=settingdata.get('email')['address'])
		except:
			inpt=TextInput(multiline=False,input_type='number',text="")
		biggerbox.add_widget(inpt)
		store_btn = Button(text='OK')
		store_btn.bind(on_release=(lambda store_btn: self.change_mail(inpt.text, popup1)))
		#store_btn.bind(on_press = lambda *args: popup1.dismiss())
		
		box.add_widget(biggerbox)
		box.add_widget(store_btn)
		popup1.open()

	def Submit(self):
		filled = 1
		for i in self.bttns :
			if i == 0 :
				filled=0
		if filled==0 :
			box = BoxLayout(orientation='vertical')
			popup1 = Popup(title='', content=box, size_hint=(.75, .75))
			box.add_widget(Label(text='Var god och svara på alla frågor.'))
			store_btn = Button(text='OK')
			store_btn.bind(on_press = lambda *args: popup1.dismiss())
			box.add_widget(store_btn)
			popup1.open()
		else:
			summa=sum(self.valuetuple)
			box = BoxLayout(orientation='vertical')
			popup1 = Popup(title='', content=box, size_hint=(.75, .75))
			if summa < 13:
				themessage='MADRS-S-score visar symptom som kan tyda på: %s\nIngen eller mycket lätt depression.'%(summa)
			if summa >= 13 and summa <= 19:
				themessage='MADRS-S-score visar symptom som kan tyda på: %s\nLätt depression.'%(summa)
			if summa >= 20 and summa <= 34:
				themessage='MADRS-S-score visar symptom som kan tyda på: %s\nMåttlig depression.'%(summa)
			if summa >= 35 :
				themessage='MADRS-S-score visar symptom som kan tyda på: %s\nSvår depression.'%(summa)
			box.add_widget(Label(text=themessage))	
			store_btn = Button(text='OK')
			store_btn.bind(on_press = lambda store_btn: self.send_mail(themessage, popup1))
			box.add_widget(store_btn)
			popup1.open()
	
	def change_mail(self, theaddress, popup1):
		popup1.dismiss()
		settingdata.put('email', address=theaddress)

	def send_mail(self, themessage, popup1):
		popup1.dismiss()
		box = BoxLayout(orientation='vertical')
		tried=0
		try:
			to_nr = str(settingdata.get('email')['address'])
			mess = str(themessage)
			sms.send(recipient=to_nr, message=mess)
#			email.send(recipient=StringProperty(str(settingdata.get('email')['address'])),
#				subject=StringProperty('MADRS-S'),
#				text=StringProperty('%s'%themessage)
				#,create_chooser=BooleanProperty()
#				)
			box.add_widget(Label(text='SMS skickat till: %s'%settingdata.get('email')['address']))
			#box.add_widget(Label(text='Email sent to:%s'%settingdata.get('email')['address']))
			tried=1
		except:
			#box.add_widget(Label(text='Couldn\'t send e-mail'))
			box.add_widget(Label(text='Kunde inte skicka SMS'))
		
		popup2 = Popup(title='Settings', content=box, size_hint=(.75, .75))
		store_btn = Button(text='OK')
		store_btn.bind(on_press = lambda *args: popup2.dismiss())
		box.add_widget(store_btn)
		popup2.open()



class emadrsApp(App):
	def build(self):
			the_screenmanager = ScreenManager()
			#the_screenmanager.transition = FadeTransition()
			mainscreen = MainScreen(name='mainscreen')
			the_screenmanager.add_widget(mainscreen)
			return the_screenmanager
					
	def on_pause(self):
			# Here you can save data if needed
			return True

	def on_resume(self):
			the_screenmanager = ScreenManager()
			#the_screenmanager.transition = FadeTransition()
			mainscreen = MainScreen(name='mainscreen')
			the_screenmanager.add_widget(mainscreen)
			return the_screenmanager
		
	def on_start(self):
			the_screenmanager = ScreenManager()
			#the_screenmanager.transition = FadeTransition()
			mainscreen = MainScreen(name='mainscreen')
			the_screenmanager.add_widget(mainscreen)
			return the_screenmanager

	def on_stop(self):
		pass

if __name__ == '__main__':
	emadrsApp().run()
