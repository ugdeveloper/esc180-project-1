def initialize():
    # init variables

    # Mutable global variables
    global cur_charge, cur_temp, cur_health
    global cur_time, overcharge_1, overcharge_2

    # Immutable global variables (constants)
    global FAST_CHARGE_RATE, SLOW_CHARGE_RATE
    global FAST_CHARGE_TEMP_INC, SLOW_CHARGE_TEMP_INC
    global MAX_CHARGE_FAST_CHARGE, MAX_TEMP_FAST_CHARGE
    global USAGE_DISCHARGE_RATE, USAGE_TEMP_INC
    global IDLE_DISCHARGE_RATE, IDLE_TEMP_INC
    global MIN_CHARGE, MIN_TEMP
    global MAX_CHARGE_GOOD, MAX_CHARGE_BAD
    global OVERCHARGE_LEVEL, OVERCHARGE_WINDOW
 
    # cur charge in %
    cur_charge = 50.0

    # cur temp in deg C.
    cur_temp = 20.0

    # cur health, true for good, false for bad
    cur_health = True
 
    # current time in minutes
    cur_time = 0.0
 
    # timeframe of overcharge 1 (-1 for not happened)
    overcharge_1 = -1.0
 
    # timeframe of overcharge 2 (-1 for not happened)
    overcharge_2 = -1.0

    #max charge for fast charging
    MAX_CHARGE_FAST_CHARGE = 80.0

    # max temp for fast charge
    MAX_TEMP_FAST_CHARGE = 40.0
 
    # fast charge rate %/min
    FAST_CHARGE_RATE = 3.0
 
    # fast charge temp increment deg C/min
    FAST_CHARGE_TEMP_INC = 0.5
 
    # slow charge rate %/min
    SLOW_CHARGE_RATE = 1.0

    # slow charge temp increment deg C/min
    SLOW_CHARGE_TEMP_INC = 0.25
 
    # min possible temperature in deg C.
    MIN_TEMP = 0.0
 
    # min charge in %.
    MIN_CHARGE = 0.0
 
    # max charge of good health battery in %
    MAX_CHARGE_GOOD = 100.0
 
    # max charge of bad health battery in %
    MAX_CHARGE_BAD = 80.0
 
    # usage temp increment in deg C/min
    USAGE_TEMP_INC = 1.0
 
    # usage rate in %/min
    USAGE_DISCHARGE_RATE = -2.0
 
    # idle temp increment in deg C/min
    IDLE_TEMP_INC = -1.0
 
    # usage rate for idle in %/min
    IDLE_DISCHARGE_RATE = -0.5
 
    # Charge at or above which charging counts as an overcharge, in %.
    OVERCHARGE_LEVEL = 90.0
 
    # Time span for 3 overcharges
    # A gap of exactly this length is not within the span.
    OVERCHARGE_WINDOW = 360.0
 
 
def get_cur_temp() -> float:
    # return current battery temp
 
    return float(cur_temp)
 
 
def get_cur_charge() -> float:
    # return current charge
    
    return float(cur_charge)
 
 
def get_cur_battery_health() -> bool:
    # return current battery health
    
    return cur_health
 
 
def duration_fast_charge_possible() -> float:
    # return duration that fast charge is possible in min
    
    # if current health is bad this time is 0
    if not cur_health:
        return 0.0
 
    # calculate the limiting times of temp and charge for fast charging
    # (i.e, the time for the current temp/charge to reach the max temp/charge)
    temp_lim_time = (MAX_TEMP_FAST_CHARGE - cur_temp) / FAST_CHARGE_TEMP_INC
    charge_lim_time = (MAX_CHARGE_FAST_CHARGE - cur_charge) / FAST_CHARGE_RATE

    # if either of the limiting times is less than or equal to zero, return 0
    if temp_lim_time <= 0 or charge_lim_time <= 0:
        return 0.0

    # base case, return the smaller value between the limiting times.
    # (i.e, the smaller time limits the entire process of fast charging
    # giving the max duration of fast charging)
    return min(temp_lim_time, charge_lim_time)
 
 
def register_overcharge(overcharge_time: int) -> bool:
    # register an overcharge and check if 3 overcharges have occured
    # in the time frame
 
    global overcharge_1, overcharge_2
 
    # Only the two most recent earlier overcharges matter: the new one is
    # the third within 6 hours exactly when the older of these two is less
    # than 6 hours before it.
    if (overcharge_1 >= 0 and overcharge_2 >= 0) and (overcharge_time - overcharge_1 < OVERCHARGE_WINDOW):
        overcharge_1 = overcharge_2
        overcharge_2 = overcharge_time
        return True

    overcharge_1 = overcharge_2
    overcharge_2 = overcharge_time
 
    return False
 
 
def simulate_charging(duration: float):
    # simulate battery charging for duration minutes
 
    global cur_charge, cur_temp, cur_health

    # if current battrey health is bad, only check this statement
    if not cur_health:

        # as long as its current charge is less that its max charge (bad),
        # this statement is read
        if cur_charge < MAX_CHARGE_BAD:
            # take the minimum value between the charge after charging at the slow rate and the max charge (bad)
            # (i.e, cur charge cannot excede max_charge_bad, this limits it)
            cur_charge = min(cur_charge + SLOW_CHARGE_RATE * duration, MAX_CHARGE_BAD)

        # temp always increases
        cur_temp += SLOW_CHARGE_TEMP_INC * duration
        return

    # Create a local variable start charge and set it to the value of the current charge
    start_charge = cur_charge
 
    # if the starting charge is over the overcharge level, it counts as another overcharge.
    if start_charge >= OVERCHARGE_LEVEL:
        # this function returns true if the 3 overcharges are recorded within 6 hours
        if register_overcharge(cur_time):
            # Now that the battery health is bad, and the battery is over 90, we can finish the pass of the function
            # by adding the rest of the duration as temperature. The start charge is the battery percent for the rest of
            # the session
            cur_health = False
            cur_temp += SLOW_CHARGE_TEMP_INC * duration
            return
 
    # Fast charging is used for its full duration as long as it isn't greater than the duration passed to the function.
    # The slow duration is the remaining fraction of minutes after fast charging is complete
    fast_duration = min(duration_fast_charge_possible(), duration)
    slow_duration = duration - fast_duration

    # First calculate the charge after fast charging, then calculate the new charge using the slow charge duration.
    charge_after_fast = cur_charge + FAST_CHARGE_RATE * fast_duration
    new_charge = charge_after_fast + SLOW_CHARGE_RATE * slow_duration
 
    # Calculate the current temp, there is no upper bound for temperature so it is computed with no conditional statements.
    cur_temp += FAST_CHARGE_TEMP_INC * fast_duration + SLOW_CHARGE_TEMP_INC * slow_duration
 
    # Check if the battery was overcharged in the pass of the function
    if start_charge < OVERCHARGE_LEVEL <= new_charge:
        # Since the battery can't be charging fast while over 80%, it will never overcharge over the fast charge duration
        # So, the time of the overcharge is the fast_duration + the duration it took to get from the charge after fast charging
        # to 90
        time_of_overcharge = fast_duration + (OVERCHARGE_LEVEL - charge_after_fast) / SLOW_CHARGE_RATE

        # pass the time of the over charge + the current time.
        # again, register overcharge will return True if 3 overcharges have been registered within 6 hours
        if register_overcharge(cur_time + time_of_overcharge):
            # The health turns bad at the moment the level is reached, so
            # the charge stays there for the rest of the session.
            cur_health = False
            new_charge = OVERCHARGE_LEVEL

    # Limiting statement that bounds cur_charge as <= 100
    cur_charge = min(new_charge, MAX_CHARGE_GOOD)
 
 
def simulate_activity(activity: str, duration: float):
    # Simulate charging, usage, and idle
 
    global cur_charge, cur_temp, cur_time

    if activity == "charge":
        # simulate charging is defined as a function for organization purposes,
        # it takes the duration specified
        simulate_charging(duration)
 
    elif activity == "use":
        # Compute the duration that the battery can be used before dying, and the rest of the duration is the
        # number of minutes the battery is dead for the pass.

        # Return the smaller value between the duration specified, and the duration to drain the battery to 0
        use_duration = min(duration, cur_charge / -USAGE_DISCHARGE_RATE)
        dead_duration = duration - use_duration

        # Update current charge with use duration, and update current temp with the use duration temp and dead duration
        # temp
        cur_charge += USAGE_DISCHARGE_RATE * use_duration
        cur_temp += USAGE_TEMP_INC * use_duration + IDLE_TEMP_INC * dead_duration

    elif activity == "idle":
        # for idle, there are no conditions, only update the values
        cur_charge += IDLE_DISCHARGE_RATE * duration
        cur_temp += IDLE_TEMP_INC * duration
 
    else:
        # Base case to prevent errors.
        return
 
    # Neither the charge nor the temperature can go below 0
    cur_charge = max(cur_charge, MIN_CHARGE)
    cur_temp = max(cur_temp, MIN_TEMP)
 
    cur_time += duration
 
 
def charge_time_needed(minutes: float) -> float:
    # returns the charge time needed for the battery to be able to be used for duration minutes
 
    # charge needed to use the battery for duration minutes
    charge_needed_total = -USAGE_DISCHARGE_RATE * minutes

    # if the current charge is greater than or equal to the time needed to use
    if cur_charge >= charge_needed_total:
        return 0

    # init local variable max charge (in-line conditional kindof like ternery operator in java '? :')
    max_charge = MAX_CHARGE_GOOD if cur_health else MAX_CHARGE_BAD

    # if the needed charge is greater than the possible charge, no value satisfies the need 
    # (in one charge->use, note that techincally you could discharge completely then charge again)

    if charge_needed_total > max_charge:
        return None
 
    # A battery in bad health can only charge slowly. The duration is given by the slow charge rate
    if not cur_health:
        return (charge_needed_total - cur_charge) / SLOW_CHARGE_RATE
 
    # If fast charging alone is enough, the whole time is fast charging.
    fast_time_needed = (charge_needed_total - cur_charge) / FAST_CHARGE_RATE
    fast_time_possible = duration_fast_charge_possible()

    # if the time needed is less than or equal to the time possible, its fine and just return it
    if fast_time_needed <= fast_time_possible:
        return fast_time_needed
 
    # If not, charge as long as possible, then calculate the slow time using the remaining time
    charge_after_fast = cur_charge + FAST_CHARGE_RATE * fast_time_possible

    # fast time possible plus slow time (amnt of charge to get to needed charge / slow charge rate)
    return fast_time_possible + (charge_needed_total - charge_after_fast) / SLOW_CHARGE_RATE

def main():
    initialize()
    simulate_activity("charge", 30)
    print(get_cur_temp() == 30.0)
    print(get_cur_charge() == 100.0)
    print(duration_fast_charge_possible() == 0)
    simulate_activity("idle", 10)
    simulate_activity("use", 25)
    print(get_cur_temp() == 45.0)
    print(get_cur_charge() == 45.0)
    print(charge_time_needed(40) == 35.0)
 

 
if __name__ == '__main__':
    main()

