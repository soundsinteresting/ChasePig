#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
import time,sys,traceback,socket,random

SHUFFLE="shuffle"
YOURTURN="your_turn"
CHOICE="choice"
ILLIGAL="illigal"
OVER="over"
FINALRESULT="finalresult"

LOGLEVEL={0:"DEBUG",1:"INFO",2:"WARN",3:"ERR",4:"FATAL"}
now_str=lambda: time.strftime("%H:%M:%S",time.localtime())
def log(msg,l=0,end="\n",logfile=None):
    st=traceback.extract_stack()[-2]
    lstr=LOGLEVEL[l]
    if l<3:
        tempstr="%s<%s:%d,%s> %s%s"%(now_str(),st.name,st.lineno,lstr,str(msg),end)
    else:
        tempstr="%s<%s:%d,%s> %s:\n%s%s"%(now_str(),st.name,st.lineno,lstr,str(msg),traceback.format_exc(limit=2),end)
    print(tempstr,end="")
    if l>=1:
        if logfile==None:
            logfile=sys.argv[0].split(".")
            logfile[-1]="log"
            logfile=".".join(logfile)
        with open(logfile,"a") as f:
            f.write(tempstr)
PRETTY_CARDS={"S":"♠ ","H":"♥ ","D":"♦ ","C":"♣ "}
CARD_ORDER={"2":2,"3":3,"4":4,"5":5,"6":6,"7":7,"8":8,"9":9,"10":10,"J":11,"Q":12,"K":13,"A":14}
CARD_VALUABLE={"H2":0,"H3":0,"H4":0,"H5":-10,"H6":-10,"H7":-10,"H8":-10,"H9":-10,"H10":-10,"HJ":-20,"HQ":-30,"HK":-40,"HA":-50,"C10":25,"DJ":100,"SQ":-100}
def prettify_cards(l):
    if isinstance(l,list):
        return ["%s%s"%(PRETTY_CARDS[i[0]],i[1]) for i in l]
    elif isinstance(l,str):
        for k in PRETTY_CARDS:
            l.replace(k,PRETTY_CARDS[k])
        return l
    else:
        return l

class Referee():
    def __init__(self,player_num=4):
        self.player_num=player_num
        self.s=socket.socket()
        self.s.bind(("",0))
        self.s.listen(self.player_num)
        log("The server is listening on %s:%d"%self.s.getsockname())
    def wait_players(self):    
        self.players={}
        self.scores={}
        online_num=0
        while online_num<self.player_num:
            sock,addr=self.s.accept()
            log("accept player on %s:%d"%addr)
            self.players[online_num]=sock
            self.scores[online_num]=[]
            online_num+=1
        log("all %d players have been online, they are %s"%(online_num,[self.players[i].getpeername() for i in sorted(self.players)]))
    def shuffle(self):
        cards=[]
        for i in ("S","H","D","C"):#("♠","♥","♦","♣"):
            for j in ("2","3","4","5","6","7","8","9","10","J","Q","K","A"):
                cards.append(i+j)
        random.shuffle(cards)
        for i in self.players:
            str_temp=SHUFFLE+","+",".join(cards[i*13:(i+1)*13])
            self.players[i].send(str_temp.encode("ascii"))
            log("send to player %d %s"%(i,prettify_cards(str_temp)))
    def rounds(self):
        startat=random.randint(0,self.player_num-1)
        for i in range(13):
            log("turn will start at player %d"%(startat))
            hist=[YOURTURN,None]
            for j in range(self.player_num):
                pnum=(j+startat)%self.player_num
                hist[1]=str(j)
                str_temp=",".join(hist)
                self.players[pnum].send(str_temp.encode("ascii"))
                msg=self.players[pnum].recv(128)
                msg=msg.decode("ascii")
                log('get "%s" from player %d'%(msg,pnum))
                hist.append(msg.split(",")[-1])
            hist.pop(1)
            hist[0]=OVER
            log("round %d start at %d: %s"%(i,startat,hist))
            byte_temp=",".join(hist).encode("ascii")
            for j in range(self.player_num):
                self.players[j].send(byte_temp)
            startat=(startat+Referee.winner(hist[1:]))%self.player_num
            for j in hist[1:]:
                if j in CARD_VALUABLE:
                    self.scores[startat].append(j)
        result=[]
        for i in range(self.player_num):
            result.append(Referee.calc_score(self.scores[i]))
            log("player %d %s %d"%(i,self.scores[i],result[-1]))
        result_str="%s,%s"%(FINALRESULT,result)
        result_byte=result_str.encode("ascii")
        log(result_str)
        for i in range(self.player_num):
            self.players[i].send(result_byte)
    def winner(l):
        w=0
        for i in range(1,len(l)):
            if l[i][0]==l[0][0] and CARD_ORDER[l[i][1:]]>CARD_ORDER[l[w][1:]]:
                w=i
        return w
    def calc_score(l):
        s=0
        has_score_flag=False
        c10_flag=False
        for i in l:
            if i=="C10":
                c10_flag=True
            else:
                s+=CARD_VALUABLE[i]
                has_score_flag=True
        if c10_flag==True:
            if has_score_flag==False: 
                s+=50
            else:
                s*=2
        return s
if __name__=="__main__":
    r=Referee(player_num=4)
    r.wait_players()
    r.shuffle()
    r.rounds()

