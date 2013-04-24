import sys, itertools

def min_prime_factor(x, f):
    if x <= 1:
        return x

    f = f or 2
    for i in itertools.count(f):
        if x%i == 0:
            return i
        '''
        if i > x>>1:
            return x
        '''

def prime_factors(x, f):
    f = min_prime_factor(x, f)
    if f==x:
        return [f]
    else:
        return [f] + prime_factors(x/f, f)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: %s <number>" % sys.argv[0])
        exit(1)
    print(prime_factors(int(sys.argv[1]), 2))
