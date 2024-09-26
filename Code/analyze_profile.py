import pstats

# Load the profiling data
profiler_stats = pstats.Stats('game_profile.prof')

# Strip directories from filenames and sort the statistics by cumulative time
profiler_stats.strip_dirs().sort_stats('cumulative').print_stats(20)
