# What I checked, and what the agent got wrong

## What the agent got wrong

The first "fix" pass made all the tests green, and that is exactly why it was easy to trust and wrong to
trust. I only caught the problems because I read every file and then probed edge cases the tests never
touched, instead of stopping at "pytest passes".

- **The average wear was still wrong.** The `//` was changed to `/`, but a car with no service reading was
  counted as 0% wear while still being divided into the average. The code comment even said "exclude". One
  99.3% car plus one unreadable car gave 49.7% instead of 99.3%. I noticed it when I ran the sample by hand
  and the number looked half of what it should be. `verify.py` could not catch it either, because its
  average check only uses two cars that both have readings.
- **Empty fleet crashed.** `fleet_summary([])` divided by zero.
- **Inconsistent readings were silently accepted.** An odometer lower than the last-service reading gave
  negative wear and the car was quietly treated as fine.
- **The two copies of the rules.** `km_wachter.py` hardcoded 15000 and 80 while `settings.cfg` held the same
  numbers, and nothing connected them. The agent left that 2016 "nobody knows which one wins" comment as it
  was. Now the code reads `settings.cfg`, and a test pins the approved values.
- **analyze.py told a story the code did not compute.** The "Key findings" text and the percentages were typed
  in by hand, and the header said only two factors matter while `load_factor` passed the script's own cutoff
  and was used in the score. The "top 10 broke down" result was also measured on the same cars the score was
  built from, which flatters it.
- **Small leftovers:** dead helpers (`mean`, `format_percent` which truncated 99.9 to 99, `debug`), unknown
  keys in `settings.cfg` being ignored silently, and the log being lost if the report crashed halfway.

## What I checked before I accepted its work

- I checked out the original commit and ran the tests there to see the real starting state: 3 of 3 tests
  failed, for the `//` flooring and the "missing reading counts as 0" bug.
- On the final code, `pytest` passes (16 tests) and `python verify.py` passes every check.
- The wear bug: a test that 14,900 km of 15,000 is flagged and reports about 99.3%.
- The 80% rule is untouched: tests assert the constants are 15000 and 80, and that exactly 12,000 km is
  flagged while 11,999 km is not. `settings.cfg` has no changes in git, and a test reads it and checks the
  same two values.
- I added tests for each edge case above (no reading, no odometer, odometer below last service, empty fleet,
  average ignoring unreadable cars, a value containing "=" in the config, a misspelled config key).
- I ran `python fleet_report.py` on `fleet_sample.json` end to end and checked the output by hand.

## What the data actually said

The obvious factor, total mileage (`odometer_km`), does not predict breakdowns: the average is 53,448 km for
cars that broke down and 53,302 km for those that did not (correlation 0.00). Age is the same story
(correlation 0.00). "Old, high-mileage cars break down" is not supported by this fleet's data.

What does separate them is how hard the car is being worked right now:
- **km since last service**: correlation 0.40, broken-down cars average 61% higher. The strongest signal.
- **average daily km**: correlation 0.25, about 21% higher.
- **load factor**: correlation 0.22, about 19% higher.

The risk score built from those three works on cars it has not seen (AUC 0.84 with 5-fold cross-validation,
where 0.50 is a coin flip). But I want to be honest about the limit: the plain 80% rule flags 32 cars and
catches 17 of the 26 breakdowns, and the same number of cars picked by the score catches only 18. The score
adds little on top of "km since service". Its real value is the 9 breakdowns that happened on cars the 80%
rule would not flag, and with only 120 cars the weights should be treated as a guide, not a guarantee.
