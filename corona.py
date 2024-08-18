a = input("please enter your contry name to :")

# import colorama

# print(colorama.Fore.GREEN+("LORD"))

from covid import Covid

corona = Covid()

c = corona.get_status_by_country_name(a)

for x in c:
    print(x,":",c[x])