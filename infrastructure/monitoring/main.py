from pprint import pprint
import memory
import invokations
import cost
import gen_email

def main():
    ret = {
        'memory': memory.main(),
        'invokations': invokations.main(),
        'cost': cost.main(),
    }
    gen_email.main(ret)


if __name__ == '__main__':
    main()