# X.509数字证书解析程序

## 运行方法

运行环境：windows 10 cmd

```
py parsingX509.py CertificateName.cer
```

## X.509证书结构描述

X.509的文件（这里是base64）以Type-Length-Value的方式存储了类型、长度和具体指，按照一定规则读取即可解析出其中的数字/字符串信息。按照一定的模式读取下去，并将每个读取到的类型和位置与下文`总体结构`中的每个项目进行匹配即可解析出完整证书。

### 总体结构

```
Certificate
    Version
    Serial Number
    Algorithm ID
    Issuer (CA’s name)
    Validity
        Not Before
        Not After
    Subject
    Subject Public Key Info
        Public Key Algorithm
        Subject Public Key
    Issuer Unique Identifier (Optional)
    Subject Unique Identifier (Optional)
    Extensions (Optional)
    Certificate Signature Algorithm
    Certificate Signature
```

### Version

```
整数0 -> 版本v1
整数1 -> 版本v2
整数2 -> 版本v3
```

### 序列号

整数

### 签名算法

AlgorithmIdentifier类型：

```
algorithm       OBJECT(x.x.x.....x)
parameters      ANY TYPE
```

这里需要在识别Object为一种算法的标识符之后，将其下一个读入的单元类型、长度和值作为该算法所需的参数

### Issuer, Subject

二者均由“属性类型和属性值”构成，其中键为Object对应的标识符，和算法的标识符不同的在于，这里对应的是属性类型。同理，将其下一个读入的单元作为刚才解析出的属性类型对应的属性值。

这里的属性类型一般包含：

```
Country(CN)
State or province name(ST)
Locality(L)
Organization name(O)
Organization Unit name(OU)
Common Name(CN)
```

### Validity

包含：

```
notBefore       Time
notAfter        Time
```

### Subject Public Key Info / Certificate Signature Algorithm， Certificate Signature

主体公钥信息包含算法和公钥两部分，其中算法部分和签名算法的类型相同，都是包含算法名称和算法参数两个项目。

主体公钥为字符串类型，直接按照16进制解析并去掉前缀`0x`即可。

>  Certificate Signature Algorithm, Certificate Signature这二者主体公钥信息的算法和公钥相对应，使用相同方法解析即可

### Optional(s)

这里根据输入的Tag如果大于`0xA0`，则应用显示标签解析；如果Tag大于`0x80`但小于`0xa0`则用隐式标签解析。

## 数据结构

这段程序中使用的数据结构主要为字节数组，将文件的打开方式设置为按字节读取。每个读取单元由其类型和长度决定，主要以Type - Length - Value为大体结构：

### Type

需要解析的数据类型，主要包括Int, BitString, PrintableString, Object, Time等简单类型

> 这里的BitString和PrintableString的不同之处在于BitString直接输出每个字节对应的两个十六进制，而PrintableString则需输出该十六进制数在ASCII码表中对应的字符，直接进行显示。
>
> BitString常用于显示密钥，而Printable用于显示Issuer和Subject的属性值，以及Extension的内容（虽然Extension由于编码格式问题仍然会解析出乱码的问题

### Length

需要解析的值的长度，一般分为大于等于`0x80`（长类型）和小于`0x80`（短类型）两种情况。由于一个字节最多表示0~255的长度，但若所需的结果超过了这一范围，则需要使用长类型进行标识，即Length位置对应的字节减去`0x80`表明了接下来多少个字节仍然是Length的表示，用接下来的字节进行大端模式计算，并能得到真正的值的长度。接下来进行值的读取，并根据类型确定读取的自己的转码方式（十进制/十六进制/可显示字符...）

### Value

value的确定方式对于每种类型互不相同，Int, BitString和Time解析为十六进制数的后两位字符，PrintableString解析为ASCII码字符集中字符，Object和生成类型的计算方式相对复杂很多。

#### Object

> 假设所求的Object格式为：v1, v2, v3, ..., vn

按照长度读取一定长度的字节，第一个字节为`v1*40+v2`，由此计算出v1和v2，与其他类型不同是这里需要用十进制的方式存储为v1(base10). v2(base10)的字符串。从v3开始的字符串需要根据后续字节的最高位判断，如果最高位为1，则说明当前字节并非这个vi的最后一个字节；如果最高位为0，说明当前字节为这个vi的最后一个字节。根据直到最后一个字节的所有字节根据先读取到的为最高位的方式，计算出十进制数。

将所有的vi组合再一次构成：v1.v2.....vn的形式，到Object数组中寻找，找到对应的属性类型描述。

> 比如在本次实验中我分将算法和RDN分为了两个数组，在哪个数组内找到，说明该值所属的逻辑类别（比如算法名字/RDN属性类型名等）

### 生成类型

我对生成类型的理解是一系列简单类型的集合，一半标明一个语义类的简单类型会在一个生成类型包含的`length`中。
