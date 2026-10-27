# Liverpool injuries: Slot vs Iraola

Status: agreed scope only. Nothing built.

## Question

Does Iraola's style cause more injuries than Slot's? Carragher raised it in June 2026 ([Empire of the Kop](https://www.empireofthekop.com/2026/06/02/carragher-raises-concerns-over-potential-liverpool-drop-off-under-iraola/amp/)).

## Agreed

- Team: Liverpool.
- Periods: Slot 2024/25 and 2025/26 (full seasons), Iraola 2026/27 (weeks so far, marked as a small sample).
- Granularity: week by week.
- Injury definition: the player missed at least 1 game (`missedGamesCount >= 1`). This matches the time-loss injury in the [consensus statement (Fuller et al., BJSM)](https://bjsm.bmj.com/content/40/3/193).
- Data: [football-injuries](https://github.com/Mohammad99Shweiki/football-injuries), run locally in `~/projects/football-injuries` with `--leagues EPL --seasons 2024-2026`. Injury data is Transfermarkt (`tm_injuries.csv`). Run manually so far.

## Not decided

- What each week shows: new injuries that week, running total, or players out that week.
- Whether to limit to key players, and how "key" is defined.
- Chart type. Published examples: [injurytools](https://archive.linux.duke.edu/cran/web/packages/injurytools/vignettes/visualize-injury-data.html) (player timeline, monthly prevalence, ranking, risk matrix), [Sky Sports / Premier Injuries](https://www.skysports.com/football/news/11095/13289368/premier-league-injuries-have-arsenal-and-tottenham-suffered-most) (per-club counts and days lost).
- Automating the data refresh.
