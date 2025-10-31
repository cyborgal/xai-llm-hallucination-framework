% validation_rules.pl
% Static rules used by primary analyses in the manuscript.
% Handles exact times and ambiguous windows (morning/afternoon/evening).
% No "closest match" or auto-correction rules are included.

:- module(validation_rules, [
    time_to_minutes/2,
    map_day/2,
    ambiguous_window/3,
    overlaps/4,
    within_slot/3,
    is_time_available/2,
    is_window_available/3,
    validate_answer/4,
    json_out/2
]).

% ---------- Utilities ----------

time_to_minutes(TimeStr, Minutes) :-
    atom(TimeStr),
    atom_codes(TimeStr, Codes),
    append(HCodes, [0':|MCodes], Codes),
    atom_codes(HH, HCodes),
    atom_codes(MM, MCodes),
    atom_number(HH, H),
    atom_number(MM, M),
    Minutes is H*60 + M.

map_day(Str, DayAtom) :-
    ( atom(Str) -> S=Str ; atom_string(S, Str) ),
    downcase_atom(S, L),
    member(DayAtom, [monday,tuesday,wednesday,thursday,friday,saturday,sunday]),
    atom_string(DayAtom, LD),
    L = LD.

% Ambiguous time-of-day windows (minutes from midnight).
% Adjust only if manuscript definitions change.
ambiguous_window(morning,    540,  720).  % 09:00–12:00
ambiguous_window(afternoon,  720, 1020).  % 12:00–17:00
ambiguous_window(evening,   1020, 1320).  % 17:00–22:00

% Inclusive-overlap between [A1,A2] and [B1,B2].
overlaps(A1, A2, B1, B2) :-
    A1 =< A2, B1 =< B2,
    max(A1, B1, S), min(A2, B2, E), S =< E.

max(A,B,A) :- A>=B, !.
max(_,B,B).
min(A,B,A) :- A=<B, !.
min(_,B,B).

% ---------- Facts expected ----------
% available_slot(Date, DayAtom, "HH:MM", StartMin, EndMin).
% (Facts come from Python or dynamic prompt; not defined here.)

% True if exact time lies within any available slot on Day.
within_slot(Day, TimeMin, Label) :-
    available_slot(_Date, Day, Label, StartMin, EndMin),
    StartMin =< TimeMin, TimeMin =< EndMin.

is_time_available(Day, TimeStr) :-
    map_day(Day, D), time_to_minutes(TimeStr, M),
    within_slot(D, M, _).

% True if the ambiguous window overlaps any available slot on Day.
is_window_available(Day, WindowAtom, OverlapLabel) :-
    map_day(Day, D),
    ambiguous_window(WindowAtom, W1, W2),
    available_slot(_Date, D, OverlapLabel, S1, S2),
    overlaps(W1, W2, S1, S2).

% ---------- Primary validation entry point ----------
% validate_answer(+Day, +Request, -Verdict, -Reason)
% Request := exact_time("HH:MM") ; ambiguous(window_atom)
% Verdict := ok ; error
validate_answer(Day, exact_time(TimeStr), ok, "exact time is available") :-
    is_time_available(Day, TimeStr), !.
validate_answer(Day, exact_time(TimeStr), error, Reason) :-
    \+ is_time_available(Day, TimeStr),
    format(atom(Reason), "exact time ~w on ~w is not within any available interval", [TimeStr, Day]).

validate_answer(Day, ambiguous(Window), ok, R) :-
    is_window_available(Day, Window, Label),
    format(atom(R), "ambiguous window (~w) overlaps slot labeled ~w", [Window, Label]), !.
validate_answer(Day, ambiguous(Window), error, R) :-
    format(atom(R), "ambiguous window (~w) has no overlap on ~w", [Window, Day]).

% ---------- Minimal JSON printing ----------
json_bool(true,  "true").
json_bool(false, "false").

json_out(ok, Reason) :-
    json_bool(true, TB),
    format('{"is_valid": ~w, "reason": "~w"}~n', [TB, Reason]).
json_out(error, Reason) :-
    json_bool(false, FB),
    format('{"is_valid": ~w, "reason": "~w"}~n', [FB, Reason]).
