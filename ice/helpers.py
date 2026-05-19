import os
import re

import polars as pl
from IPython.display import display
from tqdm import tqdm

violent_call_types = [
    "ASSAULT",
    "ASSAULT/SEXUAL",
    "ARSON",
    "ROBBERY",
    "HARASSMENT/THREATS",
    "LARCENY",
    "SUICIDE",
    "POSSIBLY",
    "SEXUAL",
    "EX",
]

sick_call_types = [
    "BREATHING",
    "CHEST",
    "CONVULSIONS/SEIZURES",
    "DIABETIC",
    "FALLS",
    "HEART",
    "HEMORRHAGE",
    "INJURY",
    "MEDICAL",
    "NURSE",
    "OVERDOSE/POISONING",
    "SICK",
    "STROKE",
    "UNCONSCIOUS/FAINTING",
    "TRAUMATIC",
    "PSYCHIATRIC/MENTAL",
    "EMD",
    "EMS1",
    "EMS2",
    "EMS4",
    "RNURSE",
    "MD",
    "AB",
    "ALLERGIES",
    "ALS",
    "BLS",
    "PDEMS2",
]

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
    """
    Get the latest file in a directory that matches a search term.

    :param dir: the directory to search
    :param search_term: the text pattern to match for the file of interest (e.g. "arrests")
    """

    files = os.listdir(dir)
    matching_files = [os.path.join(dir, f) for f in files if re.search(search_term, f)]
    if not matching_files:
        return None
    latest_file = max(matching_files, key=os.path.getctime)
    print(latest_file)
    return latest_file


def read_data(
    dataset, schema_overrides=None, header_row=0, rename_map={}, drop_cols=[]
):
    """
    Read a Deportation Data Project dataset.

    :param dataset: the text pattern to match for the dataset of interest (e.g. "arrests")
    :param schema_overrides: a dictionary of column names to polars data types to override the default type inference
    """

    sheets = pl.read_excel(
        get_latest("data", dataset),
        sheet_id=0,
        read_options={"header_row": header_row},
        schema_overrides=schema_overrides,
    )

    sheets = {
        nm: dt.rename({k: v for k, v in rename_map.items() if k in dt.columns})
        for nm, dt in sheets.items()
    }
    for c in drop_cols:
        sheets = {k: v.drop(c) if c in v.columns else v for k, v in sheets.items()}

    df = pl.concat([v for _, v in sheets.items()])
    print(df.shape)
    print(sorted(list(df.schema.keys())))
    display(df.head(3))
    return df


def read_calls_data(dataset):
    """
    Read 911 calls dataset and process date/time columns.
    """
    df = pl.read_csv(get_latest("data", dataset))
    df = (
        df.select([pl.col(col).str.strip_chars() for col in df.columns])
        .with_columns(
            DATE=pl.col("DATE").str.replace_all(" ", "-"),
            CALLTYPE=pl.col("CALLTYPE")
            .str.replace(r"\d[A-Z\d]+ ", "")
            .str.replace(r"- *", " ")
            .str.replace(r"  +", " ")
            .str.replace(r"SEX ", "SEXUAL ")
            .str.replace(r"\bSSIST", "ASSIST")
            .str.replace(r"\bSSAULT", "ASSAULT")
            .str.replace(r"/SEIZE", "/SEIZURES")
            .str.replace(r"/FAINT\b", "/FAINTING")
            .str.replace(r"PSYCH/", "PSYCHIATRIC/")
            .str.replace(r"CONVULS/", "CONVULSIONS/")
            .str.replace(r"CONVULSNS/", "CONVULSIONS/")
            .str.replace(r"PROBS/", "PROBLEMS/")
            .str.strip_chars(),
        )
        .with_columns(
            DATE=pl.col("DATE").str.strptime(pl.Date, format="%b-%d-%Y"),
            TIME=pl.col("TIME").str.strptime(pl.Time, format="%H:%M"),
            call_type_short=pl.col("CALLTYPE").str.replace(r" .*", ""),
        )
    )
    print(df.shape)
    print(sorted(list(df.schema.keys())))
    display(df.head(3))
    return df


def read_historical_data(dataset, header_row, schema_overrides=None, drop_cols=[]):
    """
    Read a historical dataset with irregular formatting.

    :param dataset: the text pattern to match for the dataset of interest (e.g. "arrests")
    :param header_row: the row number (0-indexed) that contains the column names
    :param schema_overrides: a dictionary of column names to polars data types to override the default type inference
    :param drop_cols: a list of column names to drop from the dataframe
    """

    files = [f for f in os.listdir("data") if dataset in f]
    hd = pl.DataFrame()
    for f in tqdm(files):
        df = pl.read_excel(
            os.path.join("data", f),
            read_options={"header_row": header_row},
            schema_overrides=schema_overrides,
        )
        # print(df.head())

        for c in drop_cols:
            if c in df.columns:
                df = df.drop(c)
        if len(hd.columns):
            print("Selecting and reordering common columns")
            df = df.select(hd.columns)

        hd = hd.vstack(df)
    print(hd.shape)
    print(sorted(list(hd.schema.keys())))
    hd.head()


def clean_duplicates(
    df,
    id_col="Sequence Number/Unique Identifier",
    datetime_col="Apprehension Date And Time",
):
    """
    Remove likely duplicate records based on the ID column and the datetime column. If a "duplicate_likely" column is already present, use that instead of calculating it.
    """

    if not "duplicate_likely" in df.columns:
        print("Creating duplicate likely column")

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
        df = df.drop("apprehension_date_diff")

        # dummy df
        keep = df.filter(pl.col(datetime_col).is_null() & pl.col(id_col).is_null())
    else:
        # both members of a duplicate set are marked, we must choose one
        keep = (
            df.filter(df["duplicate_likely"])
            .sort([id_col, datetime_col])
            .unique(subset=[id_col], keep="last")
        )

    # ensure we are not removing too many NA ID records
    print(
        "Records with missing ID:",
        df.filter(pl.col("duplicate_likely") & pl.col(id_col).is_null()).shape[0],
    )

    df = df.filter(~df["duplicate_likely"]).vstack(keep)
    return df


def confirm_state(
    df,
    city="Denver",
    state_full="COLORADO",
    aor_col="apprehension_aor",
    aor_state="apprehension_state",
):
    """
    Get rows where we are mostly certain that they belong to a certain state because they are designated as being in both the area of responsibility and the state of apprehension.
    """
    confirmed_state = df[aor_col].str.contains(city) & (df[aor_state] == state_full)
    return confirmed_state


def state_from_docket(
    df,
    city="Denver",
    state_abbrev="CO",
    aor_col="apprehension_aor",
    toa_col="toa_current_duty_site",
):
    """
    Get rows where we are somewhat certain that they belong to a state of interest.

    Requires that the apprehension area of responsibility be as specified AND the time of apprehension docket office is in the specified state (other states may also be included in the area of responsibility)
    """
    likely_state = df[aor_col].str.contains(city) & df[toa_col].str.contains(
        r", " + state_abbrev + ",?"
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
    """
    Get rows where we are somewhat certain that they belong to a state of interest.

    Requires that the apprehension area of responsibility be as specified AND the time of apprehension landmark is in the specified state (other states may also be included in the area of responsibility)
    """

    likely_state = df[aor_col].str.contains(city) & (
        df[landmark_col].str.ends_with(r", " + state_abbrev)
        | df[landmark_col].str.ends_with(r", " + state_full)
    )
    print("Likely to be " + state_abbrev, likely_state.sum())
    df.filter(likely_state).write_csv(
        f"output/likely_{state_abbrev.lower()}_arrests.csv"
    )
    return likely_state


def get_percent(df, group_col, time_col=None):
    """
    Calculate the percentage of each group within each time period. If time_col is not provided, calculate the overall percentage of each group.
    """

    if time_col is None:
        df = df.with_columns(pl.lit(0).alias("dummy"))
        time_col = "dummy"
    return (
        df.group_by([time_col, group_col])
        .agg(pl.len())
        .with_columns(
            percent=(pl.col("len") / pl.col("len").sum()).over(time_col).round(3) * 100,
        )
        .sort(time_col)
        .pivot(index=group_col, columns=time_col, values=["percent"])
    )


def is_trump(df):
    return (df["arrest_year"] > 2025) | (
        (df["arrest_year"] == 2025)
        & ~((df["arrest_month"] == 1) & (df["arrest_day"] < 20))
    )
