
import math
import colorama
import pyfiglet





print(pyfiglet.figlet_format("mohasebey \n rabetey Fisa ghorais"))


print("a: ertefa : |")
print("b: vatar : \\")
print("c: gaede : ___")



porshesh_avalie = input("megdar kodam yek ra mikhahi :")

while porshesh_avalie=="":
    print("dobara megdary ke mikhahid bedast avarid ra vared khonid:\n")

    print("___________________________________")
    print("a: ertefa : |")
    print("b: vatar : \\")
    print("c: gaede : ___")
    print("__________________________")
    print("")

    print("_________ !!!!!!!!!!! ______________")
    print("agar nemikhahid Ctrl+C ra bezanid")
    print("_________ !!!!!!!!!!! ______________")

    print("")

    porshesh_avalie=input("megdar kodam yek ra mikhahi : \n ")

if porshesh_avalie == "a":
    print("pas megdar do ((B,C)) ra vared khon : ")
    
    
    
    ############################################### AMALIAT MARBOT BE MOTAGHAYER :b: #########################################
    b =input("vatar mosalas ((B)) / :")

    while b=="":
        print("retry")
        b = input("enter num :bayad hadaghal 2 megdar ra vared konid (B):")
        
    b = int(b)# line 146


    ######################################### AMALIAT MARBOT BE MOTAGHAYER :b: ################################################
                                             ##################################
    ########################################## AMALIAT MARBOT BE MOTAGHAYER :c: ###############################################                                         
    c =input("gaede mosalas ((C)) __ :")

    while c=="":
        print("retry")
        c = input("enter num :bayad hadaghal 2 megdar ra vared konid (C):")
        """
        amaliat marbot be :
            agar bar c megdary vared nashode bashad angah dobare tekre=ar kon 
            ta zamani ke C daray megdar bashad 
        """   
    c = int(c) # line 146   
    ########################################## AMALIAT MARBOT BE MOTAGHAYER :c: ###############################################
                                              ###################################
    
    b = b**2 # betavan do resandan baray fisaghors
    c = c**2 # betavan do resandan baray fisaghors

    amaliat = b-c # amaliat nahve bedast avardan javab


    ####################################################### modiriat khata ######################################################
    try:
        print("megdar A :",round(math.sqrt(amaliat),2))# chap kardan javab
    except:
        print("javam addy manfi bod:",amaliat)
    ####################################################### modiriat khata ######################################################


################################################ PAYAN BEDAST AVARDAN MOTHAGHAYER ((A))#########################################



##################################################                  #############################################################
                                    ##############                  #############################################################
                                    ############## payan kol bedast avardan megdar (A)###########################################
                                    ##############                  #############################################################
##################################################                  #############################################################                                    
elif porshesh_avalie == "b":
    print("pas megdar do ((A,C)) ra vared khon : ")


    ########################################### AMALIAT MARBOT BE MOTAGHEYER (a) ################################################
    a =input("ertefa mosalas ((A))  | :")

    while a=="":
        print("retry")
        a = input("dobare emthan khonid A:")

    a = int(a)# line 146
    ########################################### PAYAN MARBOT BE AMALIAT MOTAGHEYER (a) ##########################################

    ########################################### SHORO MOHASEBe MOTAGHAYER (c)         ##########################################
    c =input("gaede mosalas ((C)) __ :")

    while c=="":
        print("retry")
        c = input("dobare megdar ra vared khonid C:")

    c = int(c)# tabdil megdar STR(c) be INT(c) baray mohasebe

    a = a**2# betavan do resandan baray fisaghors
    c = c**2# betavan do resandan baray fisaghors

    amaliat = a+c# amaliat nahve bedast avardan javab
    
    ########################################### payan MOHASEBe MOTAGHAYER (c)         ###########################################

    
    print("megdar b :",round(math.sqrt(amaliat),2))

elif porshesh_avalie == "c":

    print("pas megdar ((A,B)) ra bego:")

    ########## SHoro ######################### AMALIAT MARBOT BE MOTAGHEYER (a) ################################################
    a = input("ertefae mosalas |:")    

    while a =="":
        print("retry")
        a = input("dobare megdar ra vared khonid A:")

    a = int(a) # line 146  
    ########### payan ################# AMALIAT MARBOT BE MOTAGHEYER (a) ########################################################


    ########### shoro ################# AMALIAT MARBOT BE MOTAGHEYER (c) ########################################################
    b = input("vatar mosalas \\:")

    while b=="":
        print("retry")
        b=input("dobare megdar ra vared khonid B:")

    b = int(b)# line 146   
    ########### PAYAN ################# AMALIAT MARBOT BE MOTAGHEYER (c) ########################################################

    a = a**2# betavan do resandan baray fisaghors
    b = b**2# betavan do resandan baray fisaghors


    amaliat = b-a# amaliat nahve bedast avardan javab

    ####################################################### modiriat khata ######################################################
    try :
        print("megdar A :",round(math.sqrt(amaliat),2))# CHAP JAVAB
    except:
        print("javam addy manfi bod:",amaliat)    
    ####################################################### modiriat khata ######################################################    
