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
    global speed
    speed = True

    global FAST_CHARGE_RATE, SLOW_CHARGE_RATE, FAST_TEMP_INC, SLOW_TEMP_INC, USE_RATE, USE_TEMP_INC, IDLE_USE_RATE, MIN_TEMP, MIN_CHARGE, MAX_CHARGE, MAX_CHARGE_BAD

    FAST_CHARGE_RATE = 3.0
    SLOW_CHARGE_RATE = 1.0
    FAST_TEMP_INC = 0.5
    SLOW_TEMP_INC = 0.25
    USE_RATE = 2.0
    USE_TEMP_INC = 1.0
    IDLE_USE_RATE = 0.5
    MIN_TEMP = 0
    MIN_CHARGE = 0
    MAX_CHARGE = 100
    MAX_CHARGE_BAD = 80

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
    global MAX_CHARGE, cur_charge, speed, FAST_CHARGE_RATE, SLOW_CHARGE_RATE
    

def simulate_activity(activity: str, duration: int) -> None:

    global speed, good_battery_health, cur_temp, cur_charge, cur_time, above_90_count, FAST_CHARGE_RATE, SLOW_CHARGE_RATE, FAST_TEMP_INC, SLOW_TEMP_INC, USE_RATE, USE_TEMP_INC, IDLE_USE_RATE, MIN_TEMP, MIN_CHARGE, MAX_CHARGE, MAX_CHARGE_BAD

    for i in range(1, duration + 1):

        cur_time += 1

        if above_90_count > 3 and cur_time <= 360:
            good_battery_health = False

        match activity:
            case "charge":

                if (cur_charge >= 90):
                    above_90_count += 1

                speed = fast_charge(good_battery_health, cur_temp, cur_charge) # bool representing if fast or slow

                if (good_battery_health is True and cur_charge < MAX_CHARGE) or (good_battery_health is False and cur_charge < MAX_CHARGE_BAD):
                    if speed: # Fast charge
                        cur_charge += FAST_CHARGE_RATE
                        cur_temp += FAST_TEMP_INC
                    else: # slow charging
                        cur_charge += SLOW_CHARGE_RATE
                        cur_temp += SLOW_TEMP_INC
                else:
                    cur_temp += SLOW_TEMP_INC

            case "use":

                if cur_charge is not MIN_CHARGE:
                    cur_charge -= USE_RATE
                    cur_temp += USE_TEMP_INC
                
            case "idle":

                if cur_charge is not MIN_CHARGE:
                    cur_charge -= IDLE_USE_RATE
                    cur_temp -= USE_TEMP_INC
                
            case _:
                pass

        if cur_charge is MIN_CHARGE:
            cur_temp -= USE_TEMP_INC

        if cur_temp < MIN_TEMP:
            cur_temp = MIN_TEMP

        if cur_charge > MAX_CHARGE:
            cur_charge = MAX_CHARGE

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