import os,sys
import binascii
import struct
import re
class Row():
    def __init__(self,loc,block,label,code,value,obj):
        self.loc = loc
        self.block = block
        self.label = label
        self.code = code
        self.value = value
        self.obj = obj
def SUB(a,b,flag):#減法後十進制轉十六進制
#     print("a:" + str(a))
#     print("b:" + str(b))
    if(int(a)-int(b)>=0):
        return '{0:x}'.format(int(a)-int(b)).zfill(4)
    else:
        temp = (a-b) * -1
        if(flag == 1):
            '{0:x}'.format(int("FFFF",16)-temp+1).zfill(4)
        else:
            return '{0:x}'.format(int("FFF",16)-temp+1).zfill(4)
def symbol(a,mode):#取值模式
    if(a.value == ""):
        return a
    if(a.value[0] == "#"):
        a.obj = '{0:x}'.format(int(str(a.obj),16) + int('10000',16))
    elif(a.value[0] == "@"):
        a.obj = '{0:x}'.format(int(str(a.obj),16) + int('20000',16))
    elif(a.code[0] == "+"):
        a.obj = '{0:x}'.format(int(str(a.obj),16) + int('100000',16))
    elif(a.value[len(a.value)-1] == "X"):
        a.obj = '{0:x}'.format(int(str(a.obj),16) + int('8000',16))
    else:
        a.obj = str('{0:x}'.format(int(str(a.obj),16) + int('30000',16))).zfill(6)
    
    if(mode == "PC" and a.code[0] != "+"):
        a.obj = str('{0:x}'.format(int(str(a.obj),16) + int('2000',16))).zfill(6)
    elif(mode == "BASE" and a.code[0] != "+"):
        a.obj = str('{0:x}'.format(int(str(a.obj),16) + int('4000',16))).zfill(6)
    elif(mode == "BASE" and a.code[0] == "+"):
        a.obj = str('{0:x}'.format(int(str(a.obj),16) + int('400000',16))).zfill(6)
    else:
        a.obj = str('{0:x}'.format(int(str(a.obj),16) + int('200000',16))).zfill(6)
    return a
def correctPosition(block,position):#將program block的位置轉成正確位置
    if(block == 0):
        return position
    elif(block == 1):
        return '{0:x}'.format(int(str(position),16) + int(str(ProgramBlockTable["CDATA"][2]),16))
    elif(data[i].block == "NULL"):
        return "NULL"
    else:
        return '{0:x}'.format(int(str(position),16) + int(str(ProgramBlockTable["CBLKS"][2]),16))
def decideCode(self,block,previous):#決定program block 的位置和值
    #flag是要記錄上一個的值，如果有use要特別取ProgramEnd的紀錄值
    ProgramEnd[block] = self.loc
    if(self.code =="USE"):
#         print(str(block) + " " + str(self.code) + " " + str(self.value) + " " + str(ProgramEnd[block]))
        if(self.value == "CDATA"):
            self.block = 1
        elif(self.value == "CBLKS"):
            self.block = 2
        else:
            self.block = 0
        self.loc = ProgramEnd[self.block]
        flag = ProgramEnd[self.block]
    else:
        flag = self.loc
        self.block = block
    return flag,self.block
def decideOperation(data):#處理Expression
    OperationWeights = {"+":1,"-":1,"*":2,"/":2,"(":0,")":5}
    number = 0
    data = re.split(r"([|+|*|-|-|/|(|)])",data)
#     print(data)
    OperationStack = []
    ValueStack = []
    operationTop = -1
    decideRelative = 0
    for i,k in enumerate(data):
        if(k == "" or k == "("):
            continue
        elif(k=="+" or k=="-" or k=="*" or k=="/"):#是運算式
#             print("我是運算式:" + str(k))
            if(len(OperationStack)!=0):#如果OperationStack不是空
                pre = OperationWeights[str(OperationStack[operationTop])]
                now = OperationWeights[str(k)]
                if(now<pre):
                    OperationStack,ValueStack,operationTop = CalculateTheAnswer(OperationStack,ValueStack,operationTop,0)
                OperationStack.append(str(k))
                
            else:
                OperationStack.append(str(k))        
            operationTop = operationTop + 1
        elif( k == "(" or k == ")"):
            if(k==")"):
                OperationStack,ValueStack,operationTop = CalculateTheAnswer(OperationStack,ValueStack,operationTop,1)
        else:
            if(k in SYMBOLTABLE):
                k = SYMBOLTABLE[str(k)][2]
                decideRelative = decideRelative + 1
            ValueStack.append(k)
    OperationStack,ValueStack,operationTop = CalculateTheAnswer(OperationStack,ValueStack,operationTop,1)
    return ValueStack[0],decideRelative
def CalculateTheAnswer(OperationStack,ValueStack,operationTop,flag):#處理Expression詳細運算
                                                                    #flag是用來判斷要不要取完
    while(operationTop != -1):
        a = int(ValueStack[operationTop])
        b = int(ValueStack[operationTop+1])
        ValueStack.pop()
        if(OperationStack[operationTop]=="+"):
            ValueStack[operationTop] = a+b
        elif(OperationStack[operationTop]=="-"):
            ValueStack[operationTop] = a-b
        elif(OperationStack[operationTop]=="*"):
            ValueStack[operationTop] = a*b
        else:
            ValueStack[operationTop] = a/b
        operationTop = operationTop - 1
        OperationStack.pop()
        if(flag == 0):
            break
    return OperationStack,ValueStack,operationTop
def add(code,value,add):#location的加法運算
    if(code == "RESW"):
        value,decideRelative = decideOperation(value)
#         print(value)
        return int(value)*3
    elif(code == "RESB"):
        value,decideRelative = decideOperation(value)
        return value
    elif(code == "*" or code == "BYTE"):
        if(value[0]=="X"):
#             print(str(value)+str((len(value)-3)/2))
            return (len(value)-3)//2
        else:
#             print(str(value)+str(len(value)-3))
            return len(value)-3
    else:
        return add
    
    
data = []
i = 0
A = 0
B = 0
C = 0
ProgramEnd =[0]*3
BLOCK = 0
A = 0
B = 0
C = 0
LITTAB_number = 0
org = Row("0","","","","","")
LITTAB = {}
SYMBOLTABLE = {}
BASETABLE = {}
EQUTABLE = {}
LEETTERTABLE = {"X":1,"A":0,"S":4,"T":5}
codeDict = {"ADD":["18",3],"DIV":["24",3],"MUL":["20",3],
            "COMP":["28",3],"J":["3C",3],"SUB":["1C",3],
            "JEQ":["30",3],"JGT":["34",3],"JLT":["38",3],
            "JSUB":["48",3],"LDA":["00",3],"LDB":["68",3],
            "LDCH":["50",3],"LDF":["70",3],"LDL":["08",3],
            "LDS":["6C",3],"LDT":["74",3],"LDX":["04",3],
            "RSUB":["4C",3],"STA":["0C",3],"STB":["78",3],
            "STCH":["54",3],"STF":["80",3],"STI":["D4",3],
            "STL":["14",3],"STS":["7C",3],"STSW":["E8",3],
            "STT":["84",3],"STX":["10",3],"TD":["E0",3],
            "RD":["D8",3],"TIX":["2C",3],"WD":["DC",3],
    #------------------------------------------------------------------------------------------------------
            "ADDR":["90",2],"CLEAR":["B4",2],"COMPR":["A0",2],
            "DIVR":["9C",2],"MULR":["98",2],"SUBR":["94",2],
            "TIXR":["B8",2],
    #------------------------------------------------------------------------------------------------------
            "START":["NULL",0],"END":["NULL",0],
            "RESB":["NULL",0],"RESW":["NULL",0],
    #------------------------------------------------------------------------------------------------------
            "WORD":["00",3],"BYTE":[" ",0],"EQU": [" ",0],
            "*": [" ",0],"USE": [" ",0],"LTORG": [" ",0]}
    #------------------------------------------------------------------------------------------------------
a = input("input:")
file = open(a,'r')
for line in file.readlines():
    data.append(Row("0","","","","",""))
    if(line[0]=="."):
        continue
    data[i].label = line[0:7].replace(" ","").replace("\n","")
    data[i].code = line[7:15].replace(" ","").replace("\n","")
    data[i].value = line[15:35].replace(" ","").replace("\n","")
    #------------------------------------------------------------------------------------------------------
    #如果遇到要換區塊換區塊
    flag,BLOCK = decideCode(data[i],BLOCK,data[i-1]) 
    #------------------------------------------------------------------------------------------------------
    if(data[i].value!=""):
        if(str(data[i].value)[0] == '='):
            if (data[i].value[1]=='C'): 
                temp = binascii.b2a_hex(str(data[i].value[3:len(data[i].value)-1]).encode('utf-8'))
                a = len(data[i].value)-4 
            else:
#                 print(data[i].value)
                temp = str(data[i].value[3:len(data[i].value)-1])
                a = (len(data[i].value)-4)/2
            LITTAB[str(LITTAB_number)] = [str(data[i].value[1:]),temp,a,data[i].loc]
#             print(LITTAB)
            LITTAB_number = LITTAB_number + 1
    #------------------------------------------------------------------------------------------------------
    if(data[i].code != "END" and data[i].code != "ORG" and data[i].code != "LTORG" and data[i].code != "BASE"):
        if(data[i].code[0] == "+"):
            data[i+1].loc = '{0:x}'.format(int(str(flag),16) + int(1) + int(add(data[i].code[1::],data[i].value,codeDict[str(data[i].code)[1::]][1])))
#             print(int(str(flag),16) + int(1) + int(add(data[i].code[1::],data[i].value,codeDict[str(data[i].code)[1::]][1])))    
        else:
            if(data[i].code == "USE"):
                data[i].loc = "NULL"
                data[i].block = "NULL"
#             print(str(flag) + "+" + str(add(data[i].code,data[i].value,codeDict[str(data[i].code)][1])))    
            data[i+1].loc = '{0:x}'.format(int(str(flag),16) + int(add(data[i].code,data[i].value,codeDict[str(data[i].code)][1])))
#     ------------------------------------------------------------------------------------------------------          
    elif(data[i].code == "BASE"):
        BASETABLE[str(i)] = [BLOCK,data[i].loc,data[i].value]
        data[i+1].loc = data[i].loc
        data[i+1].block = data[i].block
    elif(data[i].code =="ORG"):
        if(data[i].value == "*"):
            data[i+1].loc = org.loc
            data[i+1].block = org.block
        else:
            value,decideRelative = decideOperation(data[i].value)
            data[i+1].loc = '{0:x}'.format(int(value))
            data[i+1].block = BLOCK
            org.loc = data[i].loc
            org.block = data[i].block
        data[i].loc = "NULL"
        data[i].block = "NULL"
    #------------------------------------------------------------------------------------------------------ 
    elif(data[i].code == "LTORG" or data[i].code == "END"):
        if(data[i].code =="LTORG"):
            data[i+1].loc = data[i].loc
#             print('%-2s %-4s %-8s %-8s %-8s %-15s %-8s' % (i,str(data[i].loc).zfill(4),data[i].block,data[i].label,data[i].code,data[i].value,data[i].obj))
        for j,k in enumerate(LITTAB):
            i = i + 1
            data[i].label = "*"
            data[i].block = data[i-1].block
            data[i].code = "*"
            data[i].value = "=" + str(LITTAB[str(k)][0])
            data[i+1].loc = '{0:x}'.format(int(str(data[i].loc),16) + int(LITTAB[str(k)][2]))
            SYMBOLTABLE[data[i].value] = [i,data[i].block,data[i].loc]
#             print('%-2s %-4s %-8s %-8s %-8s %-15s %-8s' % (i,str(data[i].loc).zfill(4),data[i].block,data[i].label,data[i].code,data[i].value,data[i].obj))
        LITTAB = {}
    else:
        print("talk")
    #------------------------------------------------------------------------------------------------------
    if(data[i].label != ""):#紀錄Label
        if(data[i].code == "EQU" and data[i].value != "*"):
            value,decideRelative = decideOperation(data[i].value)
            if(decideRelative%2==0):
                data[i].block = "NULL"
            EQUTABLE[data[i].label] = [i,BLOCK,value]
            SYMBOLTABLE[data[i].label] = [i,BLOCK,value]
#             print(EQUTABLE)
        else:
            SYMBOLTABLE[data[i].label] = [i,BLOCK,data[i].loc]
    #------------------------------------------------------------------------------------------------------
#     print('%-2s %-4s %-8s %-8s %-8s %-15s %-8s' % (i,str(data[i].loc).zfill(4),data[i].block,data[i].label,data[i].code,data[i].value,data[i].obj))
    i = i + 1
length = i
ProgramBlockTable = {"default":[0,"0",ProgramEnd[0]],
                     "CDATA":[1,ProgramEnd[0],ProgramEnd[1]],
                     "CBLKS":[2,'{0:x}'.format((int(str(ProgramEnd[0]),16) + int(str(ProgramEnd[1]),16))),ProgramEnd[2]]}
#--------------------------------------------------------------------------------------------------------------------------
for i,k in enumerate(SYMBOLTABLE):
    if(k in EQUTABLE):
        SYMBOLTABLE[k][1] = 0
# --------------------------------------------------------------------------------------------------------------
#XE_OK_01.txt
#XE_hard.txt


H = ""
T = []
M = []
E = []
number = 0
count = 0
TcardNumber = 0
for i,k in enumerate(data):
    Extend  = 0
    #------------------------------------------------------------------------------------------------------
    if(i == length):
        break
    if(k.code == "START"):
        H = "H,"+ str(k.label) +","+ str(k.loc).zfill(4) + ","+str('{0:x}'.format(int(str(ProgramEnd[0]),16) + int(str(ProgramEnd[1]),16) + int(str(ProgramEnd[1]),16)))
        k.obj = "NULL"
#         print('%-2s %-4s %-8s %-8s %-8s %-8s %-15s %-8s' % (i,str(k.loc).zfill(4),k.block,correctPosition(k.block,k.loc).zfill(4),k.label,k.code,k.value,k.obj))
        continue
    elif(k.code == "END"):
        E = "E," + str(k.value)
    elif(k.code == "USE" or k.code == "RESW" or k.code == "EQU" or k.code == "LTORG" or k.code == "ORG" or k.code == "BASE"):
        k.obj = "NULL"
    elif(k.code == "COMPR"):
        behind = str(codeDict[str(k.code)][0])
        k.obj = behind + str(LEETTERTABLE[str(k.value[0])]) + str(LEETTERTABLE[str(k.value[len(k.value)-1])])
    elif(k.code == "CLEAR"):
        behind = str(codeDict[str(k.code)][0])
        k.obj = behind + str(LEETTERTABLE[str(k.value)]) + "0"
    elif(k.code == "RSUB"):
        k.obj = str(codeDict[str(k.code)][0]) + "0000"
    elif(k.value == ""):
        k.obj = "000000"
    elif(k.code == "RESB"):
        k.obj = "NULL"
    elif(k.code == "BYTE"):
        if(k.value[0] == 'C'):
            k.obj = binascii.b2a_hex(str(data[i].value[3:len(data[i].value)-1]).encode('utf-8'))
        else:
            k.obj = k.value[2:len(k.value)-1]
    elif(k.value[0] == "#" or k.value[0] == "@" or k.code[0] == "+" or k.value in SYMBOLTABLE or k.value[0:len(k.value)-2] in SYMBOLTABLE):
        #如果value是在SYMBOLTABLE裡
        if(k.value in SYMBOLTABLE or k.value[1::] in SYMBOLTABLE or k.value[0:len(k.value)-2] in SYMBOLTABLE):
    #------------------------------------------------------------------------------------------------------
            if(k.value[1::] in SYMBOLTABLE):
                NOW = correctPosition(SYMBOLTABLE[k.value[1::]][1],SYMBOLTABLE[k.value[1::]][2])
                Mcard = "M," + str(k.loc).zfill(6) +  ",+" + str(k.value[1::])
            elif(k.value[0:len(k.value)-2] in SYMBOLTABLE):
                NOW = correctPosition(SYMBOLTABLE[k.value[0:len(k.value)-2]][1],SYMBOLTABLE[k.value[0:len(k.value)-2]][2])
                Mcard = "M," + str(k.loc).zfill(6) + ",+" + str(k.value[0:len(k.value)-2])
            elif(k.value in SYMBOLTABLE):
                NOW = correctPosition(SYMBOLTABLE[k.value][1],SYMBOLTABLE[k.value][2])
                if(k.code != "*"):
                    Mcard = "M," + str(k.loc).zfill(6) + ",+" + str(k.value)
            M.append(Mcard)
            #======================================================================================================
            if(k.code[0] == "+"):#有加號
                behind = str(codeDict[str(k.code[1::])][0]) + "00"
            else:
                behind = str(codeDict[str(k.code)][0])
            #======================================================================================================
            if(data[i].code[0] != "+"):
                PC = '{0:x}'.format((int(str(correctPosition(data[i].block,data[i].loc)),16)) + int(add(data[i].code,data[i].value,codeDict[str(data[i].code)][1])))
            else:#沒有+號後面是label
                PC = '{0:x}'.format((int(str(correctPosition(data[i].block,data[i].loc)),16)) + int(1) + int(add(data[i].code[1::],data[i].value,codeDict[str(data[i].code[1::])][1])))
#             print("behind:" + str(behind))
#             print("Now:" + str(behind))
    #------------------------------------------------------------------------------------------------------   
            if(k.code[0] == "+" and k.value[1::] in SYMBOLTABLE):#+號後面是字符直接放
                k.obj = behind +str(correctPosition(SYMBOLTABLE[k.value[1::]][1],SYMBOLTABLE[k.value[1::]][2]))
            elif(k.code[0] == "+" and k.value in SYMBOLTABLE):#+號後面是字符直接放
                k.obj = behind +str(correctPosition(SYMBOLTABLE[k.value][1],SYMBOLTABLE[k.value][2]))
            elif( (int(str(NOW),16)-int(str(PC),16) > 1000 or int(str(NOW),16)-int(str(PC),16) < -1000) and Extend == 0):
                small = i
                flag = 0
                for n,m in enumerate(BASETABLE):
#                     print(closedBasePosition)
                    if(flag==0):
                        closedBasePosition = m
                        flag = 1
                    if(int(closedBasePosition) - i < small):
                        closedBasePosition = m
                if(BASETABLE[str(closedBasePosition)][2] in SYMBOLTABLE):
                    BASE = correctPosition(SYMBOLTABLE[BASETABLE[str(closedBasePosition)][2]][1],SYMBOLTABLE[BASETABLE[str(closedBasePosition)][2]][2])
                else:
                    BASE = BASETABLE[str(closedBasePosition)][2]
                    temp = "BASE"
#                 print(NOW)
#                 print(BASE)
                k.obj = behind + SUB(int(str(NOW),16),int(str(BASE),16),0)
            else:
#                 print(NOW)
#                 print(PC)
                temp = "PC"
                if(k.code[0] == "+"):
                    k.obj = behind + SUB(int(str(NOW),16),int(str(PC),16),1)
                else:
                    k.obj = behind + SUB(int(str(NOW),16),int(str(PC),16),0)
        else:#如果value是數字
            if(k.code[0] == "+"):
                behind = str(codeDict[str(k.code[1::])][0]) + "00"
                k.obj = behind + '{0:x}'.format(int(k.value[1::]))
            else:
                k.obj = str(codeDict[str(k.code)][0]) + str(int(str(k.value[1::]),16)).zfill(4)
#         print(k.obj)
        k = symbol(k,temp)
        k.obj = str(k.obj).zfill(6)
    #------------------------------------------------------------------------------------------------------  
    elif(k.value[0] == "="):
        NOW = correctPosition(SYMBOLTABLE[k.value[1:len(k.value)]][1],SYMBOLTABLE[k.value[1:len(k.value)]][2])
        PC = '{0:x}'.format((int(str(correctPosition(data[i].block,data[i].loc)),16)) + int(add(data[i].code[1::],data[i].value,codeDict[str(data[i].code[1::])][1])))
        behind = str(codeDict[str(k.code)][0])
        k.obj = behind + str(SUB(int(str(NOW),16),int(str(PC),16))).zfill(4)
    else:
        behind = str(codeDict[str(k.code)][0])
        if(k.value in LEETTERTABLE):
            k.obj = behind + str(LEETTERTABLE[k.value]).zfill(2)
        else:
            k.obj = behind + "0000"
    #------------------------------------------------------------------------------------------------------
    print('%-2s %-4s %-8s %-8s %-8s %-8s %-15s %-8s' % (i,str.upper(str(k.loc)).zfill(4),k.block,str.upper(str(correctPosition(k.block,k.loc).zfill(4))),k.label,k.code,k.value,str.upper(str(k.obj))))
#     print(ProgramBlockTable)

for i,k in enumerate(data):
    if(k.obj != "NULL"):
        count = count + len(k.obj)
        TcardNumber = TcardNumber + 1
        if(count+len(data[i+1].obj)>30 or data[i+1].obj == "NULL" or data[i+1].code == "END"):
            Tposition = i-TcardNumber+1
#             print("Tposition:" + str(Tposition))
            Tcard = "T," + str(correctPosition(data[Tposition].block,data[Tposition].loc)).zfill(6) + "," + str('{0:x}'.format(int(count)))
            for j in range(i-TcardNumber+1,i+1):
                Tcard =  Tcard +  ","  +str(data[j].obj)
#             print(Tcard)
            T.append(Tcard)
            TcardNumber = 0
            count = 0
    if(k.code == "END"):
        break
if os.path.exists("card.txt"):
    os.remove("card.txt")
a = open("card.txt", 'w')
a.writelines(str(H))
a.writelines("\n")
for i in range(len(T)):
    a.writelines(T[i])
    a.writelines("\n")
a.writelines(E)
a.close()
if os.path.exists("list.txt"):
    os.remove("list.txt")
file_write_obj = open("list.txt", 'w')


for i,k in enumerate(data):
    #index
    file_write_obj.writelines('%-4s' %i)
    #location
    if(k.loc == "NULL"):
        file_write_obj.writelines("%-6s" %(" "))
    else:
        file_write_obj.writelines('%-6s' %str(k.loc).zfill(4))
    #block
    if(k.block == "NULL"):
        file_write_obj.writelines("%-3s" %(" "))
    else:
        file_write_obj.writelines('%-3s' %k.block)    
    #correctPosition
    if(k.block == "NULL"):
        file_write_obj.writelines("%-8s" %(" "))
    else:
        file_write_obj.writelines('%-8s' %str.upper(str(correctPosition(k.block,k.loc).zfill(4))))   
    #label,code,value
    file_write_obj.writelines('%-8s%-8s%-15s' %(k.label,k.code,str(k.value)))
    #object code
    if(k.obj == "NULL"):
        file_write_obj.writelines("%-8s" %(" "))
    else:
        file_write_obj.writelines('%-8s' %(str.upper(str(k.obj))))
#     print('%-2s %-4s %-8s %-8s %-8s %-8s %-15s %-8s' % (i,str(k.loc).zfill(4),k.block,correctPosition(k.block,k.loc).zfill(4),k.label,k.code,k.value,k.obj))
    file_write_obj.write('\n')
    if(k.code == "END"):
        break
file_write_obj.close()
print("Success")

#XE_OK_01.txt
#XE_hard.txt