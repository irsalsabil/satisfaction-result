import streamlit as st
import pandas as pd
import numpy as np
from fetch_data import fetch_data_survey, fetch_data_creds

@st.cache_data(ttl=86400)
def finalize_data():
    df_survey = fetch_data_survey()
    df_creds = fetch_data_creds()

    # Define the mapping for Likert scale
    likert_mapping = {
        'Strongly disagree': 1,
        'Disagree': 2,
        'Neutral': 3,
        'Agree': 4,
        'Strongly Agree': 5
    }

    # Convert the Likert scale columns to numerical values
    columns_to_convert = ['KD1', 'KD2', 'KD3', 'KD0', 'KI1', 'KI2', 'KI3', 'KI4', 'KI5', 'KI0',
                        'KR1', 'KR2', 'KR3', 'KR4', 'KR5', 'KR0', 'PR1', 'PR2', 'PR0',
                        'TU1', 'TU2', 'TU0', 'MO1', 'MO2', 'MO3', 'MO4', 'MO5', 'MO6', 'MO0',
                        'KE1', 'KE2', 'KE3', 'KE0']
    df_survey[columns_to_convert] = df_survey[columns_to_convert].replace(likert_mapping)

    # Calculate the average for each dimension and round to 1 decimal place
    df_survey['average_kd'] = df_survey[['KD1', 'KD2', 'KD3', 'KD0']].mean(axis=1).round(1)
    df_survey['average_ki'] = df_survey[['KI1', 'KI2', 'KI3', 'KI4', 'KI5', 'KI0']].mean(axis=1).round(1)
    df_survey['average_kr'] = df_survey[['KR1', 'KR2', 'KR3', 'KR4', 'KR5', 'KR0']].mean(axis=1).round(1)
    df_survey['average_pr'] = df_survey[['PR1', 'PR2', 'PR0']].mean(axis=1).round(1)
    df_survey['average_tu'] = df_survey[['TU1', 'TU2', 'TU0']].mean(axis=1).round(1)
    df_survey['average_mo'] = df_survey[['MO1', 'MO2', 'MO3', 'MO4', 'MO5', 'MO6', 'MO0']].mean(axis=1).round(1)
    df_survey['average_ke'] = df_survey[['KE1', 'KE2', 'KE3', 'KE0']].mean(axis=1).round(1)

    # Calculate overall satisfaction by averaging all items directly and round to 1 decimal place
    df_survey['overall_satisfaction'] = df_survey[['KD1', 'KD2', 'KD3', 'KD0', 
                                                        'KI1', 'KI2', 'KI3', 'KI4', 'KI5', 'KI0',
                                                        'KR1', 'KR2', 'KR3', 'KR4', 'KR5', 'KR0',
                                                        'PR1', 'PR2', 'PR0',
                                                        'TU1', 'TU2', 'TU0',
                                                        'MO1', 'MO2', 'MO3', 'MO4', 'MO5', 'MO6', 'MO0',
                                                        'KE1', 'KE2', 'KE3', 'KE0']].mean(axis=1).round(1)

    # Shortened unit names
    unit_map = {
        'GROUP OF MANUFACTURE': 'GOMAN',
        'GROUP OF RETAIL & PUBLISHING': 'GORP',
        'CORPORATE HUMAN RESOURCES': 'CHR',
        'GROUP OF HOTELS & RESORTS': 'GOHR',
        'GROUP OF MEDIA': 'GOMED',
        'KG PROPERTY': 'KG PRO',
        'CORPORATE COMMUNICATION': 'CORCOMM',
        'CORPORATE COMPTROLLER': 'CORCOMP',
        'GROUP OF DYANDRA MEDIA INTERNATIONAL': 'DYANDRA',
        'CORPORATE IT & IS': 'CITIS',
        'CORPORATE FINANCE & LEGAL': 'CFL',
        'YAYASAN MULTIMEDIA NUSANTARA': 'UMN',
        'CORPORATE SECRETARY': 'CORSEC',
        'REKATA': 'REKATA',
        'KOMPAS GRAMEDIA': 'KG'
    }

    df_survey['unit'] = df_survey['unit'].map(unit_map)

    return df_survey, df_creds

