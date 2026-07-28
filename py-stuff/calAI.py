import tkinter as tk

# -----------------------------
# Calculator Functions
# -----------------------------
expression = ""

def press(key):
    global expression
    expression += str(key)
    equation.set(expression)

def equal():
    global expression
    try:
        result = str(eval(expression))
        equation.set(result)
        expression = result
    except:
        equation.set("Error")
        expression = ""

def clear():
    global expression
    expression = ""
    equation.set("")

def backspace():
    global expression
    expression = expression[:-1]
    equation.set(expression)

# -----------------------------
# Window
# -----------------------------
root = tk.Tk()
root.title("Python Calculator")
root.geometry("360x500")
root.resizable(False, False)
root.configure(bg="#202124")

equation = tk.StringVar()

# Display
entry = tk.Entry(
    root,
    textvariable=equation,
    font=("Arial", 24),
    justify="right",
    bd=10,
    relief=tk.FLAT,
    bg="#303134",
    fg="white"
)
entry.pack(fill="both", ipadx=8, ipady=20, padx=10, pady=10)

# Button Frame
frame = tk.Frame(root, bg="#202124")
frame.pack(expand=True, fill="both")

buttons = [
    ["C", "(", ")", "⌫"],
    ["7", "8", "9", "/"],
    ["4", "5", "6", "*"],
    ["1", "2", "3", "-"],
    ["0", ".", "=", "+"]
]

for r, row in enumerate(buttons):
    for c, text in enumerate(row):

        if text == "=":
            command = equal
        elif text == "C":
            command = clear
        elif text == "⌫":
            command = backspace
        else:
            command = lambda t=text: press(t)

        button = tk.Button(
            frame,
            text=text,
            font=("Arial", 18, "bold"),
            command=command,
            bg="#3C4043",
            fg="white",
            activebackground="#5F6368",
            activeforeground="white",
            relief=tk.FLAT
        )

        button.grid(row=r, column=c, sticky="nsew", padx=3, pady=3)

# Make grid responsive
for i in range(5):
    frame.rowconfigure(i, weight=1)

for j in range(4):
    frame.columnconfigure(j, weight=1)

root.mainloop()
