from math import sqrt, sin, fabs, atan, cos
miu = 3.986005e14  # WGS-84坐标系中的地球引力常数
we = 7.29211567e-5   # 地球自转速率


def main():
    lmessages = splitPRN()

    tob_str = "12 1 18 14 29 36"  # 观测时间

    # PRN=6
    m = findExactMessage(lmessages=lmessages, i=6, h=14)  # i为PRN号，h为小时数
    result06 = Calculate(dicParas(m)).calculate(tob_str=tob_str)
    # PRN=13
    m = findExactMessage(lmessages=lmessages, i=13, h=14)  # i为PRN号，h为小时数
    result13 = Calculate(dicParas(m)).calculate(tob_str=tob_str)
    # PRN=21
    m = findExactMessage(lmessages=lmessages, i=21, h=14)  # i为PRN号，h为小时数
    result21 = Calculate(dicParas(m)).calculate(tob_str=tob_str)

    print("****RESULT****\n\nPRN=6\t{0}\nPRN=13\t{1}\nPRN=21\t{2}".format(
        result06, result13, result21))

    input()


def splitPRN(filename='brdc0180.12n'):
    '''返回一个列表'''
    print("...reading file")
    with open(filename) as f:
        # 略去头文件
        for i in range(8):
            f.readline()

        lmessages = []
        s = ""
        message = ""
        while True:
            for i in range(8):
                s = f.readline()
                if s == "":
                    break
                else:
                    message += s
            if s == "":
                break
            else:
                lmessages.append(message)
                message = ""
        return lmessages


def findExactMessage(lmessages, i, h, year=12, month=1, day=18):
    '''找到指定日期的某个时刻h(小时)，PRN号为i的数据段返回'''
    start_str = "{0:>2d} {1}  {2} {3} {4:>2d}".format(i, year, month, day, h)
    print("...finding data for {}".format(start_str))
    for message in lmessages:
        if message.startswith(start_str):
            return message


def dicParas(m):
    '''
        返回键为参数名值为参数值的字典
        "toe_str", "SCB", "SCD", "SCDC":
        “年 月 时 分 秒”,“卫星钟偏差”,"卫星钟漂移","卫星钟漂移速度"
        --
        "IODE", "Crs", "delta_n", "M0":
        "数据龄期","卫星矢径正弦改正振幅","平均角速度之差","平近点角"
        --
        "Cuc", "orbit_e", "Cus", "sqrt_a":
        "升交距角余弦改正振幅","轨道第一偏心率e","升交距角正弦改正振幅","轨道长半径的平方根sqrt(A)"
        --
        "toe", "Cic", "Omega_0", "Cis":
        "参考历元(时间)","轨道倾角余弦改正振幅","升交点赤经Ω_0","轨道倾角正弦改正振幅"
        --
        "i_0", "Crc", "w", "ACR":
        "轨道倾角","卫星矢径余弦改正振幅","近地点角矩ω","升交点赤经变化率Ω^·"
        --
        "OICR", "L2", "GPS_week", "L2P"
        "轨道倾角变化率i^·","L2上的码","GPS周数","L2 P码数据标记"
    '''
    # 定义参数键字典
    para_names = [["toe_str", "SCB", "SCD", "SCDC"], ["IODE", "Crs", "delta_n", "M0"], ["Cuc", "orbit_e", "Cus", "sqrt_a"], [
        "toe", "Cic", "Omega_0", "Cis"], ["i_0", "Crc", "w", "ACR"], ["OICR", "L2", "GPS_week", "L2P"]]
    frame_dic = {}
    rows = m.split("\n")
    i = 0
    for para_names_row in para_names:
        m = 0
        for key in para_names_row:
            value = rows[i][3:][m*19:(m+1)*19]
            if key == 'toe_str':
                frame_dic[key] = value
            else:
                frame_dic[key] = scistrToFloat(value)
            print("{0:>7s}:{1}".format(key, value))
            m += 1
        i += 1

    return frame_dic


class Calculate:

    def __init__(self, frame):
        self.frame = frame

    def calculate(self, tob_str="12 1 18 14 29 36"):
        '''计算卫星坐标
        tob_str:观测时间的字符串形式
        '''
        f = self.frame
        n0 = sqrt(miu)/pow(f["sqrt_a"], 3)  # 卫星运行的平均角速度

        # 计算观测时间tob的gps时
        [year, month, day, hour, min, sec] = tob_str.split(' ')
        tob = getGPSTime(int('20'+year), int(month), int(day),
                         int(hour), int(min), float(sec)).gpsTime(c='s')

        tk = tob-f["toe"]   # 规划时间
        mk = f["M0"]+n0*tk  # 观测瞬间的卫星平近点角

        # 迭代计算偏近点角Ek
        ek = mk
        temp = 0
        while fabs(ek-temp) > 0.10e-12:
            temp = ek
            ek = mk+f["orbit_e"]*sin(temp)

        fk = atan((sqrt(1-pow(f["orbit_e"], 2)) *
                   sin(ek)/(cos(ek)-f["orbit_e"])))  # 真近点角fk
        pk = fk+f["w"]    # 升交距角

        # 计算摄动改正项du,dr,di
        du = f["Cuc"]*cos(2*pk)+f["Cus"]*sin(2*pk)
        dr = f["Crc"]*cos(2*pk)+f["Crs"]*sin(2*pk)
        di = f["Cic"]*cos(2*pk)+f["Cis"]*sin(2*pk)

        # 计算经过摄动改正的升交距角uk、卫星矢径rk、轨道倾角ik
        uk = pk+du
        rk = pow(f["sqrt_a"], 2)*(1-f["orbit_e"]*cos(ek))+dr
        ik = f["i_0"]+di+f["OICR"]*tk

        # 计算卫星在轨道平面上的位置
        xk = rk*cos(uk)
        yk = rk*sin(uk)

        # 计算观测的升交点经度Ω_k
        dk = f["Omega_0"]+(f["ACR"])*tk-we*tob  # we为地球自转速率

        # 计算卫星在地心固定坐标系中的位置
        Xk = xk * cos(dk) - (yk * cos(ik) * sin(dk))
        Yk = xk * sin(dk) + (yk * cos(ik) * cos(dk))
        Zk = yk * sin(ik)

        print("\nuk:{}\nrk:{}\nik:{}\nxk:{}\nyk:{}\ndk:{}\nXk:{}\nYk:{}\nZk:{}\n".format(
            uk, rk, ik, xk, yk, dk, Xk, Yk, Zk))

        return [Xk, Yk, Zk]


def scistrToFloat(str_n):
    '''科学计数法字符串转单精度浮点数'''
    l = str_n.split('D')
    return float(l[0])*pow(10, int(l[1]))


class getGPSTime:
    def __init__(self, year, month, day, hour, miniute, second):
        self.year = year
        self.month = month
        self.day = day
        self.hour = hour
        self.miniute = miniute
        self.second = second

    def yearDayCount(self, year):
        count = 0
        if(year == 1980):
            count = 360  # 自1980年1月6日零点起算
        elif((year % 4 == 0 and year % 100 != 0) or year % 400 == 0):
            count = 366
        else:
            count = 365
        return count

    def monthDayCount(self, year, month):
        count = 0
        if(year == 1980 and month == 1):
            count = 25
        elif month in [4, 6, 9, 11]:
            count = 30
        elif month in [1, 3, 5, 7, 8, 10, 12]:
            count = 31
        else:
            count = 29 if ((year % 4 == 0 and year % 100 != 0)
                           or year % 400 == 0) else 28
        return count

    def gpsTime(self, c='s'):
        '''c = 'w' 则返回 gps 周， c = 's' 则返回 gps 周内秒，默认返回周内秒'''
        days = self.day
        if(c != 'w' and c != 's'):
            return -1
        for i in range(1980, self.year):
            days += self.yearDayCount(i)
        for i in range(1, self.month):
            days += self.monthDayCount(self.year, i)
        return (days-(days % 7))/7 if c == 'w' else (days % 7)*86400+self.hour*3600+self.miniute*60+self.second


main()
