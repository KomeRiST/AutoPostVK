import sys

def print_p(countsec):
    while countsec > 0:
    # Следующий пост через ХХ скунд.
        sys.stdout.write('Следующий пост через '+str()+' скунд.\r' % (bar, percents, '%', suffix))
        sys.stdout.flush()
        countsec -= 1
