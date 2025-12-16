import datetime as dt

def maketd(timestr:str):
    hr = int(timestr.split(":")[0])
    if timestr[-1] == 'm':
        timestr = timestr[:-1]
    if timestr[-1] == 'p':
        if hr != 12: hr += 12
        timestr = timestr[:-1]
    else:
        if hr == 12: hr = 0
    if timestr[-1] == 'a':
        timestr = timestr[:-1]
    mn = int(timestr.split(":")[1])
    return dt.timedelta(days=0, hours=hr, minutes=mn)

def t(tdelta):
    p = False
    h, rem = divmod(tdelta.seconds, 3600)
    m, _ = divmod(rem, 60)
    if h > 11:
        p = True
        if h != 12: h -= 12
    h = '{:02d}'.format(h)
    m = '{:02d}'.format(m)
    return f"{h}:{m}{'p' if p else 'a'}"

def tl(tdelta):
    h, rem = divmod(tdelta.seconds, 3600)
    m, _ = divmod(rem, 60)
    h = f"{h} hour{'s' if h > 1 else ''}" if h > 0 else ''
    m = f"{m} minute{'s' if m > 1 else ''}" if m > 0 else ''
    if h == '' and m == '':
        return 'No'
    return f"{h}{', ' if h != '' and m != '' else ''}{m}"

if __name__ == "__main__":
    movies = []
    
    while True:
        name = input(f"Movie {len(movies)+1} name: ")
        if len(name) == 0:
            break
        movie = {"name":name,"runtime":None,"showtimes":[],"ends":[]}
        runtime = maketd(input("Length: "))
        movie["runtime"] = runtime
        while True:
            inp = input(f"Showtime {len(movie['showtimes'])+1}: ")
            if len(inp) == 0:
                print('-'*30)
                break
            showtime = maketd(inp)
            end = showtime + runtime
            movie["showtimes"].append(showtime)
            movie["ends"].append(end)
        movies.append(movie)
    
    a = 'y'

    while a.lower() != 'n':
        print('*' * 60)
        print('*' * 60)
        
        slop = input("Minimum time inbetween showings (minutes): ")
        if len(slop) == 0:
            slop = maketd("0:0")
        else:
            slop = maketd(f"0:{slop}")

        maxi = input("Maximum time inbetween showings (minutes): ")
        if len(maxi) == 0:
            maxi = None
        else:
            maxi = maketd(f"0:{maxi}")        
            
        begin = input("Start no earlier than: ")
        if len(begin) != 0:
            begin = maketd(begin)
        else:
            begin = None
        
        stop = input("End no later than: ")
        if len(stop) != 0:
            stop = maketd(stop)
        else:
            stop = None

        print('')

        mvind = [0] * len(movies)
        combos = 0

        print('-'*40)
        
        while True:
            shs = []
            ends = []
            for movie, mvshow in zip(movies, mvind):
                shs.append(movie["showtimes"][mvshow])
                ends.append(movie["ends"][mvshow])
            
            try:
                if begin is not None:
                    for sh in shs:
                        # movie begins before earliest time
                        if sh < begin: raise Exception
                        
                if stop is not None:
                    for end in ends:
                        # movie ends after latest time
                        if end > stop: raise Exception

                for i in range(len(shs) - 1):
                    for j in range(i + 1, len(shs)):
                        if ends[i] > shs[j] - slop and shs[j] >= shs[i]: raise Exception
                        if ends[j] > shs[i] - slop and shs[i] >= shs[j]: raise Exception

                # sort
                moviess = list(range(len(shs)))
                shss = shs
                endss = ends

                for i in range(len(shs) - 1):
                    for j in range(i + 1, len(shs)):
                        if shss[i] > shss[j]:
                            tmp = shss[j]
                            shss[j] = shss[i]
                            shss[i] = tmp
                            
                            tmp = moviess[j]
                            moviess[j] = moviess[i]
                            moviess[i] = tmp
                            
                            tmp = endss[j]
                            endss[j] = endss[i]
                            endss[i] = tmp

                if maxi is not None:
                    for n in range(len(shss) - 1):
                        if (shss[n + 1] - endss[n]) > maxi: raise Exception

                combos+=1
                print(f"Schedule {combos}:\n")
                
                for n in range(len(shss)):
                    print(f"{movies[moviess[n]]['name']}\n{t(shss[n])} - {t(endss[n])}")
                    if n != len(shss) - 1: print(f"\n-- {tl(shss[n + 1] - endss[n])} --\n")
                
                print('-'*40)
            except Exception as _:
                pass

            cind = 0
            while cind < len(mvind):
                mvind[cind]+=1
                if mvind[cind] == len(movies[cind]["showtimes"]):
                    mvind[cind] = 0
                    cind+=1
                else:
                    break
            else:
                break

        if combos == 0:
            print("No valid combinations of showtimes")
            print('-'*40)
            print('')
            
        a = input("Recalculate (n to quit)? ")        
