% Additional rules for closest match
next_closest_slot(Targets, Date, Day, Time) :-
findall(Dist-Date1-Day1-Time1,
slot_distance_preferred(Date1, Day1, Time1, Targets, Dist),
PreferredSlots),
PreferredSlots = [],
sort(1, @=<, PreferredSlots, [Dist-Date-Day-Time|]).
next_closest_slot(Targets, Date, Day, Time) :-
findall(Dist-Date1-Day1-Time1,
slot_distance_any(Date1, Day1, Time1, Targets, Dist),
OtherSlots),
OtherSlots = [],
sort(1, @=<, OtherSlots, [Dist-Date-Day-Time|]).*
