from pprint import pprint
import memory
import invokations
import cost

def main():
    ret = {
        'memory': memory.main(),
        'invokations': invokations.main(),
        'cost': cost.main(),
    }


if __name__ == '__main__':
    main()