import os
import re

import polars as pl

fbi_violent_crime = [
    # '',
    "Aggravated Assault - Family-Strongarm",
    "Aggravated Assault - Gun",
    "Aggravated Assault - Non-family-Gun",
    "Aggravated Assault - Non-family-Strongarm",
    "Aggravated Assault - Non-family-Weapon",
    "Aggravated Assault - Weapon",
    #  'Amphetamine - Manufacturing',
    #  'Amphetamine - Possession',
    #  'Amphetamine - Sell',
    #  'Assault',
    #  'Battery',
    #  'Burglary',
    #  'Burglary - Forced Entry-Residence',
    #  'Burglary - No Forced Entry-Non-Residence',
    #  'Carrying Concealed Weapon',
    #  'Carrying Prohibited Weapon',
    #  'Cocaine',
    #  'Cocaine - Possession',
    #  'Cocaine - Sell',
    #  'Commercial Sex',
    #  'Conspiracy [use when no underlying offense, such as 18 U.S.C. SEC. 371]',
    #  'Contempt Of Court',
    #  'Contributing to Delinquency of Minor',
    #  'Counterfeiting',
    #  'Crimes Against Person',
    #  'Cruelty Toward Child',
    #  'Damage Property',
    #  'Dangerous Drugs',
    #  'Disorderly Conduct',
    #  'Domestic Violence',
    #  'Driving Under Influence Drugs',
    #  'Driving Under Influence Liquor',
    #  'Drug Possession',
    #  'Drug Trafficking',
    #  'Embezzle',
    #  'Enticement of Minor for Prostitution',
    #  'Exploitation/Enticement (Use the MIS Field to further describe offense)',
    #  'Flight - Escape',
    #  'Flight To Avoid (prosecution, confinement, etc.)',
    #  'Forgery',
    #  'Fraud',
    #  'Fraud - False Statement',
    #  'Fraud - Illegal Use Credit Cards',
    #  'Fraud - Impersonating',
    #  'Fraud By Wire',
    #  'Gambling',
    #  'Harassing Communication',
    #  'Heroin - Sell',
    #  'Heroin - Smuggle',
    #  'Hit and Run',
    "Homicide",
    #  'Homicide-Negligent Manslaughter-Vehicle',
    #  'Identity Theft',
    #  'Identity Theft (70AA)',
    #  'Illegal Entry (INA SEC.101(a)(43)(O), 8USC1325 only)',
    #  'Illegal Re-Entry (INA SEC.101(a)(43)(O), 8USC1326 only)',
    #  'Incest With Minor',
    #  'Indecent Exposure',
    #  'Intimidation',
    #  'Kidnapping',
    #  'Larceny',
    #  'Larceny - From Auto',
    #  'Licensing - Registration Weapon',
    #  'Liquor',
    #  'Liquor - Possession',
    #  'Making False Report',
    #  'Marijuana - Possession',
    #  'Marijuana - Sell',
    #  'Marijuana - Smuggle',
    #  'Narcotic Equip - Possession',
    #  'Obstruct Police',
    #  'Possession Forged (identify in comments)',
    #  'Possession Of Weapon',
    #  'Probation Violation',
    #  'Property Crimes',
    #  'Prostitution',
    #  'Public Order Crimes',
    #  'Public Peace',
    #  'Racketeer Influenced and Corrupt Organizations Act (RICO)',
    #  'Resisting Officer',
    #  'Riot - Engaging in',
    "Robbery",
    "Robbery - Residence-Gun",
    "Robbery - Residence-Weapon",
    "Sex Assault",
    "Sex Assault - Carnal Abuse",
    #  'Sex Offense',
    #  'Sex Offense Against Child-Fondling',
    #  'Sexual Exploitation of Minor - Material - Film',
    #  'Sexual Exploitation of Minor - Material - Photograph',
    #  'Sexual Exploitation of Minor - Prostitution',
    #  'Sexual Exploitation of Minor - Sex Performance',
    #  'Sexual Exploitation of Minor - Via Telecommunications',
    #  'Shoplifting',
    #  'Simple Assault',
    #  'Smuggling Aliens',
    #  'Statutory Rape - No Force',
    #  'Stolen Property',
    #  'Stolen Vehicle',
    #  'Theft And Use Vehicle Other Crime',
    #  'Threat Terroristic State Offenses',
    #  'Traffic Offense',
    #  'Trespassing',
    #  'Unauthorized Use of Vehicle (includes joy riding)',
    #  'Vehicle Theft',
    #  'Violation of a Court Order',
    #  'Voyeurism',
    #  'Weapon Offense'
]

wy_facilities = [
    "CASPER HOLDROOM",
    "CHEYENNE HOLDROOM",
    "LARAMIE COUNTY JAIL",
    "NATRONA COUNTY JAIL",
    "SWEETWATER COUNTY JAIL",
]

# TODO: where do we get this?
co_facilities = [
    "ALAMOSA HOLDROOM",
    "ARAPAHOE COUNTY JAIL",
    "AURORA CITY JAIL",
    "COLO DEPT OF CORRECTIONS",
    "COLO SPRINGS DEN HSI HOLD",
    "CRAIG HOLDROOM",
    "DENVER CONTRACT DETENTION FACILITY",
    "DENVER COUNTY JAIL",
    "DENVER HEALTH MEDICAL CENTER",
    "DENVER HOLD ROOM",
    "DOUGLAS COUNTY DETENTION CENTER",
    "DURANGO HOLDROOM",
    "GLENWOOD SPRINGS HOLDROOM",
    "GRAND JUNCTION HOLDROOM",
    "JACKSON COUNTY SHERIFF",
    "JEFFERSON COUNTY JAIL",
    "MESA COUNTY JAIL",
    "MOFFAT COUNTY JAIL",
    "OTERO COUNTY DETENTION",
    "PUEBLO COUNTY JAIL",
    "PUEBLO HOLDROOM",
    "SUMMIT COUNTY JAIL",
    "TELLER COUNTY JAIL",
    "UCHEALTH UNV HOSP OF COUINTA COUNTY JAIL",
]


def get_latest(dir, search_term):
    files = os.listdir(dir)
    matching_files = [os.path.join(dir, f) for f in files if re.search(search_term, f)]
    if not matching_files:
        return None
    latest_file = max(matching_files, key=os.path.getctime)
    print(latest_file)
    return latest_file


def detect_duplicates(
    df,
    id_col="Sequence Number/Unique Identifier",
    datetime_col="Apprehension Date And Time",
):
    df = df.sort([id_col, datetime_col]).with_columns(
        apprehension_date=pl.col(datetime_col).dt.date().alias("apprehension_date"),
        arrest_year=pl.col(datetime_col).dt.year().alias("arrest_year"),
        arrest_month=pl.col(datetime_col).dt.month().alias("arrest_month"),
        arrest_day=pl.col(datetime_col).dt.day().alias("arrest_day"),
        apprehension_date_lag=pl.col(datetime_col).shift(1).over(id_col),
        apprehension_date_diff=(
            pl.col(datetime_col) - pl.col(datetime_col).shift(1)
        ).over(id_col),
    )

    df = df.with_columns(
        duplicate_likely=pl.col("apprehension_date_diff") <= pl.duration(days=1)
    )

    return df.drop("apprehension_date_diff")


def confirm_state(
    df,
    city="Denver",
    state_full="COLORADO",
    aor_col="apprehension_aor",
    aor_state="apprehension_state",
):
    confirmed_state = df[aor_col].str.contains(city) & (df[aor_state] == state_full)
    return confirmed_state


def state_from_docket(
    df,
    city="Denver",
    state_abbrev="CO",
    aor_col="apprehension_aor",
    toa_col="toa_current_duty_site",
):
    likely_state = (
        # apprehension area of responsibility is denver and the time of apprehension docket office is in CO (not WY, which is also included in the area of responsibility)
        df[aor_col].str.contains(city)
        & df[toa_col].str.contains(r", " + state_abbrev + ",?")
    )
    print("Likely to be " + state_abbrev, likely_state.sum())
    df.filter(likely_state).write_csv(
        f"output/likely_{state_abbrev.lower()}_arrests.csv"
    )
    return likely_state


def state_from_landmark(
    df,
    city="Denver",
    state_abbrev="CO",
    state_full="COLORADO",
    aor_col="apprehension_aor",
    landmark_col="apprehension_site_landmark",
):
    likely_state = (
        # AOR is city and the site landmark ends with state
        df[aor_col].str.contains(city)
        & (
            df[landmark_col].str.ends_with(r", " + state_abbrev)
            | df[landmark_col].str.ends_with(r", " + state_full)
        )
    )
    print("Likely to be " + state_abbrev, likely_state.sum())
    df.filter(likely_state).write_csv(
        f"output/likely_{state_abbrev.lower()}_arrests.csv"
    )
    return likely_state


def get_percent(df, group_col, time_col=None):
    if time_col is None:
        df = df.with_columns(pl.lit(0).alias("dummy"))
        time_col = "dummy"
    return (
        df.group_by([time_col, group_col])
        .agg(pl.count())
        .with_columns(
            percent=(pl.col("count") / pl.col("count").sum()).over(time_col).round(3)
            * 100,
        )
        .pivot(index=group_col, columns=time_col, values=["percent"])
    )


def is_trump(df):
    return (df["arrest_year"] > 2025) | (
        (df["arrest_year"] == 2025)
        & ~((df["arrest_month"] == 1) & (df["arrest_day"] < 20))
    )
