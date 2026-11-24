% Public deterministic validator accompanying JEI article 25-313.
:- module(validation_rules, [validate_answer/4, json_out/2]).
:- use_module(library(http/json)).
:- dynamic available_slot/5.

% Valid 24-hour strings, represented as "HH:MM".
time_to_minutes(Time, Minutes) :-
    (string(Time) -> atom_string(Atom, Time) ; Atom = Time),
    atom(Atom),
    atomic_list_concat([HAtom, MAtom], ':', Atom),
    atom_number(HAtom, H), atom_number(MAtom, M),
    between(0, 23, H), between(0, 59, M),
    Minutes is H * 60 + M.

map_day(Day, Normal) :-
    (string(Day) -> string_lower(Day, Lower), atom_string(Normal, Lower)
    ; atom(Day) -> downcase_atom(Day, Normal)),
    memberchk(Normal, [monday,tuesday,wednesday,thursday,friday,saturday,sunday]).

ambiguous_window(morning, 540, 720).
ambiguous_window(afternoon, 720, 1020).
ambiguous_window(evening, 1020, 1320).

% Half-open availability windows: the end boundary is not a start time.
is_time_available(Day, Time) :-
    map_day(Day, Normal),
    time_to_minutes(Time, Minute),
    available_slot(_, Normal, _, Start, End),
    Start =< Minute, Minute < End, !.

is_window_available(Day, Window) :-
    map_day(Day, Normal), ambiguous_window(Window, WStart, WEnd),
    available_slot(_, Normal, _, SStart, SEnd),
    max(WStart, SStart) < min(WEnd, SEnd), !.

validate_answer(Day, exact_time(Time), ok, "exact time is available") :-
    is_time_available(Day, Time), !.
validate_answer(Day, exact_time(_), error, "exact time is not available") :- !.
validate_answer(Day, ambiguous(Window), ok, "requested window overlaps availability") :-
    is_window_available(Day, Window), !.
validate_answer(_, ambiguous(_), error, "requested window has no available overlap").

json_out(Verdict, Reason) :-
    (Verdict == ok -> Valid = true ; Valid = false),
    json_write_dict(current_output, _{is_valid:Valid, reason:Reason}),
    nl.
