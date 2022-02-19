def transfer_countbase(number, base):
    # The maximum count base is 16
    dict = {0: '0', 1: '1', 2: '2', 3: '3', 4: '4', 5: '5', 6: '6', 7: '7', 8: '8', 9: '9', 10: 'A', 11: 'B', 12: 'C',
            13: 'D', 14: 'E', 15: 'F'}
    x = number
    z = base
    lst = []
    while x > 0:
        y = x % z
        x = x // z
        lst.insert(0, dict[y])
    str = ''.join(lst)
    print(str)


def return_all_bases(number):
    print(number, " in 2 base is: ")
    transfer_countbase(number, 2)
    print('/n')
    print(number, " in 8 base is: ")
    transfer_countbase(number, 8)
    print('/n')
    print(number, " in 16 base is: ")
    transfer_countbase(number, 16)
