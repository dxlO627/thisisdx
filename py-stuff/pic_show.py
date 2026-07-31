"""
this only for train on my local computer ---




"""
from tkinter import *
from PIL import ImageTk,Image


root = Tk()
root.title("test pp2")

my_img1 = ImageTk.PhotoImage(Image.open(r"images\afterlife.png"))
my_img2 = ImageTk.PhotoImage(Image.open(r"images\image1.png"))
my_img3 = ImageTk.PhotoImage(Image.open(r"images\image2.png"))
my_img4 = ImageTk.PhotoImage(Image.open(r"images\image2.png"))


image_list= [my_img1,my_img2,my_img3,my_img4]

status = Label(root, text="image 1 of " +str(len(image_list)),bd=1, relief=SUNKEN, anchor=E)

my_label = Label(image=my_img1)
my_label.grid(row=0,column=0,columnspan=3)

def forward(image_number):
    global my_label
    global button_next
    global button_back

    my_label.grid_forget()
    my_label = Label(image=image_list[image_number-1])
    button_next = Button(root,text="-->",command=lambda:forward(image_number+1))
    button_back = Button(root,text="<<",command=lambda: back(image_number-1))


    if image_number == 4:
        button_next = Button(root,text=">>",state=DISABLED)


    
    my_label.grid(row=0,column=0,columnspan=3)
    button_back.grid(row=1,column=0)
    button_next.grid(row=1,column=2)


    status = Label(root, text=f"image {image_number} of " +str(len(image_list)),bd=1, relief=SUNKEN, anchor=E)
    status.grid(row=2,column=0,columnspan=3,sticky=W+E)




def back(image_number):

    global my_label
    global button_next
    global button_back
    my_label.grid_forget()
    my_label = Label(image=image_list[image_number-1])
    button_next = Button(root,text="-->",command=lambda:forward(image_number+1))
    button_back = Button(root,text="<<",command=lambda: back(image_number-1))
    
    if image_number == 1:
        button_back = Button(root,text="<<",state=DISABLED)
    

    my_label.grid(row=0,column=0,columnspan=3)
    button_back.grid(row=1,column=0)
    button_next.grid(row=1,column=2)


    status = Label(root, text=f"image {image_number} of " +str(len(image_list)),bd=1, relief=SUNKEN, anchor=E)
    status.grid(row=2,column=0,columnspan=3,sticky=W+E)
    

button_back = Button(root,text="<<",state=DISABLED)
button_kill = Button(root,text="EXIT",command=root.quit)
button_next = Button(root,text="-->",command=lambda: forward(2))


button_back.grid(row=1, column=0)
button_kill.grid(row=1,column=1)
button_next.grid(row=1,column=2)
status.grid(row=2,column=0,columnspan=3,sticky=W+E)


root.mainloop()
