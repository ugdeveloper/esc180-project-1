def initialize():
    '''Initializes the global variables needed for the simulation.
    Note: this function is incomplete, and you may want to modify it.
    '''
    global cur_temp
    cur_temp = 20 # in degrees Celsius
    global cur_charge
    cur_charge = 50 # in percentage points
    global cur_time # in minutes
    global good_battery_health
    cur_time = 0
    good_battery_health = True
    global above_90_count
    above_90_count = 0

    global FAST_RATE_C_T
    FAST_RATE_C_T = (3.0, 0.5)

    global SLOW_RATE_C_T
    SLOW_RATE_C_T = (1.0, 0.25)

    global IDLE_USE_T
    IDLE_USE_T = ()


def fast_charge(health: bool, temp: float, charge: float) -> bool:
   return True if (health and (0 <= temp <= 40) and (0 <= charge <= 80)) else False # return fast (true) or slow (false)

def duration_fast_charge_possible():
    pass

def get_cur_temp():
    global cur_temp
    return cur_temp

def get_cur_charge():
    global cur_charge
    return cur_charge

def get_cur_battery_health():
    global good_battery_health
    return good_battery_health

def charge_time_needed(minutes):

    get_cur_charge()
    

def simulate_activity(activity: str, duration: int) -> None:

    global good_battery_health, cur_temp, cur_charge, cur_time, above_90_count, FAST_RATE_C_T, SLOW_RATE_C_T

    for i in range(1, duration + 1):

        cur_time += 1

        if above_90_count > 3 and cur_time <= 360:
            good_battery_health = False

        match activity:
            case "charge":

                if (cur_charge >= 90):
                    above_90_count += 1

                speed: bool = fast_charge(good_battery_health, cur_temp, cur_charge) # bool representing if fast or slow

                if (good_battery_health is True and cur_charge < 100) or (good_battery_health is False and cur_charge < 80):
                    if speed: # Fast charge
                        cur_charge += FAST_RATE_C_T[0]
                        cur_temp += FAST_RATE_C_T[1]
                    else: # slow charging
                        cur_charge += SLOW_RATE_C_T[0]
                        cur_temp += SLOW_RATE_C_T[1]
                else:
                    cur_temp += SLOW_RATE_C_T[0]

            case "use":

                if cur_charge is not 0:
                    cur_charge -= 2
                    cur_temp += 1.0
                
            case "idle":

                if cur_charge is not 0:
                    cur_charge -= 0.5
                    cur_temp -= 1
                
            case _:
                pass

        if cur_charge is 0:
            cur_temp -= 1

        if cur_temp < 0:
            cur_temp = 0

        if cur_time > 360:
            cur_time = 0
            above_90_count = 0

if __name__ == '__main__':

    initialize()
    
    print(duration_fast_charge_possible()) # 10
    print(charge_time_needed(50)) # 30

    simulate_activity("charge",30)
    print(get_cur_charge()) # 100
    print(get_cur_temp()) # 30

    simulate_activity("use",50)
    print(get_cur_charge()) # 0
    print(get_cur_temp()) # 80

    simulate_activity("use",10)
    print(get_cur_charge()) # 0
    print(get_cur_temp()) # 70

    simulate_activity("charge",100)
    print(get_cur_charge()) # 100
    print(get_cur_temp()) # 95
    
    simulate_activity("idle",100)
    print(get_cur_charge()) # 50
    print(get_cur_temp()) # 0
    print(get_cur_battery_health()) # True
    print(duration_fast_charge_possible()) # 10

    simulate_activity("charge",80)
    print(get_cur_charge()) # 90
    print(get_cur_temp()) # 22.5
    print(get_cur_battery_health()) # False

    simulate_activity("use",40)
    print(get_cur_charge()) # 10
    print(get_cur_temp()) # 62.5

    simulate_activity("charge",80)
    print(get_cur_charge()) # 80
    print(get_cur_temp()) # 82.5
    
    initialize()
    # add your tests here