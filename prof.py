import pstats
import sys

p = pstats.Stats(sys.argv[1])

p.sort_stats('cumulative').print_stats(50)

p.sort_stats('time').print_stats(50)
