import pandas as pd
from verbalexpressions import VerEx
verbal_expression = VerEx()

crnt_usr = pd.DataFrame(columns=['name','guild','id'])
crnt_usr.head(1)

server_data = pd.DataFrame(columns=['gld',
                                    'is_init','is_roleChecked', 
                                    'crnt_num', 'full_num',
                                    'update_ch', 'role_attend',
                                    'td_info','crnt_usrs'])
server_data.head(1)

crnt_usr.loc[0]=["NAME1","GUILD",1234]
crnt_usr.loc[1]=["NAME2","GUILD",1234]
crnt_usr.loc[2]=["NAME3","GUILD",1234]
crnt_usr.loc[3]=["NAME4","GUILD",1234]
server_data.loc[0] = [1234, False, False, 50,50, 12351, 1234,145, crnt_usr]
server_data.loc[1] = [4567, False, False, 50,50, 12351,1234, 145, crnt_usr]
crt_idx = server_data.index[(server_data['gld'] == 4567)][0]
print(server_data.loc[crt_idx]["gld"])
server_data.loc[crt_idx,"gld"] = 5124

print(server_data.loc[crt_idx,"gld"])

tester = (verbal_expression.
            start_of_line().
            find('[').
            anything().
            find(']').
            anything().
            end_of_line()
)

test1 = "[아카라이브] 병풍"
test2 = "병풍"

if tester.match(test1):
    print(test1 + " is correct")
else:
    print(test1 + " is incorrect")
    
if tester.match(test2):
    print(test2 + " is correct")
else:
    print(test2 + " is incorrect")
