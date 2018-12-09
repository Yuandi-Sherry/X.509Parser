# coding=utf-8
import sys


ALGORITHM = {
    '1.2.840.10040.4.1': 'DSA',
    "1.2.840.10040.4.3" : "sha1DSA",
    "1.2.840.113549.1.1.1" :"RSA",
    "1.2.840.113549.1.1.2" : "md2RSA",
    "1.2.840.113549.1.1.3" : "md4RSA",
    "1.2.840.113549.1.1.4" : "md5RSA",
    "1.2.840.113549.1.1.5" : "sha1RSA",
    '1.3.14.3.2.29': 'sha1RSA',
    '1.2.840.113549.1.1.13': 'sha512RSA',
     '1.2.840.113549.1.1.11':'sha256RSA'
}
RDN = {
    "2.5.4.6" : "Country: ",
    "2.5.4.8" : "Sate or province name: ",
    "2.5.4.7" : "Locality: ",
    "2.5.4.10" : "Organization name: ",
    "2.5.4.11" : "Organizational Unit name: ",
    "2.5.4.3" : "Common Name: "
}
TYPE = {
    1:'BOOL',
    2:'INT',
    3:'Bit String',
    4:'Byte String',
    5:'NULL',
    6:'Object',
    0x13:'Printable String',
    0x17:'Time',
    0x18:'Time',
    0x30:'Constructor',
    0x31:'Constructor'
}

INTEGEER = {
    0: 'VERSION: ',
    1: 'default version: ',
    2: 'SERIAL NUMBER: ',
    3: '    args needed in SIGNATURE ALGORITHM: ',
    4: '    args needed in CERTIFICATE ALGORITHM: '
}

BITSTRING = {
    0: '    Subject Public Key: \n   ',
    1: 'Certificate Signature: \n   '
}

PRINTABLE = {
    0: 'PRINTABLE: ',
    1: 'PRINTABLE version: ',
    2: 'PRINTABLE NUMBER: '
}

OBJECT = {
    0:'SIGNATURE ALGORITHM: ',
    1:'ISSUER: ',
    2:'SUBJECT: ',
    3:'SUBJECT PUBLIC KEY INFO: \n    Algorithm: ',
    4:'Certificate Signature Algorithm: : '
}

NULL = {
    0: '    args needed in SIGNATURE ALGORITHM: ',
    1: '    args needed in PUBLIC KEY ALGORITHM: ',
    2: '    args needed in CERTIFICATE ALGORITHM: '
}

TIME = {
    0: '    not before: ',
    1: '    not after: '
}


VERSION = {
    '0': 'V1',
    '1': 'V2',
    "2": 'V3'
}

class Certificate(object):
    def __init__(self, filePath):
        self.filePath = sys.path[0] + '/' + filePath
        self.file = open(self.filePath, 'rb')
        # self.file.read(2)
        # self.version : INTGEGER
        # self.serialNumber : INTEGER
        self.tag = False
        self.count = -1
        # for output title
        self.intCount = 0
        self.bitStringCount = 0
        self.nullCount = 0
        self.objCount = 0
        self.printableStringCount = 0
        self.timeCount = -1
        self.followObj  = False
        self.extension = False


        # 按字节数读取
        # #print(self.file.read(2))
        # #print(self.file.read(2))
        # #print(self.file.read(2))
        # #print(self.file.read(2))
        self.savedStr = ""

    def main(self):
        tempStr = ""
        # 读取一个字节
        if(self.tag == False):
            tempStr = self.file.read(1)
            if(len(tempStr) != 0):
                self.type = ord(tempStr)
            else:
                print('end of file')
                exit(0)
        else:
            self.tag = False
        #print('type:', self.type)
        if self.type < 0x80:
            if self.type == 1:
                print("is boolean")
            elif self.type == 2:
                tempStr = self.dealInt()
            elif self.type == 3:
                if self.extension == True:
                    tempStr = self.dealPrintableStr()
                else:
                    tempStr = self.dealBitString()
            elif self.type == 4:
                print('is byte tempStr')
            elif self.type == 5:
                tempStr = self.dealNull()
            elif self.type == 6:
                tempStr = self.dealObject()
            elif self.type == 0x13 or self.type == 0x0c:
                tempStr = self.dealPrintableStr()
            elif self.type == 0x17 or self.type == 0x18:
                tempStr = self.dealTime()
            elif self.type == 0x30 or self.type == 0x31:
                self.dealConstructor()
            elif self.type == 0:
                self.dealTag()
            else:
                print("--------------------error--------------------")
            self.getResult(tempStr)
                # exit(0)
        elif self.type >= 0xa0:
            # explicit TAG
            tag = self.type - 0xa0
            if(tag == 0):
                self.count = 0 # version get!
                # print("------------get version-----------")
            elif tag == 3:
                self.extension = True

            self.type = tag
            self.tag = True
            self.main()
        else: # 隐式TAG
            tag = self.type - 0x80
            if tag == 1:
                print ("--------------------issuerUniqueID--------------------")
            elif tag == 2:
                print ("--------------------subjectUniqueID--------------------")
            self.type = tag
            self.tag = True
            self.main()

    def getResult(self, tempStr):
        if self.extension == True:
            print("--------------------EXTENSION PART--------------------")
            print(tempStr)
            print("--------------------EXTENSION End--------------------")
            self.extension = False
            return
        if self.type == 2:
            if self.intCount >= len(INTEGEER):
                print(tempStr)
                return
            if self.intCount == 0:
                tempStr = VERSION[tempStr]
            print(INTEGEER[self.intCount],tempStr)
            self.intCount+=1
        elif self.type == 3:
            if self.bitStringCount >= len(BITSTRING):
                print(tempStr)
                return
            print(BITSTRING[self.bitStringCount], tempStr)
            self.bitStringCount+=1
        elif self.type == 5:
            if self.nullCount >= len(NULL):
                print('NULL')
                return
            print(NULL[self.nullCount], tempStr)
            self.nullCount += 1
            self.intCount +=1
        elif self.type == 6:
            if self.objCount >= len(OBJECT):
                if RDN.get(tempStr,-1) != -1:
                    tempStr = RDN[tempStr]
                # Algorithm
                elif ALGORITHM.get(tempStr, -1)!= -1:
                    tempStr = ALGORITHM[tempStr]
                print(tempStr)
                return
            # Name
            if RDN.get(tempStr,-1) != -1:
                tempStr = RDN[tempStr]
                if tempStr == 'Country: ':
                    print(OBJECT[self.objCount])
                    self.objCount += 1
                self.followObj = True
                print('    ', tempStr)
            # Algorithm
            elif ALGORITHM.get(tempStr, -1)!= -1:
                tempStr = ALGORITHM[tempStr]
                print(OBJECT[self.objCount], tempStr)
                self.objCount += 1
        elif self.type == 0x17 or self.type == 0x18:
            if self.timeCount == -1:
                print("VALIDITY:")
                self.timeCount +=1
                print(TIME[self.timeCount], tempStr)
                self.timeCount +=1
            else:
                print(TIME[self.timeCount], tempStr)
        elif self.type == 0x13 or self.type == 0x0c:
            if self.followObj == False:
                print(PRINTABLE[self.printableStringCount], tempStr)
                self.printableStringCount+=1
            else:
                self.followObj = False
                print('        ', tempStr)

    def dealTag(self):
        length = ord(self.file.read(1))
        if(length > 0x80):
            trueLength = self.getTrueLength(length)
        self.main()

    def dealConstructor(self):
        length = ord(self.file.read(1))
        trueLength = self.getTrueLength(length)
        for i in range(0, trueLength):
            self.main()

    def dealBitString(self):
        tempStr = ""
        length = ord(self.file.read(1))
        trueLength = self.getTrueLength(length)
        for i in range(0, trueLength):
            temp = hex(ord(self.file.read(1)))[2:]
            if len(temp) != 2:
                temp = '0' + temp
            tempStr += temp
        return tempStr

    def dealInt(self):
        tempStr = ""
        length = ord(self.file.read(1))
        trueLength = self.getTrueLength(length)
        for i in range(0, trueLength):
            tempStr += hex(ord(self.file.read(1)))[2:]
        return tempStr

    def dealObject(self):
        tempStr = ""
        length = ord(self.file.read(1))
        trueLength = self.getTrueLength(length)
        firstByte =  ord(self.file.read(1))
        v1 = int(firstByte/40)
        v2 = firstByte - v1*40
        tempStr += str(int(v1))  + '.'
        tempStr += str(int(v2))
        i = 0
        vn = 0 # vn
        while i < trueLength - 1:
            tempByte = ord(self.file.read(1))
            while(tempByte & 0x80 != 0): # 不是最后一个字节
                tempByte &= 0x7F
                i += 1
                vn *= 128
                vn += tempByte
                # 读入下一个字节
                tempByte = ord(self.file.read(1))
            # 是最后一个字节
            vn *= 128
            vn += tempByte
            tempStr += '.' + str(int(vn))
            # print('v_n', vn, " ", i)
            # 读入下一个字节
            vn = 0
            i += 1
        return tempStr

    def dealPrintableStr(self):
        tempStr = ""
        length = ord(self.file.read(1))
        trueLength = self.getTrueLength(length)
        for i in range(0, trueLength):
            tempStr +=  str(self.file.read(1))[2:-1]
        return tempStr

    def dealNull(self):
        self.file.read(1)

    def dealTime(self):
        tempStr = ""
        length = ord(self.file.read(1))
        trueLength = self.getTrueLength(length)
        for i in range(0, trueLength):
            tempStr += str(self.file.read(1))[2:-1]
        return tempStr

    def getTrueLength(self, length):
        trueLength = 0
        if length > 0x80: # 长形式
            length -= 0x80
            for i in range(0, length):
                trueLength *= 256
                trueLength += ord(self.file.read(1))
        else: #短形式
            trueLength = length
        return trueLength

if __name__ == "__main__":
    FILENAME = sys.argv[1]
    cer = Certificate (FILENAME)
    cer.main()
