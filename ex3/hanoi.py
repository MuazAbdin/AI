import sys
from itertools import product


def create_domain_file(domain_file_name, n_, m_):
    disks = ['d_%s' % i for i in list(range(n_))]  # [d_0,..., d_(n_ - 1)]
    pegs = ['p_%s' % i for i in list(range(m_))]  # [p_0,..., p_(m_ - 1)]
    domain_file = open(domain_file_name, 'w')  # use domain_file.write(str) to write to domain_file
    "*** YOUR CODE HERE ***"
    # I. Propositions:
    domain_file.write("Propositions:\n")
    for obj in (disks + pegs):
        domain_file.write(f"(clear {obj}) ")
    for disk, peg in product(disks, pegs):
        domain_file.write(f"(smaller {disk} {peg}) ")
        domain_file.write(f"(on {disk} {peg}) ")
    for i in range(len(disks)):
        for j in range(i + 1, len(disks)):
            domain_file.write(f"(smaller {disks[i]} {disks[j]}) ")
            domain_file.write(f"(on {disks[i]} {disks[j]}) ")
    domain_file.write("\n")
    # II. Moves:
    ACTION = "MOVE"
    domain_file.write("Actions:\n")
    for disk in disks:
        for src, tar in product(disks + pegs, disks + pegs):
            if (disk != src) and (disk != tar) and (src != tar):
                domain_file.write(f"Name: ({ACTION} {disk} FROM {src} TO {tar})\n")
                domain_file.write(f"pre: (smaller {disk} {src}) (smaller {disk} {tar}) "
                                  f"(on {disk} {src}) "
                                  f"(clear {disk}) (clear {tar})\n")
                domain_file.write(f"add: (clear {src}) (on {disk} {tar})\n")
                domain_file.write(f"delete: (on {disk} {src}) (clear {tar})\n")
    domain_file.close()


def create_problem_file(problem_file_name_, n_, m_):
    disks = ['d_%s' % i for i in list(range(n_))]  # [d_0,..., d_(n_ - 1)]
    pegs = ['p_%s' % i for i in list(range(m_))]  # [p_0,..., p_(m_ - 1)]
    problem_file = open(problem_file_name_, 'w')
    # use problem_file.write(str) to write to problem_file
    "*** YOUR CODE HERE ***"
    # I. Initial state:
    problem_file.write(f"Initial state: ")
    for disk, peg in product(disks, pegs):
        problem_file.write(f"(smaller {disk} {peg}) ")
    for i in range(len(disks)):
        for j in range(i + 1, len(disks)):
            problem_file.write(f"(smaller {disks[i]} {disks[j]}) ")
    for peg in pegs[1:]:
        problem_file.write(f"(clear {peg}) ")
    problem_file.write(f"(clear {disks[0]}) ")
    for i in range(len(disks) - 1):
        problem_file.write(f"(on {disks[i]} {disks[i + 1]}) ")
    problem_file.write(f"(on {disks[-1]} {pegs[0]})\n")
    # I. Goal state:
    problem_file.write(f"Goal state: ")
    for i in range(len(disks) - 1):
        problem_file.write(f"(on {disks[i]} {disks[i + 1]}) ")
    problem_file.write(f"(on {disks[-1]} {pegs[-1]})\n")
    problem_file.close()


if __name__ == '__main__':
    if len(sys.argv) != 3:
        print('Usage: hanoi.py n m')
        sys.exit(2)

    n = int(float(sys.argv[1]))  # number of disks
    m = int(float(sys.argv[2]))  # number of pegs

    domain_file_name = 'hanoi_%s_%s_domain.txt' % (n, m)
    problem_file_name = 'hanoi_%s_%s_problem.txt' % (n, m)

    create_domain_file(domain_file_name, n, m)
    create_problem_file(problem_file_name, n, m)
