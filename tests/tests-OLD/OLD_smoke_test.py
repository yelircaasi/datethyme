from datethyme import Date, DateTime, Time

t0 = Time.parse("00:37")
t1 = Time.parse("05:15:30.345")

td_a = t1 - t0
print(f"{td_a.days:.3f} days between {t0} and {t1}.")
print(f"{td_a.hours:.3f} hours between {t0} and {t1}.")
print(f"{td_a.minutes:.3f} minutes between {t0} and {t1}.")
print(f"{td_a.seconds:.3f} seconds between {t0} and {t1}.")

print(f"{td_a.full_days} full days between {t0} and {t1}.")
print(f"{td_a.full_hours} full hours between {t0} and {t1}.")
print(f"{td_a.full_minutes} full minutes between {t0} and {t1}.")
print(f"{td_a.full_seconds} full seconds between {t0} and {t1}.")

d0 = Date.parse("2025-03-17")
d1 = Date.parse("2026-1-1")

dt0 = DateTime.parse("2025-06-15 14:30")
dt1 = DateTime.parse("2025-7-05__23:59:59.999")
dt2 = DateTime.parse("2025-10-10_20:00:00.01")

print(t0)
print(t1)
print(d0)
print(d1)
print(dt0)
print(dt1)
print(dt2)
