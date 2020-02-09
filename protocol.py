协议采用socket或者http包装协议主体, 目前暂定采用socket包装.
协议主体一律采用json格式
首先包括一个"command"关键字(key), 指出这条通信的命令
之后再根据不同的命令有不同的key和格式
目前定下的命令有
* {"command":"login","user":["username","hashed_pwd"],"room":"roomnum"}
"hashed_pwd"是密码加上epoch至今分钟数经过SHA256之后的字符串
"roomnum"留空(就是""),表示要创建房间
* {"command":"login_suc","room":"roomnum","your_loc":"S","players":["player1_name","player2_name",...]}
"your_loc"是坐的位置, 暂定按加入顺序按SENW分配, "players"也按SENW顺序排好
登陆失败交给"error"命令处理
* {"command":"new_player","players":["player1_name","player2_name",...]}
"players"格式与login_suc中一样
* {"command":"shuffle","cards":["SA","H2","D3","C4",...]}
S(Spade), H(Heart), D(Diamond), C(Club)表示黑红方梅
A23456789JQK表示不同的牌
"cards"可以返回["SA","H2","D3","C4",...]也可以是"SA,H2,D3,C4,..."这样的格式, 你挑一个方便的
* {"command":"your_turn"}
* {"command":"my_choice","card":"SQ"}
* {"command":"new_card","cards":["S2","SQ",..],"start":"W"}
每次出一张新牌都会把这一圈已经出过的牌再按顺序重复一遍
"start"是这一圈开始的那一家的位置
* {"command":"trick_end","cards":["S2","SQ","SJ","SA"],"start":"W","winner":"N"}
* {"command":"game_end","scores":[0,50,200,0]}
"scores"也按SENW顺序排好
* {"command":"error","detail":"blabla"}
