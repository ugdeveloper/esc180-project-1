def initialize():
    """Initialize the battery to 50% charge, 20 degrees C and good health,
    reset the simulation clock and the overcharge history, and set the
    simulation constants.
    """

    # Mutable global variables
    global cur_charge, cur_temp, cur_health
    global elapsed_time, overcharge_1, overcharge_2

    # Immutable global variables (constants)
    global FAST_CHARGE_RATE, SLOW_CHARGE_RATE
    global FAST_CHARGE_TEMP_INC, SLOW_CHARGE_TEMP_INC
    global MAX_CHARGE_FAST_CHARGE, MAX_TEMP_FAST_CHARGE
    global USAGE_CHARGE_RATE, USAGE_TEMP_INC
    global IDLE_CHARGE_RATE, IDLE_TEMP_INC
    global MIN_CHARGE, MIN_TEMP
    global MAX_CHARGE_GOOD, MAX_CHARGE_BAD
    global OVERCHARGE_LEVEL, OVERCHARGE_WINDOW
 
    # Current charge of the battery in %. Always between MIN_CHARGE and
    # MAX_CHARGE_GOOD.
    cur_charge = 50.0
 
    # Current temperature of the battery in degrees C. Never below MIN_TEMP.
    cur_temp = 20.0
 
    # Current health of the battery: True for good, False for bad.
    cur_health = True
 
    # Total time simulated since the start of the simulation, in min.
    elapsed_time = 0
 
    # Time (in min since the start of the simulation) of the second most
    # recent overcharge. -1 means that this overcharge has not happened yet.
    overcharge_1 = -1
 
    # Time (in min since the start of the simulation) of the most recent
    # overcharge. -1 means that no overcharge has happened yet.
    overcharge_2 = -1
 
    # Maximal charge at which fast charging is possible, in %.
    MAX_CHARGE_FAST_CHARGE = 80
 
    # Maximal temperature at which fast charging is possible, in degrees C.
    MAX_TEMP_FAST_CHARGE = 40
 
    # Rate at which the charge increases when fast charging, in %/min.
    FAST_CHARGE_RATE = 3
 
    # Rate at which the temperature increases when fast charging,
    # in degrees C/min.
    FAST_CHARGE_TEMP_INC = 0.5
 
    # Rate at which the charge increases when slow charging, in %/min.
    SLOW_CHARGE_RATE = 1
 
    # Rate at which the temperature increases when slow charging,
    # in degrees C/min.
    SLOW_CHARGE_TEMP_INC = 0.25
 
    # Minimal possible temperature, in degrees C.
    MIN_TEMP = 0
 
    # Minimal possible charge, in %.
    MIN_CHARGE = 0
 
    # Maximal possible charge of a battery in good health, in %.
    MAX_CHARGE_GOOD = 100
 
    # Maximal possible charge of a battery in bad health, in %.
    MAX_CHARGE_BAD = 80
 
    # Rate at which the temperature increases when the battery is used,
    # in degrees C/min.
    USAGE_TEMP_INC = 1
 
    # Rate at which the charge changes when the battery is used, in %/min
    # (negative because the battery discharges).
    USAGE_CHARGE_RATE = -2
 
    # Rate at which the temperature changes when the battery is idle or
    # dead, in degrees C/min (negative because the battery cools down).
    IDLE_TEMP_INC = -1
 
    # Rate at which the charge changes when the battery is idle, in %/min
    # (negative because the battery discharges).
    IDLE_CHARGE_RATE = -0.5
 
    # Charge at or above which charging counts as an overcharge, in %.
    OVERCHARGE_LEVEL = 90
 
    # Time span in which 3 overcharges make the battery health bad, in min
    # (6 hours). A gap of exactly this length is not within the span.
    OVERCHARGE_WINDOW = 360
 
 
def get_cur_temp():
    """Return the current temperature of the battery in degrees Celsius
    as a float.
    """
 
    return float(cur_temp)
 
 
def get_cur_charge():
    """Return the current charge level of the battery as a percentage
    (a float).
    """
 
    return float(cur_charge)
 
 
def get_cur_battery_health():
    """Return True if the battery is in good health and False otherwise."""
 
    return cur_health
 
 
def duration_fast_charge_possible():
    """Return in min the maximum duration for which fast charging is
    possible, starting from the current charge, temperature and health.
    Return 0 if fast charging is not possible at all. 
    """
 
    if not cur_health:
        return 0
 
    # Time until the battery reaches the maximal temperature of fast charge
    temp_lim_time = (MAX_TEMP_FAST_CHARGE - cur_temp) / FAST_CHARGE_TEMP_INC
 
    # Time until the battery reaches the maximal charge of fast charge
    charge_lim_time = (MAX_CHARGE_FAST_CHARGE - cur_charge) / FAST_CHARGE_RATE
 
    if temp_lim_time <= 0 or charge_lim_time <= 0:
        return 0
 
    return min(temp_lim_time, charge_lim_time)
 
 
def charge_after_fast_charging(fast_duration):
    """Return the charge of the battery after it has been fast charged for
    fast_duration min, starting from the current charge. Assume that
    fast_duration is at most duration_fast_charge_possible().
    """
 
    if fast_duration == (MAX_CHARGE_FAST_CHARGE - cur_charge) \
            / FAST_CHARGE_RATE:
        # Fast charging ends exactly at its charge limit. Return the limit
        # itself to avoid floating point errors (e.g. 79.99999999999999).
        return MAX_CHARGE_FAST_CHARGE
 
    return cur_charge + FAST_CHARGE_RATE * fast_duration
 
 
def register_overcharge(overcharge_time):
    """Record an overcharge that happened overcharge_time min after the
    start of the simulation and return True if it is the third overcharge
    within 6 hours (the battery health becomes bad), False otherwise.
    Assume that overcharge_time is not earlier than any recorded overcharge.
    """
 
    global overcharge_1, overcharge_2
 
    # Only the two most recent earlier overcharges matter: the new one is
    # the third within 6 hours exactly when the older of these two is less
    # than 6 hours before it.
    makes_health_bad = overcharge_1 >= 0 and overcharge_2 >= 0 \
        and overcharge_time - overcharge_1 < OVERCHARGE_WINDOW
 
    overcharge_1 = overcharge_2
    overcharge_2 = overcharge_time
 
    return makes_health_bad
 
 
def simulate_charging(duration):
    """Simulate charging the battery for duration min, updating its charge,
    temperature and health. Assume that duration is a positive int. Do not
    update the simulation clock.
    """
 
    global cur_charge, cur_temp, cur_health
 
    if not cur_health:
        # A battery in bad health charges slowly and not past
        # MAX_CHARGE_BAD. If it is at or above that level, its charge
        # stays where it is. Its temperature rises in any case.
        if cur_charge < MAX_CHARGE_BAD:
            cur_charge = min(cur_charge + SLOW_CHARGE_RATE * duration,
                             MAX_CHARGE_BAD)
 
        cur_temp += SLOW_CHARGE_TEMP_INC * duration
        return
 
    start_charge = cur_charge
 
    # Starting to charge at or above the overcharge level immediately
    # counts as an overcharge.
    if start_charge >= OVERCHARGE_LEVEL:
        if register_overcharge(elapsed_time):
            # The health turns bad at the start of this session, so the
            # charge stays where it is for the whole session.
            cur_health = False
            cur_temp += SLOW_CHARGE_TEMP_INC * duration
            return
 
    # Fast charging is used for as long as possible, then slow charging.
    fast_duration = min(duration_fast_charge_possible(), duration)
    slow_duration = duration - fast_duration
 
    charge_after_fast = charge_after_fast_charging(fast_duration)
    new_charge = charge_after_fast + SLOW_CHARGE_RATE * slow_duration
 
    # The temperature keeps rising at the slow rate even when the charge
    # can no longer increase, so it does not depend on what happens below.
    cur_temp += FAST_CHARGE_TEMP_INC * fast_duration \
        + SLOW_CHARGE_TEMP_INC * slow_duration
 
    # Check whether the charge reached the overcharge level in this
    # session. This can only happen during slow charging, since fast
    # charging stops at MAX_CHARGE_FAST_CHARGE, which is below that level.
    if start_charge < OVERCHARGE_LEVEL <= new_charge:
        time_to_overcharge = fast_duration \
            + (OVERCHARGE_LEVEL - charge_after_fast) / SLOW_CHARGE_RATE
 
        if register_overcharge(elapsed_time + time_to_overcharge):
            # The health turns bad at the moment the level is reached, so
            # the charge stays there for the rest of the session.
            cur_health = False
            new_charge = OVERCHARGE_LEVEL
 
    cur_charge = min(new_charge, MAX_CHARGE_GOOD)
 
 
def simulate_activity(activity: str, duration: int):
    """Simulate the battery performing the specified activity for duration
    minutes. activity is the activity performed by the battery and must be
    "charge", "use", or "idle". duration is the number of minutes
    for which the activity is performed. Update the battery's charge,
    temperature, and health accordingly. Do nothing if activity is not
    one of these.
    """
 
    global cur_charge, cur_temp, elapsed_time
 
    if activity == "charge":
        simulate_charging(duration)
 
    elif activity == "use":
        # The battery is used until it runs out of charge. Afterwards it is
        # dead: its charge stays at MIN_CHARGE, and its temperature drops
        # as it does when the battery is idle.
        use_duration = min(cur_charge / -USAGE_CHARGE_RATE, duration)
        dead_duration = duration - use_duration
 
        cur_charge += USAGE_CHARGE_RATE * use_duration
        cur_temp += USAGE_TEMP_INC * use_duration \
            + IDLE_TEMP_INC * dead_duration
 
    elif activity == "idle":
        cur_charge += IDLE_CHARGE_RATE * duration
        cur_temp += IDLE_TEMP_INC * duration
 
    else:
        # Any other activity has no effect (not even on the clock).
        return
 
    # Neither the charge nor the temperature can go below its minimum.
    cur_charge = max(cur_charge, MIN_CHARGE)
    cur_temp = max(cur_temp, MIN_TEMP)
 
    elapsed_time += duration
 
 
def charge_time_needed(minutes):
    """Return the charging time needed to allow the battery to be used
    for minutes mins.
    Return 0 if the battery already has enough charge and None if the
    battery cannot be charged enough to support the specified usage.
    """
 
    # Overall charge needed to use the battery for minutes min
    charge_needed_total = -USAGE_CHARGE_RATE * minutes
 
    if cur_charge >= charge_needed_total:
        return 0
 
    if cur_health:
        max_charge = MAX_CHARGE_GOOD
    else:
        max_charge = MAX_CHARGE_BAD
 
    if charge_needed_total > max_charge:
        return None
 
    # A battery in bad health can only charge slowly.
    if not cur_health:
        return (charge_needed_total - cur_charge) / SLOW_CHARGE_RATE
 
    # If fast charging alone is enough, the whole time is fast charging.
    fast_time_needed = (charge_needed_total - cur_charge) / FAST_CHARGE_RATE
    fast_time_possible = duration_fast_charge_possible()
 
    if fast_time_needed <= fast_time_possible:
        return fast_time_needed
 
    # Otherwise charge fast for as long as possible, then slowly.
    charge_after_fast = charge_after_fast_charging(fast_time_possible)
 
    return fast_time_possible \
        + (charge_needed_total - charge_after_fast) / SLOW_CHARGE_RATE
 
 
if __name__ == '__main__':
    # Example simulation from the handout.
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
 


