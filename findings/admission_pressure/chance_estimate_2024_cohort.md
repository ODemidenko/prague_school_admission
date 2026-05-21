# Admission-chance estimate — birth cohort 2024

Children born in **2024** in Praha 3/7/8/9/10/14 enter základní škola in **September 2030**. The April 2030 zápis is the moment of truth.

## Data freshness

This report is a snapshot of the inputs as of the dates below. Two of the four feeds are legally bound and change on a predictable cadence (the OZV catchment decree is amended ~yearly; the rejstřík kapacita updates as schools register expansions). If you are reading this more than ~12 months after the generation date, re-check at minimum the catchment decree and the kapacita snapshot before trusting the per-school numbers.

- **Report generated:** 2026-05-20 (UTC)
- **Spádové obvody (catchment):** OZV č. 19/2025 hl. m. Prahy, effective **2026-01-01** (source file `vyhlaska-hmp-19-2025_via-P6.pdf`).
- **School kapacita:** MŠMT rejstřík škol snapshot **2025-10-31**.
- **Births by MČ:** ČSÚ historical series, latest year **2025**.
- **External-flow ratio:** MŠMT statistical yearbook, latest school year **2025/2026** (5-year average used).

## What pressure means

Per the školský zákon, a child has a legal right to a place at their **spádová ZŠ** (the school assigned to their street in the current OZV č. 19/2025 hl. m. Prahy).

`pressure_corrected` is the ratio of the expected entry-grade cohort (births in MČ in 2024 × catchment share × Praha-wide stay-in-own-spádová ratio of 57.8%) to the modelled entry-grade capacity (`kapacita_registered × 0.9 / 9`). `pressure_ceiling` drops the 58% multiplier — it's the worst case where every spádový child attends.

**Chance bands** (interpreting `pressure_corrected`):

- **< 0.7** — comfortable. Non-spádoví regularly admitted.
- **0.7–0.9** — balanced. Non-spádový admission only if odklady free seats.
- **0.9–1.1** — tight. Spádoví fill the grade; non-spádoví essentially shut out.
- **> 1.1** — overrun. Capacity exceeded by the spádový pool alone; the city tends to redraw the obvod or expand classes before April.

For a spádový child: legal admission ≈ certain unless the obvod is redrawn (which happens when pressure_corrected stays > 1 for multiple cohorts).

## Per-MČ ranking (57 schools)

### Praha 10 — 14 spádové ZŠ

| ZŠ (street) | Cap. (entry) | Expected (ceiling) | Expected (corr.) | Pressure (corr.) | Band |
|---|---:|---:|---:|---:|---|
| ZŠ Břečťanová 2919/6 | 63.8 | 112.9 | 65.2 | 1.022 (±10 %: 0.92-1.135) | tight — spádoví fill the entry grade; non-spádoví essentially shut out |
| ZŠ Nad vodovodem 460/81 | 63.0 | 106.8 | 61.7 | 0.979 (±10 %: 0.881-1.088) | tight — spádoví fill the entry grade; non-spádoví essentially shut out |
| ZŠ U vršovického nádraží 950/1 | 49.0 | 80.6 | 46.6 | 0.95 (±10 %: 0.855-1.056) | tight — spádoví fill the entry grade; non-spádoví essentially shut out |
| Základní škola Eden | 65.0 | 106.8 | 61.7 | 0.949 (±10 %: 0.854-1.055) | tight — spádoví fill the entry grade; non-spádoví essentially shut out |
| ZŠ Olešská 2222/18 | 69.0 | 100.8 | 58.2 | 0.844 (±10 %: 0.759-0.937) | balanced — non-spádový admission only if odklady free up seats |
| ZŠ Švehlova 2900/12 | 63.0 | 88.7 | 51.2 | 0.813 (±10 %: 0.732-0.903) | balanced — non-spádový admission only if odklady free up seats |
| Základní škola V Olšinách | 17.5 | 22.2 | 12.8 | 0.732 (±10 %: 0.659-0.813) | balanced — non-spádový admission only if odklady free up seats |
| ZŠ Gutova 1987/39 | 72.0 | 88.7 | 51.2 | 0.711 (±10 %: 0.64-0.79) | balanced — non-spádový admission only if odklady free up seats |
| ZŠ Hostýnská 2100/2 | 75.0 | 84.6 | 48.9 | 0.652 (±10 %: 0.587-0.724) | comfortable — non-spádoví regularly admitted |
| ZŠ Jakutská 1210/2 | 58.5 | 64.5 | 37.3 | 0.637 (±10 %: 0.573-0.708) | comfortable — non-spádoví regularly admitted |
| ZŠ V Rybníčkách 1980/31 | 66.0 | 58.4 | 33.8 | 0.512 (±10 %: 0.46-0.568) | comfortable — non-spádoví regularly admitted |
| Základní škola Solidarita | 61.0 | 50.4 | 29.1 | 0.477 (±10 %: 0.429-0.53) | comfortable — non-spádoví regularly admitted |
| Základní škola Karla Čapka | 59.4 | 46.4 | 26.8 | 0.451 (±10 %: 0.406-0.501) | comfortable — non-spádoví regularly admitted |
| ZŠ U Roháčových kasáren 1381/19 | 62.0 | 38.3 | 22.1 | 0.357 (±10 %: 0.321-0.396) | comfortable — non-spádoví regularly admitted |

### Praha 14 — 6 spádové ZŠ

| ZŠ (street) | Cap. (entry) | Expected (ceiling) | Expected (corr.) | Pressure (corr.) | Band |
|---|---:|---:|---:|---:|---|
| ZŠ Šimanovská 16 | 59.5 | 180.0 | 104.0 | 1.748 (±10 %: 1.573-1.942) | overrun — capacity exceeded by spádový pool; obvod boundaries likely to be redrawn |
| ZŠ Chvaletická 918/3 | 86.8 | 91.5 | 52.9 | 0.609 (±10 %: 0.548-0.677) | comfortable — non-spádoví regularly admitted |
| ZŠ Hloubětínská 700/24 | 50.0 | 52.5 | 30.3 | 0.607 (±10 %: 0.546-0.674) | comfortable — non-spádoví regularly admitted |
| ZŠ Bratří Venclíků 1140/1 | 81.0 | 34.5 | 19.9 | 0.246 (±10 %: 0.221-0.273) | comfortable — non-spádoví regularly admitted |
| Základní škola Generála Janouška | 80.0 | 27.0 | 15.6 | 0.195 (±10 %: 0.175-0.217) | comfortable — non-spádoví regularly admitted |
| ZŠ Vybíralova 964/8 | 92.0 | 28.5 | 16.5 | 0.179 (±10 %: 0.161-0.199) | comfortable — non-spádoví regularly admitted |

### Praha 3 — 10 spádové ZŠ

| ZŠ (street) | Cap. (entry) | Expected (ceiling) | Expected (corr.) | Pressure (corr.) | Band |
|---|---:|---:|---:|---:|---|
| Základní škola a mateřská škola Jarov | 32.0 | 73.8 | 42.6 | 1.332 (±10 %: 1.199-1.481) | overrun — capacity exceeded by spádový pool; obvod boundaries likely to be redrawn |
| ZŠ náměstí Jiřího z Poděbrad 1685/7 | 62.0 | 109.0 | 62.9 | 1.015 (±10 %: 0.914-1.128) | tight — spádoví fill the entry grade; non-spádoví essentially shut out |
| Základní škola a mateřská škola Jaroslava Seiferta | 40.0 | 63.3 | 36.5 | 0.914 (±10 %: 0.822-1.015) | tight — spádoví fill the entry grade; non-spádoví essentially shut out |
| Základní škola Pražačka | 50.0 | 77.3 | 44.7 | 0.893 (±10 %: 0.804-0.993) | balanced — non-spádový admission only if odklady free up seats |
| ZŠ Cimburkova 600/18 | 25.8 | 38.7 | 22.3 | 0.866 (±10 %: 0.779-0.962) | balanced — non-spádový admission only if odklady free up seats |
| ZŠ Lupáčova 1200/1 | 73.5 | 91.4 | 52.8 | 0.718 (±10 %: 0.646-0.798) | balanced — non-spádový admission only if odklady free up seats |
| Základní škola a mateřská škola | 105.0 | 126.5 | 73.1 | 0.696 (±10 %: 0.627-0.773) | comfortable — non-spádoví regularly admitted |
| Základní škola a mateřská škola | 72.5 | 84.4 | 48.7 | 0.672 (±10 %: 0.605-0.747) | comfortable — non-spádoví regularly admitted |
| Základní škola Chmelnice | 70.0 | 80.8 | 46.7 | 0.667 (±10 %: 0.6-0.741) | comfortable — non-spádoví regularly admitted |
| ZŠ Jeseniova 2400/96 | 91.7 | 80.8 | 46.7 | 0.509 (±10 %: 0.458-0.566) | comfortable — non-spádoví regularly admitted |

### Praha 7 — 6 spádové ZŠ

| ZŠ (street) | Cap. (entry) | Expected (ceiling) | Expected (corr.) | Pressure (corr.) | Band |
|---|---:|---:|---:|---:|---|
| Základní škola T. G. Masaryka Praha 7 | 65.0 | 136.6 | 78.9 | 1.214 (±10 %: 1.093-1.349) | overrun — capacity exceeded by spádový pool; obvod boundaries likely to be redrawn |
| Základní škola Fr. Plamínkové s rozšířenou výukou jazyků Praha 7 | 49.0 | 71.9 | 41.5 | 0.848 (±10 %: 0.763-0.942) | balanced — non-spádový admission only if odklady free up seats |
| Základní škola Praha 7 | 56.0 | 68.3 | 39.5 | 0.705 (±10 %: 0.634-0.783) | balanced — non-spádový admission only if odklady free up seats |
| Základní škola a Mateřská škola Praha 7 | 60.0 | 61.1 | 35.3 | 0.588 (±10 %: 0.53-0.654) | comfortable — non-spádoví regularly admitted |
| Fakultní základní škola PedF UK a Mateřská škola U Studánky Praha 7 | 70.0 | 68.3 | 39.5 | 0.564 (±10 %: 0.507-0.626) | comfortable — non-spádoví regularly admitted |
| Základní škola Praha 7 | 114.0 | 64.7 | 37.4 | 0.328 (±10 %: 0.295-0.364) | comfortable — non-spádoví regularly admitted |

### Praha 8 — 15 spádové ZŠ

| ZŠ (street) | Cap. (entry) | Expected (ceiling) | Expected (corr.) | Pressure (corr.) | Band |
|---|---:|---:|---:|---:|---|
| ZŠ Libčická 658/10 | 46.0 | 95.2 | 55.0 | 1.196 (±10 %: 1.076-1.328) | overrun — capacity exceeded by spádový pool; obvod boundaries likely to be redrawn |
| ZŠ Palmovka 468/8 | 50.0 | 96.9 | 56.0 | 1.12 (±10 %: 1.008-1.244) | overrun — capacity exceeded by spádový pool; obvod boundaries likely to be redrawn |
| Základní škola a mateřská škola | 45.0 | 68.0 | 39.3 | 0.873 (±10 %: 0.786-0.97) | balanced — non-spádový admission only if odklady free up seats |
| ZŠ Na Šutce 440/28 | 55.0 | 78.2 | 45.2 | 0.821 (±10 %: 0.739-0.913) | balanced — non-spádový admission only if odklady free up seats |
| Základní škola Bohumila Hrabala | 110.0 | 137.7 | 79.6 | 0.723 (±10 %: 0.651-0.804) | balanced — non-spádový admission only if odklady free up seats |
| Základní škola a mateřská škola Na Slovance | 65.0 | 62.9 | 36.3 | 0.559 (±10 %: 0.503-0.621) | comfortable — non-spádoví regularly admitted |
| ZŠ Žernosecká 1597/3 | 73.0 | 61.2 | 35.4 | 0.484 (±10 %: 0.436-0.538) | comfortable — non-spádoví regularly admitted |
| ZŠ Burešova 1130/14 | 100.0 | 57.8 | 33.4 | 0.334 (±10 %: 0.301-0.371) | comfortable — non-spádoví regularly admitted |
| ZŠ Glowackého 555/6 | 80.0 | 45.9 | 26.5 | 0.331 (±10 %: 0.298-0.368) | comfortable — non-spádoví regularly admitted |
| ZŠ Hovorčovická 1281/11 | 75.0 | 42.5 | 24.6 | 0.327 (±10 %: 0.295-0.364) | comfortable — non-spádoví regularly admitted |
| Základní škola a mateřská škola | 92.4 | 51.0 | 29.5 | 0.319 (±10 %: 0.287-0.354) | comfortable — non-spádoví regularly admitted |
| Základní škola a mateřská škola Ústavní | 75.0 | 35.7 | 20.6 | 0.275 (±10 %: 0.247-0.306) | comfortable — non-spádoví regularly admitted |
| Základní škola Mazurská | 63.0 | 28.9 | 16.7 | 0.265 (±10 %: 0.239-0.294) | comfortable — non-spádoví regularly admitted |
| Základní škola a mateřská škola Petra Strozziho | 38.0 | 17.0 | 9.8 | 0.258 (±10 %: 0.233-0.287) | comfortable — non-spádoví regularly admitted |
| Základní škola a mateřská škola | 47.5 | 17.0 | 9.8 | 0.207 (±10 %: 0.186-0.23) | comfortable — non-spádoví regularly admitted |

### Praha 9 — 6 spádové ZŠ

| ZŠ (street) | Cap. (entry) | Expected (ceiling) | Expected (corr.) | Pressure (corr.) | Band |
|---|---:|---:|---:|---:|---|
| Základní škola a Mateřská škola Na Balabence | 89.8 | 239.3 | 138.2 | 1.539 (±10 %: 1.385-1.71) | overrun — capacity exceeded by spádový pool; obvod boundaries likely to be redrawn |
| Základní škola a Mateřská škola Elektra | 34.0 | 65.0 | 37.6 | 1.105 (±10 %: 0.994-1.227) | overrun — capacity exceeded by spádový pool; obvod boundaries likely to be redrawn |
| Základní škola Litvínovská 600 | 70.0 | 111.8 | 64.6 | 0.923 (±10 %: 0.831-1.025) | tight — spádoví fill the entry grade; non-spádoví essentially shut out |
| Základní škola Špitálská | 72.0 | 114.4 | 66.1 | 0.918 (±10 %: 0.826-1.02) | tight — spádoví fill the entry grade; non-spádoví essentially shut out |
| Základní škola Litvínovská 500 | 82.0 | 70.2 | 40.6 | 0.495 (±10 %: 0.445-0.55) | comfortable — non-spádoví regularly admitted |
| Základní škola Novoborská | 115.0 | 83.2 | 48.1 | 0.418 (±10 %: 0.376-0.464) | comfortable — non-spádoví regularly admitted |

## Caveats

1. **Uniform catchment-share weighting (v1).** Street-count ratios assume every street has the same number of school-age children. False — some streets are 1 building, others 50. A v2 ZSJ-population-weighted lift would tighten the per-school numbers.
2. **56 % stay-in-spádová is Praha-wide.** Per-MČ rates likely differ (Praha 3 historically loses more children to alternative schools; Praha 14 retains nearer the average). Without per-MČ data we use the city-wide average.
3. **Inflow not modelled.** Some non-spádoví families actively seek out specific schools; this raises pressure at popular ZŠ and reduces it at less-popular ones. The current model can't estimate the net effect at the per-school level.
4. **Capacity is registered, not actual.** `kapacita_registered` is the legal ceiling; actual usable capacity may be lower if a school can't staff to the registered maximum.
5. **2024 births already happened.** No demographic uncertainty in the birth count — it's a measured ČSÚ value. The ±10 % sensitivity band is dominated by the modelling assumptions, not the births term.
