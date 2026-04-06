# Conditional-Return-Stats
Study return statistics conditional on the level of an indicator such as VIX

```
                          time: 2026-04-05 19:58
                        script: xreturn_stats_univariate.py
                     ret_scale:                100.0
                       rf_rate:                  0.0
                        thresh:     [ 2.5  5.  10. ]
                      ret_type:               simple
                        infile:         gspc_vix.csv
                         indic:                  VIX
                  indic_thresh:                   25
          event_abs_ret_thresh:                  2.5
                       max_col:                 None
                      date_min:           1990-01-02
                      date_max:           2026-03-31
                  dropna_dates:                False
                    dropna_sym:                False
               transpose_stats:                 True
       call_print_return_stats:                 True
                  call_min_max:                 True
               allowed_symbols:                 None
                    freq_scale:                100.0

#returns, date range: 9127 1990-01-03 2026-03-31
#returns with prior VIX >= 25: 1599
#returns with prior VIX < 25 : 7528

all returns:
#sym, #obs = 2 9127
1990-01-03 to 2026-03-31
return stats:
      #obs  annmean     vol   maxDD  cumul/maxDD  Sharpe  Sharpe_adj   skew  kurtosis     min     max
GSPC  9127    9.632  18.028  73.617        4.739   0.534       0.459 -0.146    10.689 -11.984  11.580
VIX   9127   61.139 113.273 108.231       20.460   0.540       0.530  1.954    16.005 -35.754 115.598

returns conditional on prior VIX >= 25:
#sym, #obs = 2 1599
1990-01-16 to 2026-03-31
return stats:
      #obs  annmean     vol    maxDD  cumul/maxDD  Sharpe  Sharpe_adj   skew  kurtosis     min    max
GSPC  1599   23.051  32.272   54.073        2.705   0.714       0.649 -0.067     3.896 -11.984 11.580
VIX   1599 -169.076 129.196 1083.003       -0.991  -1.309      -0.419  1.235     5.749 -35.754 50.933

returns conditional on prior VIX < 25:
#sym, #obs = 2 7528
1990-01-03 to 2026-03-20
return stats:
      #obs  annmean     vol  maxDD  cumul/maxDD  Sharpe  Sharpe_adj   skew  kurtosis     min     max
GSPC  7528    6.782  13.139 63.769        3.177   0.516       0.482 -0.453     2.505  -6.866   4.765
VIX   7528  110.039 109.346 69.736       47.137   1.006       0.541  2.235    19.854 -25.909 115.598

return stats, all:
       #obs   min_index   max_index  min_value  max_value  median  mean   std   skew  kurtosis
GSPC  9127  2020-03-16  2008-10-13    -11.984     11.580   0.059 0.038 1.136 -0.146    10.689
VIX   9127  2025-04-09  2018-02-05    -35.754    115.598  -0.411 0.243 7.136  1.954    16.005

return stats, prior VIX >= 25:
       #obs   min_index   max_index  min_value  max_value  median   mean   std   skew  kurtosis
GSPC  1599  2020-03-16  2008-10-13    -11.984     11.580   0.123  0.091 2.034 -0.067     3.896
VIX   1599  2025-04-09  2025-04-04    -35.754     50.933  -1.417 -0.671 8.141  1.235     5.749

return stats, prior VIX < 25:
       #obs   min_index   max_index  min_value  max_value  median  mean   std   skew  kurtosis
GSPC  7528  1997-10-27  2000-03-16     -6.866      4.765   0.055 0.027 0.828 -0.453     2.505
VIX   7528  2006-06-15  2018-02-05    -25.909    115.598  -0.250 0.437 6.889  2.235    19.854

return counts, all:
          GSPC_count  GSPC_freq  VIX_count  VIX_freq
>= 2.5           153      1.676       2685    29.418
<= -2.5          181      1.983       3029    33.187
>= 5.0            21      0.230       1637    17.936
<= -5.0           22      0.241       1630    17.859
>= 10.0            2      0.022        610     6.683
<= -10.0           1      0.011        377     4.131

return counts, prior VIX >= 25:
          GSPC_count  GSPC_freq  VIX_count  VIX_freq
>= 2.5           132      8.255        442    27.642
<= -2.5          127      7.942        679    42.464
>= 5.0            21      1.313        285    17.824
<= -5.0           21      1.313        432    27.017
>= 10.0            2      0.125        123     7.692
<= -10.0           1      0.063        127     7.942

return counts, prior VIX < 25:
          GSPC_count  GSPC_freq  VIX_count  VIX_freq
>= 2.5            21      0.279       2243    29.795
<= -2.5           54      0.717       2350    31.217
>= 5.0             0      0.000       1352    17.960
<= -5.0            1      0.013       1198    15.914
>= 10.0            0      0.000        487     6.469
<= -10.0           0      0.000        250     3.321

c:\python\liquids\return_stats>python xreturn_stats_univariate.py
                          time: 2026-04-05 20:03
                        script: xreturn_stats_univariate.py
                     ret_scale:                100.0
                       rf_rate:                  0.0
                        thresh:     [ 2.5  5.  10. ]
                      ret_type:               simple
                        infile:         gspc_vix.csv
                         indic:                  VIX
                  indic_thresh:                   25
          event_abs_ret_thresh:                  2.5
                       max_col:                 None
                      date_min:           1990-01-02
                      date_max:           2026-03-31
                  dropna_dates:                False
                    dropna_sym:                False
               transpose_stats:                 True
       call_print_return_stats:                 True
                  call_min_max:                 True
               allowed_symbols:                 None
                    freq_scale:                100.0

#returns, date range: 9127 1990-01-03 2026-03-31
#returns with prior VIX >= 25: 1599
#returns with prior VIX < 25 : 7528

all returns:
#sym, #obs = 2 9127
1990-01-03 to 2026-03-31
return stats:
      #obs  annmean     vol   maxDD  cumul/maxDD  Sharpe  Sharpe_adj   skew  kurtosis     min     max
GSPC  9127    9.632  18.028  73.617        4.739   0.534       0.459 -0.146    10.689 -11.984  11.580
VIX   9127   61.139 113.273 108.231       20.460   0.540       0.530  1.954    16.005 -35.754 115.598

returns conditional on prior VIX >= 25:
#sym, #obs = 2 1599
1990-01-16 to 2026-03-31
return stats:
      #obs  annmean     vol    maxDD  cumul/maxDD  Sharpe  Sharpe_adj   skew  kurtosis     min    max
GSPC  1599   23.051  32.272   54.073        2.705   0.714       0.649 -0.067     3.896 -11.984 11.580
VIX   1599 -169.076 129.196 1083.003       -0.991  -1.309      -0.419  1.235     5.749 -35.754 50.933

returns conditional on prior VIX < 25:
#sym, #obs = 2 7528
1990-01-03 to 2026-03-20
return stats:
      #obs  annmean     vol  maxDD  cumul/maxDD  Sharpe  Sharpe_adj   skew  kurtosis     min     max
GSPC  7528    6.782  13.139 63.769        3.177   0.516       0.482 -0.453     2.505  -6.866   4.765
VIX   7528  110.039 109.346 69.736       47.137   1.006       0.541  2.235    19.854 -25.909 115.598

return stats, all:
       #obs   min_index   max_index  min_value  max_value  median  mean   std   skew  kurtosis
GSPC  9127  2020-03-16  2008-10-13    -11.984     11.580   0.059 0.038 1.136 -0.146    10.689
VIX   9127  2025-04-09  2018-02-05    -35.754    115.598  -0.411 0.243 7.136  1.954    16.005

return stats, prior VIX >= 25:
       #obs   min_index   max_index  min_value  max_value  median   mean   std   skew  kurtosis
GSPC  1599  2020-03-16  2008-10-13    -11.984     11.580   0.123  0.091 2.034 -0.067     3.896
VIX   1599  2025-04-09  2025-04-04    -35.754     50.933  -1.417 -0.671 8.141  1.235     5.749

return stats, prior VIX < 25:
       #obs   min_index   max_index  min_value  max_value  median  mean   std   skew  kurtosis
GSPC  7528  1997-10-27  2000-03-16     -6.866      4.765   0.055 0.027 0.828 -0.453     2.505
VIX   7528  2006-06-15  2018-02-05    -25.909    115.598  -0.250 0.437 6.889  2.235    19.854

return counts, all:
          GSPC_count  GSPC_freq  VIX_count  VIX_freq
>= 2.5           153      1.676       2685    29.418
<= -2.5          181      1.983       3029    33.187
>= 5.0            21      0.230       1637    17.936
<= -5.0           22      0.241       1630    17.859
>= 10.0            2      0.022        610     6.683
<= -10.0           1      0.011        377     4.131

return counts, prior VIX >= 25:
          GSPC_count  GSPC_freq  VIX_count  VIX_freq
>= 2.5           132      8.255        442    27.642
<= -2.5          127      7.942        679    42.464
>= 5.0            21      1.313        285    17.824
<= -5.0           21      1.313        432    27.017
>= 10.0            2      0.125        123     7.692
<= -10.0           1      0.063        127     7.942

return counts, prior VIX < 25:
          GSPC_count  GSPC_freq  VIX_count  VIX_freq
>= 2.5            21      0.279       2243    29.795
<= -2.5           54      0.717       2350    31.217
>= 5.0             0      0.000       1352    17.960
<= -5.0            1      0.013       1198    15.914
>= 10.0            0      0.000        487     6.469
<= -10.0           0      0.000        250     3.321
```
