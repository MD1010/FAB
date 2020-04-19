import arrow

TRIAL = "A"
BRONZE = "B"
SILVER = "C"
GOLD = "D"
LEGEND = "E"

plan_accounts_limit = {
    TRIAL: 1,
    BRONZE: 2,
    SILVER: 5,
    GOLD: 10,
    LEGEND: 50
}

plan_expiration_dates = {
    TRIAL: arrow.now().shift(hours=3).datetime.isoformat(),
    BRONZE: arrow.now().shift(months=1).datetime.isoformat(),
    SILVER: arrow.now().shift(months=3).datetime.isoformat(),
    GOLD: arrow.now().shift(months=6).datetime.isoformat(),
    LEGEND: arrow.now().shift(years=1).datetime.isoformat(),
}
