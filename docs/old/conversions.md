# Conversions

## Span Creation

Assume the following variable types in the following examples:

``` python
d: Date
t: Time
ds: DateSpan
ts: TimeSpan
dts: DateTimeSpan

d0: Date
d1: Date
...
```

A span instance can be created from:

- two identical point types:
    * `#!python (d0 >> d1) == DateSpan(d0, d1)`
    * `#!python (t0 >> t1) == TimeSpan(t0, t1)`
    * `#!python (dt0 >> dt1) == TimeSpan(dt0, dt1)`
- a point type and a corresponding span type:
    * `#!python (d >> ds) == DateSpan(d, ds.end)`
    * `#!python (t >> ts) == TimeSpan(t, ts.end)`
    * `#!python (dt >> dts) == TimeSpan(dt, dts.end)`
- a span type and a corresponding point type:
    * `#!python (ds >> d) == DateSpan(ds.start, d)`
    * `#!python (ts >> t) == DateSpan(ts.start, t)`
    * `#!python (dts >> dt) == DateSpan(dts.start, dt)`
- two identical span types:
    * `#!python (ds0 >> ds1) == DateSpan(ds0.start, ds1.end)`
    * `#!python (ts0 >> ts1) == DateSpan(ts0.start, ts1.end)`
    * `#!python (dts0 >> dts1) == DateTimeSpan(dts0.start, dts1.end)`

## Type Compability Tables

### Minimal Span Creation

| `#!python >>`           | `#!python Date`         | `#!python Time` | `#!python DateTime` | `#!python DateSpan` | `#!python TimeSpan` | `#!python DateTimeSpan` |
| :---------------------- | :-----------------:     | :-------------: | :-----------------: | :-----------------: | :-----------------: | :---------------------: |
| `#!python Date`         | `#!python DateSpan`     | ❌          | `#!python DateTimeSpan` | `#!python DateSpan` | ❌ | `#!python DateTimeSpan` |
| `#!python Time`         | ❌                      | `#!python TimeSpan` | `#!python ___`  | `#!python ___`  | `#!python ___`  | `#!python ___`  |
| `#!python DateTime`     | `#!python dt.start >> `         | `#!python ___`  | `#!python ___`  | `#!python ___`  | `#!python ___`  | `#!python ___`  |
| `#!python DateSpan`     | `#!python ___`         | `#!python ___`  | `#!python ___`  | `#!python ___`  | `#!python ___`  | `#!python ___`  |
| `#!python TimeSpan`     | `#!python DateTimeSpan` | `#!python TimeSpan`     | `#!python DateTimeSpan` | `#!python DateTimeSpan` | `#!python TimeSpan` | `#!python DateTimeSpan` |
| `#!python DateTimeSpan` | `#!python DateTimeSpan` | `#!python DateTimeSpan` | `#!python DateTimeSpan` | `#!python DateTimeSpan` | `#!python DateTimeSpan` | `#!python DateTimeSpan` |

Where a combination is not supported, it is because there is some ambiguity and the trouble would outweigh any convenience.
Usually there is a more explicit, and therefore safer, alternative. For example, `#!python d >> t` is unnecessary because `#!python d.start >> d & t` is clearer and also very concise.

### Span Extension

| `#!python >>=`           | `#!python Date`         | `#!python Time` | `#!python DateTime` | `#!python DateSpan` | `#!python TimeSpan` | `#!python DateTimeSpan` |
| :---------------------- | :-----------------:     | :-------------: | :-----------------: | :-----------------: | :-----------------: | :---------------------: |
| `#!python Date`         | use `#!python d >> d`         | use `#!python d >> t`  | use `#!python d ** dt`  | `#!python ___`  | `#!python ___`  | `#!python ___`  |
| `#!python Time`         | use `#!python t >> d`         | use `#!python t >> t`  | use `#!python t ** dt`  | `#!python ___`  | `#!python ___`  | `#!python ___`  |
| `#!python DateTime`     | use `#!python dt >> d`         | use `#!python dt >> t`  | use `#!python dt ** dt`  | `#!python ___`  | `#!python ___`  | `#!python ___`  |
| `#!python DateSpan`     | `#!python DateSpan`         | `#!python DateTimeSpan`  | `#!python DateTimeSpan`  | `#!python DateSpan`  | `#!python DateTimeSpan`  | `#!python DateTimeSpan`  |
| `#!python TimeSpan`     | `#!python DateTimeSpan`         | `#!python TimeSpan`  | `#!python DateTimeSpan`  | `#!python DateTimeSpan`  | `#!python TimeSpan`  | `#!python DateTimeSpan`  |
| `#!python DateTimeSpan` | `#!python DateTimeSpan`         | `#!python DateTimeSpan`  | `#!python DateTimeSpan`  | `#!python DateTimeSpan`  | `#!python DateTimeSpan`  | `#!python DateTimeSpan`  |

### Range Creation

All 9 combinations between `#!python Date`, `#!python DateTime`, and `#!python DateRange` result in a `#!python DateRange`.
For other `#!python datethyme` types, the `#!python **` is not defined.

| `#!python **`           | `#!python Date`         | `#!python DateTime` | `#!python DateRange` |
| :---------------------- | :-----------------:     | :-------------: | :-----------------: |
| `#!python Date`         | `#!python DateRange`         | `#!python DateRange`  | `#!python DateRange`  |
| `#!python DateTime`     | `#!python DateRange`         | `#!python DateRange`  | `#!python DateRange`  |
| `#!python DateRange`     | `#!python DateRange`         | `#!python DateRange`  | `#!python DateRange`  |

Range creation using the operator `#!python **` is defined only for date ranges because for unit-specific time ranges, it is ambiguous and needs additional information to be passed as parameters to the relevant methods. However, it is defined for already-instantiated time range types.

TODO

| `#!python **`             | `#!python HourRange` | `#!python HourRangeDated` | `#!python Date` | `#!python Time` | `#!python DateTime`  | `#!python DateRange` |
| :------------------------ | :-----------------:   | :-----------------------: | :-----------------: | :-----------------: | :-----------------: | :---------------------: |
| `#!python HourRange`      | `#!python HourRange`  | `#!python ___`  | `#!python ___`  | `#!python ___`  | `#!python ___`  | `#!python ___`  |
| `#!python HourRangeDated` | `#!python HourRangeDated`  | `#!python HourRangeDated`  | `#!python ___`  | `#!python ___`  | `#!python ___`  | `#!python ___`  |
| `#!python Date`           | `#!python ___`        | `#!python ___`  | `#!python ___`  | `#!python ___`  | `#!python ___`  | `#!python ___`  |
| `#!python Time`           | `#!python ___`        | `#!python ___`  | `#!python ___`  | `#!python ___`  | `#!python ___`  | `#!python ___`  |
| `#!python DateTime`       | `#!python ___`        | `#!python ___`  | `#!python ___`  | `#!python ___`  | `#!python ___`  | `#!python ___`  |
| `#!python DateRange`      | `#!python ___`        | `#!python ___`  | `#!python ___`  | `#!python ___`  | `#!python ___`  | `#!python ___`  |

TODO: minutes

TODO: seconds

### Range Extension

Range extension never results in a smaller range than the left operand. If `#!python d0 > d1`, `#!python d0 **= d1` results in a DateRange of length 0.

| `#!python **=`           | `#!python Date`         | `#!python DateTime` | `#!python DateRange` |
| :---------------------- | :-----------------:     | :-------------:     | :-----------------: |
| `#!python Date`         | use `#!python d ** d`    | use `#!python d ** dt`      | `#!python DateRange`  |
| `#!python DateTime`     | use `#!python dt ** d`          | use `#!python dt ** dt`      | `#!python DateRange`  |
| `#!python DateRange`    | `#!python DateRange`          | `#!python DateRange`      | `#!python DateRange`  |

For all non-date range types (`#!python HourRange`, `#!python MinuteRange`, `#!python SecondRange`, `#!python HourRangeDated`, `#!python MinuteRangeDated`, `#!python SecondRangeDated`), the operations are only defined with point types, date ranges, and range types having the same unit of time.

| `#!python **=`             | `#!python HourRange` | `#!python HourRangeDated` | `#!python Date` | `#!python Time` | `#!python DateTime`  | `#!python DateRange` |
| :------------------------ | :-----------------:   | :-----------------------: | :-----------------: | :-----------------: | :-----------------: | :---------------------: |
| `#!python HourRange`      | `#!python HourRange`  | `#!python ___`  | `#!python ___`  | `#!python ___`  | `#!python ___`  | `#!python ___`  |
| `#!python HourRangeDated` | `#!python HourRangeDated`  | `#!python HourRangeDated`  | `#!python ___`  | `#!python ___`  | `#!python ___`  | `#!python ___`  |
| `#!python Date`           | `#!python ___`        | `#!python ___`  | `#!python ___`  | `#!python ___`  | `#!python ___`  | `#!python ___`  |
| `#!python Time`           | `#!python ___`        | `#!python ___`  | `#!python ___`  | `#!python ___`  | `#!python ___`  | `#!python ___`  |
| `#!python DateTime`       | `#!python ___`        | `#!python ___`  | `#!python ___`  | `#!python ___`  | `#!python ___`  | `#!python ___`  |
| `#!python DateRange`      | `#!python ___`        | `#!python ___`  | `#!python ___`  | `#!python ___`  | `#!python ___`  | `#!python ___`  |

| `#!python **=`             | `#!python MinuteRange` | `#!python MinuteRangeDated` | `#!python Date` | `#!python Time` | `#!python DateTime`  | `#!python DateRange` |
| :------------------------ | :-----------------:   | :-----------------------: | :-----------------: | :-----------------: | :-----------------: | :---------------------: |
| `#!python MinuteRange`      | `#!python MinuteRange`  | `#!python ___`  | `#!python ___`  | `#!python ___`  | `#!python ___`  | `#!python ___`  |
| `#!python MinuteRangeDated` | `#!python MinuteRangeDated`  | `#!python MinuteRangeDated`  | `#!python ___`  | `#!python ___`  | `#!python ___`  | `#!python ___`  |
| `#!python Date`           | `#!python ___`        | `#!python ___`  | `#!python ___`  | `#!python ___`  | `#!python ___`  | `#!python ___`  |
| `#!python Time`           | `#!python ___`        | `#!python ___`  | `#!python ___`  | `#!python ___`  | `#!python ___`  | `#!python ___`  |
| `#!python DateTime`       | `#!python ___`        | `#!python ___`  | `#!python ___`  | `#!python ___`  | `#!python ___`  | `#!python ___`  |
| `#!python DateRange`      | `#!python ___`        | `#!python ___`  | `#!python ___`  | `#!python ___`  | `#!python ___`  | `#!python ___`  |

| `#!python **=`             | `#!python SecondRange` | `#!python SecondRangeDated` | `#!python Date` | `#!python Time` | `#!python DateTime`  | `#!python DateRange` |
| :------------------------ | :-----------------:   | :-----------------------: | :-----------------: | :-----------------: | :-----------------: | :---------------------: |
| `#!python SecondRange`      | `#!python SecondRange`  | `#!python ___`  | `#!python ___`  | `#!python ___`  | `#!python ___`  | `#!python ___`  |
| `#!python SecondRangeDated` | `#!python SecondRangeDated`  | `#!python SecondRangeDated`  | `#!python ___`  | `#!python ___`  | `#!python ___`  | `#!python ___`  |
| `#!python Date`           | `#!python ___`        | `#!python ___`  | `#!python ___`  | `#!python ___`  | `#!python ___`  | `#!python ___`  |
| `#!python Time`           | `#!python ___`        | `#!python ___`  | `#!python ___`  | `#!python ___`  | `#!python ___`  | `#!python ___`  |
| `#!python DateTime`       | `#!python ___`        | `#!python ___`  | `#!python ___`  | `#!python ___`  | `#!python ___`  | `#!python ___`  |
| `#!python DateRange`      | `#!python ___`        | `#!python ___`  | `#!python ___`  | `#!python ___`  | `#!python ___`  | `#!python ___`  |
