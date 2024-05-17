import os, sys, io, codecs
import sqlite3
from PyQt5.QtWidgets import QMessageBox, QFileDialog,QListWidgetItem, QListWidget



class Player():

    def __init__(self,name, position,ht, wt, spd, run, rcv, blk, throw, kick):
    
        self.name = name
        self.position = position
        self.height = ht
        self.weight = wt
        self.speed = spd
        self.run = run
        self.rcv = rcv
        self.blk = blk
        self.throw = throw
        self.kick = name





