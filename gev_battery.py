def initialize():
    """Initialize the battery charge, temperature, health, and simulation constants."""

    global cur_charge, cur_temp, cur_health, overcharging, time_after_overcharging
    cur_charge = 50 # current charge in %
    cur_temp = 20 # current temperature in °C
    cur_health = True # True for good battery health False for bad battery health
    global elapsed_time, overcharge_1, overcharge_2

    elapsed_time = 0 #total time since the start of evaluation
    overcharge_1 = -1 #-1 means that event doesn't exist yet
    overcharge_2 = -1


    global FAST_CHARGE_RATE, SLOW_CHARGE_RATE, MIN_TEMP, MIN_CHARGE, MAX_TEMP_FAST_CHARGE, MAX_CHARGE_FAST_CHARGE, FAST_CHARGE_TEMP_INC, SLOW_CHARGE_TEMP_INC, USAGE_CHARGE_RATE, USAGE_TEMP_INC, IDLE_TEMP_INC, IDLE_CHARGE_RATE, MAX_CHARGE_GOOD, MAX_CHARGE_BAD

    MAX_CHARGE_FAST_CHARGE = 80 # the maximal charge for fast charging in units %

    MAX_TEMP_FAST_CHARGE = 40 # the maximal temperature for fast charging in units °C

    FAST_CHARGE_RATE = 3 #fast_charging charge rate in units %/min

    FAST_CHARGE_TEMP_INC = 0.5 #the increment in temperature when charging fast in units °C/min

    SLOW_CHARGE_RATE = 1 #slow_charging charge rate in units %/min

    SLOW_CHARGE_TEMP_INC = 0.25 # the increment in temperature when charging slow in units °C/min

    MIN_TEMP = 0 # the minimal temperature possible in units °C

    MIN_CHARGE = 0 # the minimal charge possible in units %

    MAX_CHARGE_GOOD = 100 # the maximal charge possible for healthy battery in units %

    MAX_CHARGE_BAD = 80 # the maximal charge possible for not healthy battery in units %

    USAGE_TEMP_INC = 1 # the increment in temperature when used in units °C/min

    USAGE_CHARGE_RATE = -2 #rate of charge when used (negative for discharge/losing charge) in units %/min

    IDLE_TEMP_INC = -1 #rate of increment of temperature (negative for decrement) in units °C/min

    IDLE_CHARGE_RATE = -0.5 #rate of charge when sitting idle (negative for discharge/losing charge) in units %/min



def get_cur_temp(): #return current temperature (in °C)
    """Return the current temperature of the battery in degrees Celsius."""
    return cur_temp

def get_cur_charge(): #return current charge (in %)
    """Return the current charge level of the battery as a percentage."""
    return cur_charge

def get_cur_battery_health(): #return current health (True for good False for bad)
    """Return True if the battery is in good health and False otherwise."""

    return cur_health

def duration_fast_charge_possible(): # return the max duration fast charging is possible (in min)
    """Return in min the maximum duration for which fast charging is possible."""

    temp_lim_time = (MAX_TEMP_FAST_CHARGE - cur_temp)/FAST_CHARGE_TEMP_INC
    # temperature limited time is the time for battery to reach max temp of fast charge (40°C)

    charge_lim_time = (MAX_CHARGE_FAST_CHARGE - cur_charge)/FAST_CHARGE_RATE
    # charge limited time is the time for battery to reach max charge of fast charge (80%)


    if cur_health: #when health is good

        if charge_lim_time > 0 and temp_lim_time > 0 : # check if time > 0 to avoid negative results

            return min(charge_lim_time, temp_lim_time) # the minimal time is the limiting time

        else:
            return 0


    else: #when health is bad
        return 0

def simulate_activity(activity: str, duration: int):
    """Simulate the battery performing the specified activity for duration minutes.
    activity is the activity performed by the battery and must be
    "charge", "use", or "idle". duration is the number of minutes
    for which the activity is performed. Update the battery's charge,
    temperature, and health accordingly.
    """
    global FAST_CHARGE_RATE, SLOW_CHARGE_RATE, MIN_TEMP, MIN_CHARGE, MAX_TEMP_FAST_CHARGE, MAX_CHARGE_FAST_CHARGE, FAST_CHARGE_TEMP_INC, SLOW_CHARGE_TEMP_INC, USAGE_CHARGE_RATE, USAGE_TEMP_INC, IDLE_TEMP_INC, IDLE_CHARGE_RATE, MAX_CHARGE_GOOD, MAX_CHARGE_BAD, cur_charge, cur_temp, cur_health
    global elapsed_time, overcharge_1, overcharge_2



    match activity:
        case "charge":
            was_bad = not cur_health # storing if the battery was initially bad or not

            if was_bad and cur_charge >= MAX_CHARGE_BAD:# if it turned bad during this session
                # while charge > 80 the charge doesn't get changed
                cur_temp += SLOW_CHARGE_TEMP_INC * duration
                elapsed_time += duration
                return

            # Remove the oldest overcharge if it is more than 6 hours old.
            if overcharge_1 >= 0 and elapsed_time - overcharge_1 > 360:
                overcharge_1 = overcharge_2
                overcharge_2 = -1

            # A new charging activity starting at 90% or more
            # immediately counts as an overcharge.
            if cur_charge >= 90:

                if overcharge_1 < 0: # if overcharge 1 didn't happen
                    overcharge_1 = elapsed_time #set overcharge 1 happening time to cur time

                elif overcharge_2 < 0:
                    overcharge_2 = elapsed_time #same logic here

                elif elapsed_time - overcharge_1 <= 360:
                    #if both overcharges happened and the 1st one happened less than 6 hours before
                    cur_health = False

                    if cur_charge > MAX_CHARGE_BAD: #if battery health went down while being at 90+ charge
                        # Charge stays at its current level
                        # for the rest of this session.
                        cur_temp += SLOW_CHARGE_TEMP_INC * duration
                    else:
                        cur_charge += SLOW_CHARGE_RATE * duration
                        cur_temp += SLOW_CHARGE_TEMP_INC * duration

                    elapsed_time += duration
                    return

                else: #if the furthest overcharge stored happened more than 6 hours ago
                    overcharge_1 = overcharge_2 #set new furthest overcharge to the previous one
                    overcharge_2 = elapsed_time #and the closest overcharge becomes at cur time

            fast_charge_duration = min(duration_fast_charge_possible(), duration)
            #min is to account for cases where duration < fast charge possible duration

            slow_charge_duration = duration - fast_charge_duration

            charge_before = cur_charge #save the value of battery before charging

            cur_charge += (FAST_CHARGE_RATE * fast_charge_duration+ SLOW_CHARGE_RATE * slow_charge_duration)

            cur_temp += (FAST_CHARGE_TEMP_INC * fast_charge_duration+ SLOW_CHARGE_TEMP_INC * slow_charge_duration)

            # Check whether the battery reached 90% during this session.
            if charge_before < 90 and cur_charge >= 90:

                if charge_before < MAX_CHARGE_FAST_CHARGE:
                    time_to_90 = (MAX_CHARGE_FAST_CHARGE - charge_before) / FAST_CHARGE_RATE #calculate time from cur to 90%

                    remaining_charge = (90 - MAX_CHARGE_FAST_CHARGE)

                    time_to_90 += (remaining_charge / SLOW_CHARGE_RATE) #add the slow charge time component to the time

                else:
                    time_to_90 = (90 - charge_before) / SLOW_CHARGE_RATE

                overcharge_time = elapsed_time + time_to_90

                if overcharge_1 < 0: #if 1st overcharge didn't happen
                    overcharge_1 = overcharge_time #assign overcharge time to overcharge_1

                elif overcharge_2 < 0: #same logic
                    overcharge_2 = overcharge_time

                elif overcharge_time - overcharge_1 <= 360: #if this overcharge is less than 6 hours after the furthest one
                    cur_health = False

                    # The battery becomes bad at the moment it
                    # reaches 90%, so it stays at that charge level
                    # for the rest of this charging session.
                    charge_at_90 = 90
                    time_after_90 = duration - time_to_90

                    cur_charge = charge_at_90
                    cur_temp += SLOW_CHARGE_TEMP_INC * time_after_90 #temperature continues to grow while charge is const

                else:
                    overcharge_1 = overcharge_2 #delete the furthest overcharge and assign the latest to corresponding values
                    overcharge_2 = overcharge_time

            if cur_health and cur_charge > MAX_CHARGE_GOOD: #don't let charge exceed max charge
                cur_charge = MAX_CHARGE_GOOD

            elif was_bad and cur_charge > MAX_CHARGE_BAD: #sets charge =80 if it was already bad and current charge is > 80
                cur_charge = MAX_CHARGE_BAD


            elapsed_time += duration

        case "use":

            duration_use = min((cur_charge - MIN_CHARGE) / - USAGE_CHARGE_RATE, duration)
            #negative because discharging
            #the time it will be used either before end of using or before dying

            duration_dead = duration - duration_use # time it is dead in duration

            cur_charge += USAGE_CHARGE_RATE * duration_use + IDLE_CHARGE_RATE * duration_dead

            cur_temp += USAGE_TEMP_INC * duration_use + IDLE_TEMP_INC * duration_dead


            if cur_charge < MIN_CHARGE: #not letting charge be less than min
                cur_charge = MIN_CHARGE

            if cur_temp < MIN_TEMP:
                cur_temp = MIN_TEMP #not letting temp be less than min

            elapsed_time += duration

        case "idle":

            cur_temp += IDLE_TEMP_INC * duration

            cur_charge += IDLE_CHARGE_RATE * duration

            if cur_charge < MIN_CHARGE: #not letting charge be less than min
                cur_charge = MIN_CHARGE

            if cur_temp < MIN_TEMP: #not letting temp be less than min
                cur_temp = MIN_TEMP
            elapsed_time += duration


def charge_time_needed(minutes):
    """Return the charging time needed to allow the battery to be used
    for minutes mins.
    Return 0 if the battery already has enough charge and None if the
    battery cannot be charged enough to support the specified usage.
    """

    charge_needed_ovr = -USAGE_CHARGE_RATE * minutes #the overall charge needed vor minutes mins of use

    if cur_charge >= charge_needed_ovr: # if already have the charge
        return 0

    if cur_health: #if impossible to get that charge
        if charge_needed_ovr > MAX_CHARGE_GOOD:
            return None
    else:
        if charge_needed_ovr > MAX_CHARGE_BAD:
            return None

    charge_needed = charge_needed_ovr - cur_charge #how many more % do we need

    fast_charge_duration = min(duration_fast_charge_possible(),charge_needed / FAST_CHARGE_RATE)

    charge_from_fast = (FAST_CHARGE_RATE * fast_charge_duration)

    charge_from_slow = charge_needed - charge_from_fast

    time_needed = (fast_charge_duration+ charge_from_slow / SLOW_CHARGE_RATE)

    return time_needed

    #this covers every scenario of fast_charge_duration and "minutes" possible


    return time_needed