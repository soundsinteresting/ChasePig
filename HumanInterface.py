#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
import socket,re
from Referee import *

class HumanInterface():
    def __init__(self):
        log("please input server's \"ip:port\":",end=" ")
        while True:
            iport=input()
            m=re.fullmatch("([0-9\.]+?):([0-9]{1,5})",iport)
            if m:
                break
            else:
                log("format incorrect, please input like \"127.0.0.1:12345\":",end=" ")
        
        log("connecting to remote server...")
        self.s=socket.socket()
        self.s.connect((m.group(1),int(m.group(2))))
        log("connected to %s:%d"%self.s.getpeername())
    def recv_msg(self):
        while True:
            msg=self.s.recv(128)
            msg=msg.decode("ascii")
            if msg.startswith(SHUFFLE):
                self.recv_shuffle(msg)
            elif msg.startswith(YOURTURN):
                self.recv_turn(msg)
            elif msg.startswith(OVER):
                self.recv_over(msg)
            elif msg.startswith(FINALRESULT):
                log(msg)
                break
            else:
                log('unparsable msg "%s"'%(msg))
    def recv_shuffle(self,msg):
        cards=msg.split(",")[1:]
        self.mycards={"S":[],"H":[],"D":[],"C":[]}
        for i in cards:
            self.mycards[i[0]].append(i[1:])
        for i in list(self.mycards):
            if len(self.mycards[i])==0:
                self.mycards.pop(i)
        log("get cards %s"%(self.mycards))
    def recv_turn(self,msg):
        log("you have %s"%(self.mycards))
        log("%s: "%(msg),end="")
        msg=msg.split(",")
        if len(msg)==2:
            thesuit=None
        else:
            thesuit=msg[2][0]
        to_send=None
        while to_send==None:
            card=input()
            m=re.fullmatch("([SHDC])([1-9JQKA][0]{0,1})",card)
            if not m:
                log("format incorrect, please input [SHDC][2-9JQKA]: ",end="")
                continue
            suit=m.group(1)
            number=m.group(2)
            if number not in self.mycards[suit]:
                log("you do not have that card, please input your card again: ",end="")
                continue
            if suit!=thesuit and (thesuit!=None and len(self.mycards[thesuit])>0):
                log("you have to play a %s card: "%(thesuit),end="")
                continue
            for i in range(len(self.mycards[suit])):
                if self.mycards[suit][i]==number:
                    self.mycards[suit].pop(i)
                    break
            to_send="%s,%s"%(CHOICE,card)
        self.s.send(to_send.encode("ascii"))
    def recv_over(self,msg):
        log(msg)

if __name__=="__main__":
    h=HumanInterface()
    h.recv_msg()
    