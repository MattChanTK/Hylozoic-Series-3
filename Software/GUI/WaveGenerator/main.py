#!/usr/bin/env python

from tkinter import *
import numpy
import time

class Window(Frame):

    def __init__(self, master=None):
        Frame.__init__(self, master)
        self.master = master
        self.init_window()
        self.wave.bind("<B1-Motion>", self.click)

    #Creation of init_window
    def init_window(self):

        # changing the title of our master widget
        self.master.title("GUI")

        # allowing the widget to take the full space of the root window
        self.wave = Canvas(width=600, height=200)
        self.wave_values = numpy.zeros(32)
        self.wave.grid(row=1,column=0, columnspan=2)
        self.wave.create_rectangle(0, 0, 600, 200, fill="grey", outline="grey")
        self.wave.create_line(0, 0, 0, 200, fill="black",tag="TimeIndex")
        self.tk_rgb = "#%02x%02x%02x" % (128, 192, 200)
        for N in range(0,32):
            self.oval = self.wave.create_oval(-2,-2,2,2,fill=self.tk_rgb)
            self.wave.move(self.oval,N*600/31,200-self.wave_values[N])
        for N in range(0,31):
            self.line = self.wave.create_line(N*600/31,200-self.wave_values[N],(N+1)*600/31,200-self.wave_values[N+1], fill="black")

        # w.create_line(0, 100, 200, 0, fill="grey", dash=(4, 4))

        self.pwm = Canvas(width=200, height=200)
        self.pwm.grid(row=1,column=2, columnspan=3)
        self.rect = self.pwm.create_rectangle(0, 0, 200, 200, fill="black", outline="black",tag ="PWM")

        # creating a button instance
        printWaveButton = Button(self.master, text="Print Wave",command=self.print_wave)

        # placing the button on my window
        printWaveButton.grid(row=0,column=0, sticky="W")
        self.e1 = Entry(self.master,width=70)
        self.e1.grid(row=0,column=1)

        # placing the button on my window
        printWaveButton.grid(row=0,column=0, sticky="W")
        self.e2 = Entry(self.master,width=5)
        self.e2.grid(row=0,column=2)
        self.e2.delete(0,END)
        self.e2.insert(0,"5")

        # creating a button instance
        animateButton = Button(self.master, text="Animate",command=self.animate)
        # placing the button on my window
        animateButton.grid(row=0,column=3)

        # creating a button instance
        quitButton = Button(self.master, text="Quit",command=self.client_exit)
        # placing the button on my window
        quitButton.grid(row=0,column=4)

    # create Functions to perform
    def client_exit(self):
        exit()

    def print_wave(self):
        S = ""
        Vals = 255/200*self.wave_values

        for N in range(0,32):
            S = S + str(int(round(Vals[N])))
            S = S + "_"
        S = S + "T" + str(self.e2.get())
        self.e1.delete(0,END)
        self.e1.insert(0,S)

    def click(self, event):
        x = event.x
        if(x < 0):
            x = 0
        elif(x>600):
            x=600

        y = event.y
        if(y < 0):
            y = 0
        elif(y>200):
            y=200
        print(y)
        W_index = round(x/600.0*31)
        self.wave_values[W_index] = 200-y
        self.wave_values[0] = 0
        self.wave_values[31] = 0
        self.wave.delete(ALL)
        self.wave.create_rectangle(0, 0, 600, 200, fill="grey", outline="grey")
        for N in range(0,32):
            self.oval = self.wave.create_oval(-2,-2,2,2,fill=self.tk_rgb)
            self.wave.move(self.oval,N*600/31,200-self.wave_values[N])
        for N in range(0,31):
            self.line = self.wave.create_line(N*600/31,200-self.wave_values[N],(N+1)*600/31,200-self.wave_values[N+1], fill="black")

    def animate(self):
        self.total_time = float(self.e2.get())
        fps = 30
        frames= int(fps*self.total_time)

        x = numpy.arange(0,32,32/frames)
        xp = numpy.arange(0,32)
        interp_wave_values = 255/200*numpy.interp(x,xp,self.wave_values)
        self.wave.delete("TimeIndex")
        self.wave.create_line(0, 0, 0, 200, fill="black",tag="TimeIndex")
        for n in range(0,frames):
            GV = interp_wave_values[n]
            rgb = "#%02x%02x%02x" % (GV, GV, GV)
            self.pwm.delete(ALL)
            self.wave.move("TimeIndex",600/frames,0)
            self.rect = self.pwm.create_rectangle(0, 0, 200, 200, fill=rgb, outline=rgb,tag="PWM")
            self.pwm.update()
            time.sleep(self.total_time/frames)
        self.wave.delete("TimeIndex")
        self.wave.create_line(0, 0, 0, 200, fill="black",tag="TimeIndex")

root = Tk()

#size of the window
root.geometry("810x250")
app = Window(root)
root.mainloop()