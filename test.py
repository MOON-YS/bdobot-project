import pandas as pd

crnt_usr = pd.DataFrame(columns=['name','guild','id'])
crnt_usr.head(1)

server_data = pd.DataFrame(columns=['gld',
                                    'is_init','is_roleChecked', 
                                    'crnt_num', 'full_num',
                                    'update_ch',
                                    'td_info','crnt_usrs'])
server_data.head(1)

crnt_usr.loc[0]=["NAME1","GUILD",1234]
crnt_usr.loc[1]=["NAME2","GUILD",1234]
crnt_usr.loc[2]=["NAME3","GUILD",1234]
crnt_usr.loc[3]=["NAME4","GUILD",1234]
server_data.loc[0] = [1234, False, False, 50,50, 12351, 145, crnt_usr]
server_data.loc[0,"gld"] = 331
print((crnt_usr["name"]==123).any())

