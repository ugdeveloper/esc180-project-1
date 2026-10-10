def initialize():
    '''Initializes the global variables needed for the simulation.
    Note: this function is incomplete, and you may want to modify it.
    '''

    global cur_temp # in degrees Celsius
    global cur_charge # in percentage points
    global cur_time # in minutes
    global good_battery_health
    global fast_charging
    global last_overcharge_time1
    global last_overcharge_time2
    global last_overcharge_time3
    # In general it is good practice to make variables for constants within your program
    cur_temp = 20
    cur_charge = 50
    cur_time = 0
    good_battery_health = True
    fast_charging = True
    last_overcharge_time1 = -1
    last_overcharge_time2 = -1
    # Edit: you don't need 3 overcharge times, just save the most recent 2, and compare with the current time.
    last_overcharge_time3 = -1

def simulate_activity(activity, duration):
    global cur_temp, cur_charge, cur_time
    global good_battery_health, fast_charging
    global last_overcharge_time1, last_overcharge_time2, last_overcharge_time3

    if activity == 'idle':
        cur_charge -= 0.5 * duration
        cur_temp -= 1 * duration

        if cur_charge <0:
            cur_charge = 0

        if cur_temp <0:
            cur_temp = 0

        cur_time += duration

    if activity == 'use':
        cur_charge -= 2 * duration
        cur_temp += 1 * duration

        if cur_charge <0:
            cur_charge = 0

        cur_time += duration

    if activity == 'charge':
        fast_time = duration_fast_charge_possible ()
        if fast_charging>=duration:##### come back to this to fix
            cur_temp += 0.5 * duration
            cur_charge += 3 * duration
        else:
            cur_temp += 0.5 * fast_time
            cur_charge += 3 * fast_time

            cur_temp += 0.25 * (duration - fast_time)
            cur_charge += 1 * (duration - fast_time)

        cur_time += duration


        if cur_charge >= 90:
            last_overcharge_time1 = last_overcharge_time2
            last_overcharge_time2 = last_overcharge_time3
            last_overcharge_time3 = cur_time

        #check if 3 overcharges happened within 6 hours

        if (last_overcharge_time1 >=0 and cur_time - last_overcharge_time1 < 360):

            if (last_overcharge_time2 >=0 and cur_time-last_overcharge_time2 <360):

                if (last_overcharge_time3 >=0 and cur_time - last_overcharge_time3 < 360):
                    good_battery_health = False
        else:
            good_battery_health = True

def duration_fast_charge_possible():
    global cur_temp
    global fast_charging

    if good_battery_health == True:
        if cur_temp >= 0 and cur_temp<=40 and cur_charge < 80:
            # charging fast
            fast_charging = True

            # calculate time to reach 80%, fast charging adds 3%/min
            charge_time =  (80-cur_charge)/3
            # calculate the time for the temperature to reach 40º
            temp_time = (40-cur_temp)/0.5

            if charge_time < temp_time:
                return charge_time
            else:
                return temp_time

        else: fast_charging = False

    else:
        fast_charging = False







    # fast charging increases the charge by 3%/min
    # fast charging occurs when the temp is between 0-40, battery charge is below 80%, and battery_health = True
    # fast charging increases temp by 0.5ºC/min
    #slow charging increases by 1%/min
    #slow charging increases temp by 0.25º/min


def get_cur_temp():
    global cur_temp
    return cur_temp


def get_cur_charge():
    global cur_charge
    return cur_charge


def get_cur_battery_health():
    return good_battery_health

def charge_time_needed(minutes):
    global charge_time_needed
    return charge_time_needed

if __name__ == '__main__':
    initialize()

    print(duration_fast_charge_possible()) # 10
    #print(charge_time_needed(50)) # 30

    simulate_activity("charge",30)
    print(get_cur_charge()) # 100
    print(get_cur_temp()) # 30

    # simulate_activity("use",50)
    # print(get_cur_charge()) # 0
    # print(get_cur_temp()) # 80
    #
    # simulate_activity("use",10)
    # print(get_cur_charge()) # 0
    # print(get_cur_temp()) # 70
    #
    # simulate_activity("charge",100)
    # print(get_cur_charge()) # 100
    # print(get_cur_temp()) # 95
    #
    # simulate_activity("idle",100)
    # print(get_cur_charge()) # 50
    # print(get_cur_temp()) # 0
    # print(get_cur_battery_health()) # True
    # print(duration_fast_charge_possible()) # 10
    #
    # simulate_activity("charge",80)
    # print(get_cur_charge()) # 90
    # print(get_cur_temp()) # 22.5
    # print(get_cur_battery_health()) # False
    #
    # simulate_activity("use",40)
    # print(get_cur_charge()) # 10
    # print(get_cur_temp()) # 62.5
    #
    # simulate_activity("charge",80)
    # print(get_cur_charge()) # 80
    # print(get_cur_temp()) # 82.5

    initialize()
    # add your tests here
