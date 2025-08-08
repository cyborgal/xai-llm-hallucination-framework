% Facts from availability
available_slot('2025-07-31', thursday, '10:15', 510, 720). % Start: 08:30, End: 12:00
available_slot('2025-07-31', thursday, '15:45', 945, 1080).
available_slot('2025-08-01', friday, '18:00', 1080, 1200).
% User preferences
preferred_day(thursday).
preferred_time('10:15').
% Helper: Convert time to minutes
time_to_minutes(TimeStr, Minutes) :-
atom_codes(TimeStr, Codes),
append(HCodes, [58|MCodes], Codes),
atom_codes(HH, HCodes), atom_codes(MM, MCodes),
atom_number(HH, H), atom_number(MM, M),
Minutes is H*60 + M.
% Rule: Valid slot within range
valid_slot(Date, Day, Time, StartMin, EndMin) :-
available_slot(Date, Day, Time, StartMin, EndMin),
preferred_day(Day),
preferred_time(Time),
time_to_minutes(Time, Min),
Min >= StartMin, Min =< EndMin.
% Query exact matches
:- valid_slot(D, Day, T, _, _), write(D), write('|'), write(Day), write('|'), write(T), nl, fail.
