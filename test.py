import pandas as pd
from verbalexpressions import VerEx
verbal_expression = VerEx()

crnt_usr = pd.DataFrame(columns=['name','guild','id'])


server_data = pd.DataFrame(columns=['gld',
                                    'is_init','is_roleChecked', 
                                    'crnt_num', 'full_num',
                                    'update_ch', 'role_attend',
                                    'td_info','crnt_usrs'])
server_data.head(1)


server_data.loc[0] = [1234, False, False, 50,50, 12351, 1234,145, crnt_usr.copy()]
server_data.loc[1] = [4567, False, False, 50,50, 12351,1234, 145, crnt_usr.copy()]
crt_idx = server_data.index[(server_data['gld'] == 4567)][0]

print(server_data.loc[crt_idx,"crnt_usrs"])

server_data.loc[crt_idx,"crnt_usrs"].loc[0] = ["NAME","GUILD","ID"]
server_data.loc[crt_idx,"crnt_usrs"].loc[1] = ["NAME","GUILD","ID"]
server_data.loc[crt_idx,"crnt_usrs"].loc[2] = ["NAME","GUILD","ID"]
server_data.loc[crt_idx,"crnt_usrs"].loc[3] = ["NAME","GUILD","ID"]

print(server_data.loc[crt_idx]["crnt_usrs"])

k = server_data.loc[crt_idx]["crnt_usrs"]

for l in range(0,len(k)):
    k.drop(l, axis=0, inplace=True)


server_data.loc[crt_idx,"crnt_usrs"] = pd.DataFrame(crnt_usr.loc[0])
print(crnt_usr)
print(server_data.loc[crt_idx]["crnt_usrs"])

