# Admission-chance estimate — birth cohort 2021

Children born in **2021** in Praha 3/7/8/9/10/14 enter základní škola in **September 2027**. The April 2027 zápis is the moment of truth.

## Data freshness

This report is a snapshot of the inputs as of the dates below. Two of the four feeds are legally bound and change on a predictable cadence (the OZV catchment decree is amended ~yearly; the rejstřík kapacita updates as schools register expansions). If you are reading this more than ~12 months after the generation date, re-check at minimum the catchment decree and the kapacita snapshot before trusting the per-school numbers.

- **Report generated:** 2026-05-20 (UTC)
- **Spádové obvody (catchment):** OZV č. 19/2025 hl. m. Prahy, effective **2026-01-01** (source file `vyhlaska-hmp-19-2025_via-P6.pdf`).
- **School kapacita:** MŠMT rejstřík škol snapshot **2025-10-31**.
- **Births by MČ:** ČSÚ historical series, latest year **2025**.
- **External-flow ratio:** MŠMT statistical yearbook, latest school year **2025/2026** (5-year average used).

## What pressure means

Per the školský zákon, a child has a legal right to a place at their **spádová ZŠ** (the school assigned to their street in the current OZV č. 19/2025 hl. m. Prahy).

`pressure_corrected` is the ratio of the expected entry-grade cohort (births in MČ in 2021 × catchment share × Praha-wide stay-in-own-spádová ratio of 57.8%) to the modelled entry-grade capacity (`kapacita_registered × 0.9 / 9`). `pressure_ceiling` drops the 58% multiplier — it's the worst case where every spádový child attends.

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
| ZŠ Břečťanová 2919/6 | 63.8 | 135.0 | 78.0 | 1.222 (±10 %: 1.1-1.358) | overrun — capacity exceeded by spádový pool; obvod boundaries likely to be redrawn |
| ZŠ Nad vodovodem 460/81 | 63.0 | 127.8 | 73.8 | 1.172 (±10 %: 1.054-1.302) | overrun — capacity exceeded by spádový pool; obvod boundaries likely to be redrawn |
| ZŠ U vršovického nádraží 950/1 | 49.0 | 96.4 | 55.7 | 1.137 (±10 %: 1.023-1.263) | overrun — capacity exceeded by spádový pool; obvod boundaries likely to be redrawn |
| Základní škola Eden | 65.0 | 127.8 | 73.8 | 1.135 (±10 %: 1.022-1.262) | overrun — capacity exceeded by spádový pool; obvod boundaries likely to be redrawn |
| ZŠ Olešská 2222/18 | 69.0 | 120.5 | 69.6 | 1.009 (±10 %: 0.908-1.121) | tight — spádoví fill the entry grade; non-spádoví essentially shut out |
| ZŠ Švehlova 2900/12 | 63.0 | 106.1 | 61.3 | 0.973 (±10 %: 0.875-1.081) | tight — spádoví fill the entry grade; non-spádoví essentially shut out |
| Základní škola V Olšinách | 17.5 | 26.5 | 15.3 | 0.875 (±10 %: 0.788-0.973) | balanced — non-spádový admission only if odklady free up seats |
| ZŠ Gutova 1987/39 | 72.0 | 106.1 | 61.3 | 0.851 (±10 %: 0.766-0.946) | balanced — non-spádový admission only if odklady free up seats |
| ZŠ Hostýnská 2100/2 | 75.0 | 101.3 | 58.5 | 0.78 (±10 %: 0.702-0.867) | balanced — non-spádový admission only if odklady free up seats |
| ZŠ Jakutská 1210/2 | 58.5 | 77.1 | 44.6 | 0.762 (±10 %: 0.686-0.846) | balanced — non-spádový admission only if odklady free up seats |
| ZŠ V Rybníčkách 1980/31 | 66.0 | 69.9 | 40.4 | 0.612 (±10 %: 0.551-0.68) | comfortable — non-spádoví regularly admitted |
| Základní škola Solidarita | 61.0 | 60.3 | 34.8 | 0.571 (±10 %: 0.514-0.634) | comfortable — non-spádoví regularly admitted |
| Základní škola Karla Čapka | 59.4 | 55.4 | 32.0 | 0.539 (±10 %: 0.485-0.599) | comfortable — non-spádoví regularly admitted |
| ZŠ U Roháčových kasáren 1381/19 | 62.0 | 45.8 | 26.5 | 0.427 (±10 %: 0.384-0.474) | comfortable — non-spádoví regularly admitted |

### Praha 14 — 6 spádové ZŠ

| ZŠ (street) | Cap. (entry) | Expected (ceiling) | Expected (corr.) | Pressure (corr.) | Band |
|---|---:|---:|---:|---:|---|
| ZŠ Šimanovská 16 | 59.5 | 230.0 | 132.9 | 2.233 (±10 %: 2.01-2.481) | overrun — capacity exceeded by spádový pool; obvod boundaries likely to be redrawn |
| ZŠ Chvaletická 918/3 | 86.8 | 116.9 | 67.5 | 0.778 (±10 %: 0.7-0.865) | balanced — non-spádový admission only if odklady free up seats |
| ZŠ Hloubětínská 700/24 | 50.0 | 67.1 | 38.8 | 0.775 (±10 %: 0.698-0.861) | balanced — non-spádový admission only if odklady free up seats |
| ZŠ Bratří Venclíků 1140/1 | 81.0 | 44.1 | 25.5 | 0.314 (±10 %: 0.283-0.349) | comfortable — non-spádoví regularly admitted |
| Základní škola Generála Janouška | 80.0 | 34.5 | 19.9 | 0.249 (±10 %: 0.224-0.277) | comfortable — non-spádoví regularly admitted |
| ZŠ Vybíralova 964/8 | 92.0 | 36.4 | 21.0 | 0.229 (±10 %: 0.206-0.254) | comfortable — non-spádoví regularly admitted |

### Praha 3 — 10 spádové ZŠ

| ZŠ (street) | Cap. (entry) | Expected (ceiling) | Expected (corr.) | Pressure (corr.) | Band |
|---|---:|---:|---:|---:|---|
| Základní škola a mateřská škola Jarov | 32.0 | 85.0 | 49.1 | 1.534 (±10 %: 1.381-1.705) | overrun — capacity exceeded by spádový pool; obvod boundaries likely to be redrawn |
| ZŠ náměstí Jiřího z Poděbrad 1685/7 | 62.0 | 125.5 | 72.5 | 1.169 (±10 %: 1.052-1.299) | overrun — capacity exceeded by spádový pool; obvod boundaries likely to be redrawn |
| Základní škola a mateřská škola Jaroslava Seiferta | 40.0 | 72.8 | 42.1 | 1.052 (±10 %: 0.947-1.169) | tight — spádoví fill the entry grade; non-spádoví essentially shut out |
| Základní škola Pražačka | 50.0 | 89.0 | 51.4 | 1.029 (±10 %: 0.926-1.143) | tight — spádoví fill the entry grade; non-spádoví essentially shut out |
| ZŠ Cimburkova 600/18 | 25.8 | 44.5 | 25.7 | 0.997 (±10 %: 0.897-1.107) | tight — spádoví fill the entry grade; non-spádoví essentially shut out |
| ZŠ Lupáčova 1200/1 | 73.5 | 105.2 | 60.8 | 0.827 (±10 %: 0.744-0.919) | balanced — non-spádový admission only if odklady free up seats |
| Základní škola a mateřská škola | 105.0 | 145.7 | 84.2 | 0.801 (±10 %: 0.721-0.891) | balanced — non-spádový admission only if odklady free up seats |
| Základní škola a mateřská škola | 72.5 | 97.1 | 56.1 | 0.774 (±10 %: 0.696-0.86) | balanced — non-spádový admission only if odklady free up seats |
| Základní škola Chmelnice | 70.0 | 93.1 | 53.8 | 0.768 (±10 %: 0.691-0.853) | balanced — non-spádový admission only if odklady free up seats |
| ZŠ Jeseniova 2400/96 | 91.7 | 93.1 | 53.8 | 0.586 (±10 %: 0.528-0.651) | comfortable — non-spádoví regularly admitted |

### Praha 7 — 6 spádové ZŠ

| ZŠ (street) | Cap. (entry) | Expected (ceiling) | Expected (corr.) | Pressure (corr.) | Band |
|---|---:|---:|---:|---:|---|
| Základní škola T. G. Masaryka Praha 7 | 65.0 | 174.6 | 100.9 | 1.552 (±10 %: 1.397-1.724) | overrun — capacity exceeded by spádový pool; obvod boundaries likely to be redrawn |
| Základní škola Fr. Plamínkové s rozšířenou výukou jazyků Praha 7 | 49.0 | 91.9 | 53.1 | 1.084 (±10 %: 0.975-1.204) | tight — spádoví fill the entry grade; non-spádoví essentially shut out |
| Základní škola Praha 7 | 56.0 | 87.3 | 50.4 | 0.901 (±10 %: 0.811-1.001) | tight — spádoví fill the entry grade; non-spádoví essentially shut out |
| Základní škola a Mateřská škola Praha 7 | 60.0 | 78.1 | 45.1 | 0.752 (±10 %: 0.677-0.836) | balanced — non-spádový admission only if odklady free up seats |
| Fakultní základní škola PedF UK a Mateřská škola U Studánky Praha 7 | 70.0 | 87.3 | 50.4 | 0.721 (±10 %: 0.648-0.801) | balanced — non-spádový admission only if odklady free up seats |
| Základní škola Praha 7 | 114.0 | 82.7 | 47.8 | 0.419 (±10 %: 0.377-0.466) | comfortable — non-spádoví regularly admitted |

### Praha 8 — 15 spádové ZŠ

| ZŠ (street) | Cap. (entry) | Expected (ceiling) | Expected (corr.) | Pressure (corr.) | Band |
|---|---:|---:|---:|---:|---|
| ZŠ Libčická 658/10 | 46.0 | 130.5 | 75.4 | 1.639 (±10 %: 1.475-1.821) | overrun — capacity exceeded by spádový pool; obvod boundaries likely to be redrawn |
| ZŠ Palmovka 468/8 | 50.0 | 132.8 | 76.7 | 1.534 (±10 %: 1.381-1.705) | overrun — capacity exceeded by spádový pool; obvod boundaries likely to be redrawn |
| Základní škola a mateřská škola | 45.0 | 93.2 | 53.8 | 1.196 (±10 %: 1.077-1.329) | overrun — capacity exceeded by spádový pool; obvod boundaries likely to be redrawn |
| ZŠ Na Šutce 440/28 | 55.0 | 107.2 | 61.9 | 1.126 (±10 %: 1.013-1.251) | overrun — capacity exceeded by spádový pool; obvod boundaries likely to be redrawn |
| Základní škola Bohumila Hrabala | 110.0 | 188.7 | 109.0 | 0.991 (±10 %: 0.892-1.101) | tight — spádoví fill the entry grade; non-spádoví essentially shut out |
| Základní škola a mateřská škola Na Slovance | 65.0 | 86.2 | 49.8 | 0.766 (±10 %: 0.69-0.851) | balanced — non-spádový admission only if odklady free up seats |
| ZŠ Žernosecká 1597/3 | 73.0 | 83.9 | 48.5 | 0.664 (±10 %: 0.597-0.738) | comfortable — non-spádoví regularly admitted |
| ZŠ Burešova 1130/14 | 100.0 | 79.2 | 45.8 | 0.458 (±10 %: 0.412-0.509) | comfortable — non-spádoví regularly admitted |
| ZŠ Glowackého 555/6 | 80.0 | 62.9 | 36.3 | 0.454 (±10 %: 0.409-0.505) | comfortable — non-spádoví regularly admitted |
| ZŠ Hovorčovická 1281/11 | 75.0 | 58.3 | 33.7 | 0.449 (±10 %: 0.404-0.499) | comfortable — non-spádoví regularly admitted |
| Základní škola a mateřská škola | 92.4 | 69.9 | 40.4 | 0.437 (±10 %: 0.393-0.486) | comfortable — non-spádoví regularly admitted |
| Základní škola a mateřská škola Ústavní | 75.0 | 48.9 | 28.3 | 0.377 (±10 %: 0.339-0.419) | comfortable — non-spádoví regularly admitted |
| Základní škola Mazurská | 63.0 | 39.6 | 22.9 | 0.363 (±10 %: 0.327-0.404) | comfortable — non-spádoví regularly admitted |
| Základní škola a mateřská škola Petra Strozziho | 38.0 | 23.3 | 13.5 | 0.354 (±10 %: 0.319-0.394) | comfortable — non-spádoví regularly admitted |
| Základní škola a mateřská škola | 47.5 | 23.3 | 13.5 | 0.283 (±10 %: 0.255-0.315) | comfortable — non-spádoví regularly admitted |

### Praha 9 — 6 spádové ZŠ

| ZŠ (street) | Cap. (entry) | Expected (ceiling) | Expected (corr.) | Pressure (corr.) | Band |
|---|---:|---:|---:|---:|---|
| Základní škola a Mateřská škola Na Balabence | 89.8 | 313.1 | 180.9 | 2.014 (±10 %: 1.813-2.238) | overrun — capacity exceeded by spádový pool; obvod boundaries likely to be redrawn |
| Základní škola a Mateřská škola Elektra | 34.0 | 85.1 | 49.1 | 1.445 (±10 %: 1.301-1.606) | overrun — capacity exceeded by spádový pool; obvod boundaries likely to be redrawn |
| Základní škola Litvínovská 600 | 70.0 | 146.3 | 84.5 | 1.208 (±10 %: 1.087-1.342) | overrun — capacity exceeded by spádový pool; obvod boundaries likely to be redrawn |
| Základní škola Špitálská | 72.0 | 149.7 | 86.5 | 1.201 (±10 %: 1.081-1.335) | overrun — capacity exceeded by spádový pool; obvod boundaries likely to be redrawn |
| Základní škola Litvínovská 500 | 82.0 | 91.9 | 53.1 | 0.647 (±10 %: 0.583-0.719) | comfortable — non-spádoví regularly admitted |
| Základní škola Novoborská | 115.0 | 108.9 | 62.9 | 0.547 (±10 %: 0.492-0.608) | comfortable — non-spádoví regularly admitted |

## Caveats

1. **Uniform catchment-share weighting (v1).** Street-count ratios assume every street has the same number of school-age children. False — some streets are 1 building, others 50. A v2 ZSJ-population-weighted lift would tighten the per-school numbers.
2. **56 % stay-in-spádová is Praha-wide.** Per-MČ rates likely differ (Praha 3 historically loses more children to alternative schools; Praha 14 retains nearer the average). Without per-MČ data we use the city-wide average.
3. **Inflow not modelled.** Some non-spádoví families actively seek out specific schools; this raises pressure at popular ZŠ and reduces it at less-popular ones. The current model can't estimate the net effect at the per-school level.
4. **Capacity is registered, not actual.** `kapacita_registered` is the legal ceiling; actual usable capacity may be lower if a school can't staff to the registered maximum.
5. **2021 births already happened.** No demographic uncertainty in the birth count — it's a measured ČSÚ value. The ±10 % sensitivity band is dominated by the modelling assumptions, not the births term.
