def initialize():
   """
Here is my new version of the project. I think it is better than your previous one because:

1. it can input non integer values for duration (yours couldn't because of the range(duration) part of your programm) P.S. i checked it said assume duration is a positive integer so i kinda fucked up here))

2. it is much more effective (yours needed to run all the loops "duration" times while mine is with 'while' and runs a loop maximum 2 times)

3. it is shorter than yours(if we remove the skip-lines and my comments i did for the code to be more understandable, my code would be shorter)

4. the comments i have written would make so much easier both the understanding of the code (both by TA's and us) and the presentation of the code (since half of our mark depends on personal presentation)

5. and i think you either forgot or didn't write a couple of requirements

the only disadvantage is that i didn't think of a way to represent the overcharging because i didn't understand the requirement please think a way to execute that in this code(i will also). thanks in advance

"""


def initialize():
    """Initialize the battery charge, temperature, health, and simulation constants."""

    global cur_charge, cur_temp, cur_health
    cur_charge = 50 # current charge in %
    cur_temp = 20 # current temperature in °C
    cur_health = True # True for good battery health False for bad battery health

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
    global cur_charge, cur_temp

    match activity:
        case "charge":
            # fast charge for as long as it is possible (but no longer than duration),
            # computed ONCE before any state changes
            fast_duration = min(duration, duration_fast_charge_possible())
            # whatever is left of the duration is slow charging
            slow_duration = duration - fast_duration

            # fast charging phase
            cur_charge += fast_duration * FAST_CHARGE_RATE
            cur_temp += fast_duration * FAST_CHARGE_TEMP_INC

            # slow charging phase
            if cur_health:
                cur_charge += SLOW_CHARGE_RATE * slow_duration
                if cur_charge > MAX_CHARGE_GOOD:
                    cur_charge = MAX_CHARGE_GOOD
            elif cur_charge <= MAX_CHARGE_BAD:
                # a bad battery only charges up to its max; above it, charge stays as is
                cur_charge += SLOW_CHARGE_RATE * slow_duration
                if cur_charge > MAX_CHARGE_BAD:
                    cur_charge = MAX_CHARGE_BAD

            # temperature keeps rising during slow charging even when charge is capped
            cur_temp += SLOW_CHARGE_TEMP_INC * slow_duration

        case "use":
            # minutes until the battery is empty
            duration_use_possible = -(cur_charge - MIN_CHARGE) / USAGE_CHARGE_RATE

            if duration >= duration_use_possible:
                cur_charge = MIN_CHARGE
                cur_temp += USAGE_TEMP_INC * duration_use_possible  # heats up until dead
                cur_temp += IDLE_TEMP_INC * (duration - duration_use_possible)  # cools afterwards
                if cur_temp < MIN_TEMP:
                    cur_temp = MIN_TEMP
            else:
                cur_charge += USAGE_CHARGE_RATE * duration
                cur_temp += USAGE_TEMP_INC * duration

        case "idle":
            cur_temp += IDLE_TEMP_INC * duration
            cur_charge += IDLE_CHARGE_RATE * duration

            if cur_charge < MIN_CHARGE:
                cur_charge = MIN_CHARGE
            if cur_temp < MIN_TEMP:
                cur_temp = MIN_TEMP

        case _:
            pass  # unknown activity: do nothing

def charge_time_needed(minutes): # return the time needed to charge to than be used "minutes" mins
    """Return the charging time needed to allow the battery to be used
    for minutes mins.
    Return 0 if the battery already has enough charge and None if the
    battery cannot be charged enough to support the specified usage.
    """

    charge_needed_ovr = -USAGE_CHARGE_RATE *minutes #the overall charge in % needed for "minutes" mins of usage

    if cur_health: # if health is good
        if charge_needed_ovr > MAX_CHARGE_GOOD:
            return None

    else: # if health is bad
        if charge_needed_ovr > MAX_CHARGE_BAD:
            return None

    max_charge_fast_charge = duration_fast_charge_possible() * FAST_CHARGE_RATE #max charge to get via fast charge

    if charge_needed_ovr - cur_charge <= max_charge_fast_charge:
        #if all the charge needed can be provided via fast charge

        time_needed = (charge_needed_ovr - cur_charge) / FAST_CHARGE_RATE

        if time_needed <= 0: # if you already have the overall charge needed
            return 0
        else:
            return time_needed

    elif duration_fast_charge_possible() == 0 : #if all the charging should be done via slow charge
        time_needed = (charge_needed_ovr - cur_charge) / SLOW_CHARGE_RATE

        if time_needed <= 0: # if you already have the overall charge needed
            return 0
        else:
            return time_needed

    else: # if charging should be a combination of slow and fast charge
        time_needed = ((charge_needed_ovr - cur_charge) - FAST_CHARGE_RATE * duration_fast_charge_possible()) / SLOW_CHARGE_RATE + duration_fast_charge_possible()
        #how many more charge do we need - the charge that is provided with fast charge = the amount of slow charge
        # amount of slow charge needed / slow charge rate gives us the time for slow charge
        #than add the time of fast charging which is duration_fast_charge_possible() and we get the time_needed

        if time_needed <= 0: # if you already have the overall charge needed
            return 0
        else:
            return time_needed
"""
#
#
# I suspect this block can be optimized to just 1 equation but i will check that later
#
#
"""

if __name__ == "__main__":
    initialize()
    simulate_activity("charge",30.5)
    print(get_cur_temp())
    print(get_cur_charge())
    print(duration_fast_charge_possible())
    simulate_activity("idle", 10.2)
    simulate_activity("use", 25.3)
    print(get_cur_temp())
    print(get_cur_charge())
    print(charge_time_needed(40.9))
    #add your tests here





