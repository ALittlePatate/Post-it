import tkinter as tk
import sys, getopt, traceback, types
import os
from tkinter import *
from tkinter.filedialog import askopenfilename
from tkinter.filedialog import asksaveasfilename
from tkinter.scrolledtext import ScrolledText

def runAsAdmin(cmdLine=None, wait=True):

    if os.name != 'nt':
        raise(RuntimeError, "This function is only implemented on Windows.")

    import win32api, win32con, win32event, win32process
    from win32com.shell.shell import ShellExecuteEx
    from win32com.shell import shellcon

    python_exe = sys.executable

    if cmdLine is None:
        cmdLine = [python_exe] + sys.argv
    elif type(cmdLine) not in (types.TupleType,types.ListType):
        raise(ValueError, "cmdLine is not a sequence.")
    cmd = '"%s"' % (cmdLine[0],)
    # XXX TODO: isn't there a function or something we can call to massage command line params?
    params = " ".join(['"%s"' % (x,) for x in cmdLine[1:]])
    cmdDir = ''
    showCmd = win32con.SW_SHOWNORMAL
    #showCmd = win32con.SW_HIDE
    lpVerb = 'runas'  # causes UAC elevation prompt.

    # print "Running", cmd, params

    # ShellExecute() doesn't seem to allow us to fetch the PID or handle
    # of the process, so we can't get anything useful from it. Therefore
    # the more complex ShellExecuteEx() must be used.

    # procHandle = win32api.ShellExecute(0, lpVerb, cmd, params, cmdDir, showCmd)

    procInfo = ShellExecuteEx(nShow=showCmd,
                              fMask=shellcon.SEE_MASK_NOCLOSEPROCESS,
                              lpVerb=lpVerb,
                              lpFile=cmd,
                              lpParameters=params)

    if wait:
        procHandle = procInfo['hProcess']    
        obj = win32event.WaitForSingleObject(procHandle, win32event.INFINITE)
        rc = win32process.GetExitCodeProcess(procHandle)
        #print "Process handle %s returned code %s" % (procHandle, rc)
    else:
        rc = None

    return rc


open_file = " "
cwd = os.getcwd()
window = tk.Tk()
window.attributes("-topmost", False)
window.geometry("600x425")
window.minsize(0,0)
window['background']='#fff96d'
window.resizable(99999,99999)
try :
    window.iconbitmap("Icon/icon.ico")
except :
    pass
window.title("Post-It ! - Untitled")

def main(argv) :
    global open_file
    try:
        opts, args = getopt.getopt(argv,"hi:o:",["open=","admin"])
    except getopt.GetoptError:
        print('python post-it.py -o <file to open> -a <run as admin>')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print("Usage :")
            print('python post-it.py -o <file to open> -a <run as admin>')
            print(" ")
            print('Note : You can theoretically open all types of files with post-it but it may not work.')
            sys.exit()
        elif opt in ("-o", "--open"):
            open_file = arg
        elif opt in ("-a", "--admin"):
            runAsAdmin()

def file_assos() :
    global cwd
    os.system('assoc .post-it="'+cwd+'\post-it.bat"')

def openfile_arg() :
    global current_file
    global open_file

    if open_file == " " :
        return

    current_file = open_file
    window.title("Post-It ! - "+current_file)

    try :
        with open(open_file, "r") as file_opened :
            file_str = file_opened.read()
    except Exception as e:
        #print(e)
        pass

    text.insert(INSERT, file_str)

topmost = True
current_file = " "

def newfile(*args) :
    global text
    global current_file
    current_file = " "
    window.title("Post-It ! - Untitled")
    text.delete('1.0', END)

def savefile(*args) :
    global text
    file_content = text.get('1.0', END)
    
    try :
        with open(current_file, "r+") as file_save :
            file_save.write(file_content)
            file_save.close()
    except FileNotFoundError :
        savefileas()

def savefileas(*args) :
    global text
    global tkFileDialog
    global current_file
    file_content = text.get('1.0', END)

    try :
        f = asksaveasfilename(title="Save as", initialdir=cwd+"/My Post-it Files", defaultextension=".post-it", filetypes=(("Post-it File", "*.post-it"),("All Files", "*.*")))
    except :
        f = asksaveasfilename(title="Save as", defaultextension=".post-it", filetypes=(("Post-it File", "*.post-it"),("All Files", "*.*")))
    if f is None:
        return
    
    current_file = f
    window.title("Post-It ! - "+current_file)
    
    try :
        with open(f, "w") as file_save :
            file_save.write(file_content)
            file_save.close()
    except Exception as e:
        #print(e)
        pass

def openfile(*args) :
    global tkFileDialog
    global current_file

    try :
        f = askopenfilename(title="Open", initialdir=cwd+"/My Post-it Files", defaultextension=".post-it", filetypes=(("Post-it File", "*.post-it"),("All Files", "*.*")))
    except :
        f = askopenfilename(title="Open", defaultextension=".post-it", filetypes=(("Post-it File", "*.post-it"),("All Files", "*.*")))
    if f is None:
        return
    
    current_file = f
    window.title("Post-It ! - "+current_file)
    text.delete('1.0', END)

    try :
        with open(f, "r") as file_opened :
            file_str = file_opened.read()
            file_opened.close()
        text.insert(INSERT, file_str)
    except Exception as e:
        #print(e)
        pass

def TopMost() :
    global topmost
    if topmost == True :
        print("topmost = False")
        window.attributes("-topmost", False)
        topmost = False
        return topmost

    if topmost == False :
        print("Topmost = True")
        window.attributes("-topmost", True)
        topmost = True
        return topmost
    
    else :
        print(str(topmost))
        print("a")


text = ScrolledText(window)
text.config(background='#fff96d')
text.pack(fill=BOTH,expand=True)

topmost_var = tk.IntVar()
case = tk.Checkbutton(variable = topmost_var,activebackground="#fff96d",activeforeground="#fff96d",bg="#fff96d",command=TopMost)
case.config(text="Top Most",background='#fff96d')
case.pack(side=RIGHT, fill=Y)

menubar = Menu(window)
window.config(menu=menubar)

filemenu = Menu(menubar, tearoff=0)
filemenu.add_command(label="New", command=newfile, accelerator="Ctrl+N")
filemenu.add_command(label="Open", command=openfile, accelerator="Ctrl+O")
filemenu.add_command(label="Save", command=savefile, accelerator="Ctrl+S")
filemenu.add_command(label="Save as", command=savefileas, accelerator="Ctrl+Alt+S")
filemenu.add_separator()
filemenu.add_command(label="Exit", command=quit, accelerator="Ctrl+Q")
window.bind_all("<Control-q>", quit)
window.bind_all("<Control-n>", newfile)
window.bind_all("<Control-o>", openfile)
window.bind_all("<Control-s>", savefile)
window.bind_all("<Control-Shift-s>", savefileas)
menubar.add_cascade(label="File", menu=filemenu)

settings_menu = Menu(menubar, tearoff=0)
settings_menu.add_command(label="Use Post-it by default for .post-it files", command=file_assos)
menubar.add_cascade(label="Settings", menu=settings_menu)

topmost = topmost_var.get()

if __name__ == "__main__":
   main(sys.argv[1:])

try :
    openfile_arg()
except Exception as e:
    print(e)
    pass

window.mainloop()