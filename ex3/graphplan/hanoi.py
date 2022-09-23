import sys
from itertools import product
from typing import List, TextIO, Iterator


def move_between_pegs(disk: str, places: Iterator[str], file: TextIO):
    ACTION = "MOVE"
    for src, tar in places:
        if (disk != src) and (disk != tar) and (src != tar):
            file.write(f"Name: ({ACTION}_{disk}_FROM_{src}_TO_{tar})\n")
            file.write(f"pre: (smaller_{disk}_{src}) (smaller_{disk}_{tar}) "
                       f"(on_{disk}_{src}) "
                       f"(clear_{disk}) (clear_{tar})\n")
            file.write(f"add: (clear_{src}) (on_{disk}_{tar})\n")
            file.write(f"delete: (on_{disk}_{src}) (clear_{tar})\n")


def move_from_disk_to_peg(disk_size: int, disks, pegs, file: TextIO):
    ACTION = "MOVE"
    disk = disks[disk_size]
    for i in range(disk_size+1, len(disks)):
        for j in range(len(pegs)):
            file.write(f"Name: ({ACTION}_{disk}_FROM_{disks[i]}_TO_{pegs[j]})\n")
            file.write(f"pre: (smaller_{disk}_{disks[i]}) (smaller_{disk}_{pegs[j]}) "
                       f"(on_{disk}_{disks[i]}) "
                       f"(clear_{disk}) (clear_{pegs[j]})\n")
            file.write(f"add: (clear_{disks[i]}) (on_{disk}_{pegs[j]})\n")
            file.write(f"delete: (on_{disk}_{disks[i]}) (clear_{pegs[j]})\n")


def move_from_peg_to_disk(disk_size: int, disks, pegs, file: TextIO):
    ACTION = "MOVE"
    disk = disks[disk_size]
    for i in range(disk_size+1, len(disks)):
        for j in range(len(pegs)):
            file.write(f"Name: ({ACTION}_{disk}_FROM_{pegs[j]}_TO_{disks[i]})\n")
            file.write(f"pre: (smaller_{disk}_{pegs[j]}) (smaller_{disk}_{disks[i]}) "
                       f"(on_{disk}_{pegs[j]}) "
                       f"(clear_{disk}) (clear_{disks[i]})\n")
            file.write(f"add: (clear_{pegs[j]}) (on_{disk}_{disks[i]})\n")
            file.write(f"delete: (on_{disk}_{pegs[j]}) (clear_{disks[i]})\n")


def move_between_disks(disk_size: int, disks: List[str], file: TextIO):
    ACTION = "MOVE"
    disk = disks[disk_size]
    for i in range(disk_size + 1, len(disks)):
        for j in range(i + 1, len(disks)):
            file.write(f"Name: ({ACTION}_{disk}_FROM_{disks[i]}_TO_{disks[j]})\n")
            file.write(f"pre: (smaller_{disk}_{disks[i]}) (smaller_{disk}_{disks[j]}) "
                       f"(on_{disk}_{disks[i]}) "
                       f"(clear_{disk}) (clear_{disks[j]})\n")
            file.write(f"add: (clear_{disks[i]}) (on_{disk}_{disks[j]})\n")
            file.write(f"delete: (on_{disk}_{disks[i]}) (clear_{disks[j]})\n")


def create_domain_file(domain_file_name, n_, m_):
    if (n_ <= 0) or (m_ <= 0):
        domain_file = open(domain_file_name, 'w')
        domain_file.close()
        return
    disks = ['d_%s' % i for i in list(range(n_))]  # [d_0,..., d_(n_ - 1)]
    pegs = ['p_%s' % i for i in list(range(m_))]  # [p_0,..., p_(m_ - 1)]
    domain_file = open(domain_file_name, 'w')  # use domain_file.write(str) to write to domain_file
    "*** YOUR CODE HERE ***"
    # I. Propositions:
    domain_file.write("Propositions:\n")
    for obj in (disks + pegs):
        domain_file.write(f"(clear_{obj}) ")
    for disk, peg in product(disks, pegs):
        domain_file.write(f"(smaller_{disk}_{peg}) ")
        domain_file.write(f"(on_{disk}_{peg}) ")
    for i in range(len(disks)):
        for j in range(i + 1, len(disks)):
            domain_file.write(f"(smaller_{disks[i]}_{disks[j]}) ")
            domain_file.write(f"(on_{disks[i]}_{disks[j]}) ")
    domain_file.write("\n")

    # II. Moves:
    domain_file.write("Actions:\n")
    disk_size = 0
    for disk in disks:
        # move the disk from peg to peg (peg -> peg)
        move_between_pegs(disk, product(pegs, pegs), domain_file)
        # move the disk between peg and disk (disk -> peg || peg -> disk)
        move_from_disk_to_peg(disk_size, disks, pegs, domain_file)
        move_from_peg_to_disk(disk_size, disks, pegs, domain_file)
        # move the disk from disk to disk (disk -> disk)
        move_between_disks(disk_size, disks, domain_file)
        disk_size += 1

    domain_file.close()


def create_problem_file(problem_file_name_, n_, m_):
    if (n_ <= 0) or (m_ <= 0):
        problem_file = open(problem_file_name_, 'w')
        problem_file.close()
        return
    disks = ['d_%s' % i for i in list(range(n_))]  # [d_0,..., d_(n_ - 1)]
    pegs = ['p_%s' % i for i in list(range(m_))]  # [p_0,..., p_(m_ - 1)]
    problem_file = open(problem_file_name_, 'w')
    # use problem_file.write(str) to write to problem_file
    "*** YOUR CODE HERE ***"
    # I. Initial state:
    problem_file.write(f"Initial state: ")
    for disk, peg in product(disks, pegs):
        problem_file.write(f"(smaller_{disk}_{peg}) ")
    for i in range(len(disks)):
        for j in range(i + 1, len(disks)):
            problem_file.write(f"(smaller_{disks[i]}_{disks[j]}) ")
    for peg in pegs[1:]:
        problem_file.write(f"(clear_{peg}) ")
    problem_file.write(f"(clear_{disks[0]}) ")
    for i in range(len(disks) - 1):
        problem_file.write(f"(on_{disks[i]}_{disks[i + 1]}) ")
    problem_file.write(f"(on_{disks[-1]}_{pegs[0]})\n")
    # I. Goal state:
    problem_file.write(f"Goal state: ")
    for i in range(len(disks) - 1):
        problem_file.write(f"(on_{disks[i]}_{disks[i + 1]}) ")
    problem_file.write(f"(on_{disks[-1]}_{pegs[-1]})\n")
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
