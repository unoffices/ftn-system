#!/usr/bin/env python
# -*- coding: UTF-8 -*-

"""
Попытка реализовать binkp протокол на python

"""

__author__ = 'svelic'

import socket
import bitstring



def data_frame_size(LO, HI):
    """
    Считаем размер блока данных
    Пример:
        >>> a = '00000000' + '00010100'
        >>> len(a)
        16
        >>> b = '0b' + a
        >>> len(b)
        18
        >>> c = bitstring.BitArray(b)
        >>> c.uint
        20
        >>> c.uintbe
        20
    :param LO: значение байта LO из заголовка для командных фреймов(8бит)
    :param HI: значение байта HI из заголовка для командных фреймов(7бит) - дополняем в начале 0 ! до длины в 8 бит !
    :return:
        возвращаем кортеж
        пример: [20, 20, 5120, 5120]
        в формате: [uint, uintbe(Big-endian), uintle(Little-endian), uintne(Native-endian)]
    """
    if len(HI) != 8:
        HI = '0' + HI
    a = HI + LO
    c = bitstring.BitArray(bin=a)
    d = (c.uint, c.uintbe, )
    print("Размер данных пакета:", HI, LO, d)
    return d

def block_type(header):
    """
    функция которая определяет тип блока: блок данных или блок комманд
    и вызывает соответсвующие фукнции обработки блоков
    """
    if int(header[0]) == 0:
        # Обрабатываем пакет как блок данных
        #TODO: добавить обработку
        print("Получили блок данные")
        return 0
    elif int(header[0]) == 1:
        # Обрабатываем пакет как блок комманд
        print("Получили блок с командой")
        return 1
    else:
        # Получили неизвестный или поврежденный блок
        print("Получили неизвестный или поврежденный блок")
        return None

def command_block(header):
    """
    В заголовке блока с командой обрабатываем команду
    :param header: заголовок блока с командой
    :return:
    """
    commands = {
        '0' : 'M_NUL',  # Аргумент команды игнорируется (и, возможно, записывается в лог). Именно так передаем нодлистовую информацию, имя сисопа и т.д.
        '1' : 'M_ADR'   # Список 5D адесов (через пробел)
    }
    cmd_num = str(bitstring.ConstBitArray(bin=header[3]).uintbe)
    if cmd_num in commands.keys():
        print("Получили команду: ", commands[cmd_num], cmd_num)
        return cmd_num
    else:
        print("Получили неизвестную команду!")
        return None


def recv_header(sock):
    """
    Читаем из сокета заголовок пакета
    :param sock: подключенный сокет
    :return: вернуть кортеж с полученным заголовком
        в формате: (block_type, HI, LO)
    """
     # Читаем из сокета заголовок
    data = sock.recv(3)
    # формируем битовый поток
    a = bitstring.BitStream(data)

    # формируем шаблон битового потока
    header_frame_template = ['bin:1','bin:7', 'bin:8', 'bin:8']
    # читаем из битового потока согласно шаблону
    block_header = tuple(a.readlist(header_frame_template))
    print("Прочитали заголовок блока: ", block_header)
    return block_header

def recv_data(sock, header):
    """
    Читаем блок данных из коммандного блока
    :param sock: сокет
    :param data_size: размер блока данных
    :return: блок данных
    """
    # Читаем XXX байт из потока согласно вычисленному размеру блока данных
    data_size = data_frame_size(HI=header[1], LO=header[2])[1] - 1
    data = sock.recv(data_size)

    if data:
        print("Прочитали из блока данных: ", data)
        return data
    else:
        print("Нет данных в блоке данных")
        return None

def main():
    """
    Run binkd server: sbin/binkd -s -v -m -r etc/binkd.config
    """

    # server = "192.168.1.104"
    server = "127.0.0.1"
    port = 24554
    srv_port = (server,port)
    sock = socket.socket()
    sock.connect(srv_port)

    #TODO: Сделать функцию которая в принимет данные блоков комманд, использовать словарь для команд
    """
        Прочитали следующий заголовок:  ['1', '0000000', '00010001', '00000000']
        Размер данных пакета: ['00000000', '00010001', 17, 17, 4352, 4352]
        Прочитали следующее из блока данных:  b'SYS MatrixSystem'
        Прочитали следующий заголовок:  ['1', '0000000', '00010100', '00000000']
        Размер данных пакета: ['00000000', '00010100', 20, 20, 5120, 5120]
        Прочитали следующее из блока данных:  b'ZYZ Sergey Velychko'
        Прочитали следующий заголовок:  ['1', '0000000', '00010010', '00000000']
        Размер данных пакета: ['00000000', '00010010', 18, 18, 4608, 4608]
        Прочитали следующее из блока данных:  b'LOC Kyiv, Ukraine'
        Прочитали следующий заголовок:  ['1', '0000000', '00010101', '00000000']
        Размер данных пакета: ['00000000', '00010101', 21, 21, 5376, 5376]
        Прочитали следующее из блока данных:  b'NDL 115200,TCP,BINKP'
        Прочитали следующий заголовок:  ['1', '0000000', '00100101', '00000000']
        Размер данных пакета: ['00000000', '00100101', 37, 37, 9472, 9472]
        Прочитали следующее из блока данных:  b'TIME Mon, 17 Nov 2014 00:17:33 +0200'
        Прочитали следующий заголовок:  ['1', '0000000', '00100001', '00000000']
        Размер данных пакета: ['00000000', '00100001', 33, 33, 8448, 8448]
        Прочитали следующее из блока данных:  b'VER binkd/0.9.9/Darwin binkp/1.1'
        Прочитали следующий заголовок:  ['1', '0000000', '00010101', '00000001']
        Размер данных пакета: ['00000000', '00010101', 21, 21, 5376, 5376]
        Прочитали следующее из блока данных:  b' 2:464/900.1@fidonet'
    """

    # Организовать цикл
    # Который будет читать данные из потока пока не встретится неизвестная команда ()
    # или не блок с командами


    header = recv_header(sock=sock)
    block_t = block_type(header)
    if block_t == 0:
        # обрабатываем блок данных
        # TODO: Сделать функцию обработки приема блоков данных
        pass
    else:
        command_block(header)
        block_data = recv_data(sock, header)



    """
    # Читаем следующий блок
    # Читаем из сокета заголовок
    data = sock.recv(3)
    # формируем битовый поток
    a = bitstring.BitStream(data)

    # формируем шаблон битового потока
    start_frame = ['bin:1','bin:7', 'bin:8', 'bin:8']
    # читаем из битового потока согласно шаблону
    data = a.readlist(start_frame)
    print("Прочитали следующий заголовок: ", data)

    # Читаем XXX байт из потока согласно вычисленному размеру блока данных
    data_size = data_frame_size(HI=data[1], LO=data[2])[1] - 1
    data=sock.recv(data_size)
    print("Прочитали следующее из блока данных: ", data)


    # Читаем следующий блок
    # Читаем из сокета заголовок
    data = sock.recv(3)
    # формируем битовый поток
    a = bitstring.BitStream(data)

    # формируем шаблон битового потока
    start_frame = ['bin:1','bin:7', 'bin:8', 'bin:8']
    # читаем из битового потока согласно шаблону
    data = a.readlist(start_frame)
    print("Прочитали следующий заголовок: ", data)

    # Читаем XXX байт из потока согласно вычисленному размеру блока данных
    data_size = data_frame_size(HI=data[1], LO=data[2])[1] - 1
    data=sock.recv(data_size)
    print("Прочитали следующее из блока данных: ", data)


    # Читаем следующий блок
    # Читаем из сокета заголовок
    data = sock.recv(3)
    # формируем битовый поток
    a = bitstring.BitStream(data)

    # формируем шаблон битового потока
    start_frame = ['bin:1','bin:7', 'bin:8', 'bin:8']
    # читаем из битового потока согласно шаблону
    data = a.readlist(start_frame)
    print("Прочитали следующий заголовок: ", data)

    # Читаем XXX байт из потока согласно вычисленному размеру блока данных
    data_size = data_frame_size(HI=data[1], LO=data[2])[1] - 1
    data=sock.recv(data_size)
    print("Прочитали следующее из блока данных: ", data)


    # Читаем следующий блок
    # Читаем из сокета заголовок
    data = sock.recv(3)
    # формируем битовый поток
    a = bitstring.BitStream(data)

    # формируем шаблон битового потока
    start_frame = ['bin:1','bin:7', 'bin:8', 'bin:8']
    # читаем из битового потока согласно шаблону
    data = a.readlist(start_frame)
    print("Прочитали следующий заголовок: ", data)

    # Читаем XXX байт из потока согласно вычисленному размеру блока данных
    data_size = data_frame_size(HI=data[1], LO=data[2])[1] - 1
    data=sock.recv(data_size)
    print("Прочитали следующее из блока данных: ", data)

    # Читаем следующий блок
    # Читаем из сокета заголовок
    data = sock.recv(3)
    # формируем битовый поток
    a = bitstring.BitStream(data)

    # формируем шаблон битового потока
    start_frame = ['bin:1','bin:7', 'bin:8', 'bin:8']
    # читаем из битового потока согласно шаблону
    data = a.readlist(start_frame)
    print("Прочитали следующий заголовок: ", data)


    # Читаем XXX байт из потока согласно вычисленному размеру блока данных
    data_size = data_frame_size(HI=data[1], LO=data[2])[1] - 1
    data=sock.recv(data_size)
    print("Прочитали следующее из блока данных: ", data)

    # Читаем следующий блок
    # Читаем из сокета заголовок
    data = sock.recv(3)
    # формируем битовый поток
    a = bitstring.BitStream(data)

    # формируем шаблон битового потока
    start_frame = ['bin:1','bin:7', 'bin:8', 'bin:8']
    # читаем из битового потока согласно шаблону
    data = a.readlist(start_frame)
    print("Прочитали следующий заголовок: ", data)

    # Читаем XXX байт из потока согласно вычисленному размеру блока данных
    data_size = data_frame_size(HI=data[1], LO=data[2])[1] - 1
    data=sock.recv(data_size)
    print("Прочитали следующее из блока данных: ", data)
    """

    sock.close()



if __name__ == "__main__":
    main()