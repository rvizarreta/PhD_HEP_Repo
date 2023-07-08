import time

fin = open( 'time_header.txt', 'r' )
timestrings = fin.readlines()[0]
start = float(timestrings.split()[0])
end = float(timestrings.split()[1])
fin.close()

elapsed = (end-start)/60.0 # elapsed time in minutes
wday_string = [ 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun' ]
month_string = [ 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec' ]

fout = open( 'time_header2.txt', 'w' )
localStart = time.localtime(start/1.0E6)
localEnd = time.localtime(end/1.0E6)

start_year = localStart[0]
start_month = localStart[1]-1
start_day = localStart[2]
start_hour = localStart[3]
start_min = localStart[4]
start_sec = localStart[5]
start_wday = localStart[6]

fout.write( '# begin   %16.0f %s %s %02d %02d:%02d:%02d %04d\n' % (start, wday_string[start_wday], month_string[start_month], start_day, start_hour, start_min, start_sec, start_year) )

end_year = localEnd[0]
end_month = localEnd[1]-1
end_day = localEnd[2]
end_hour = localEnd[3]
end_min = localEnd[4]
end_sec = localEnd[5]
end_wday = localEnd[6]

fout.write( '# end     %16.0f %s %s %02d %02d:%02d:%02d %04d\n' % (end, wday_string[end_wday], month_string[end_month], end_day, end_hour, end_min, end_sec, end_year) )

fout.write( '# elapsed %1.1f min\n' % elapsed )
