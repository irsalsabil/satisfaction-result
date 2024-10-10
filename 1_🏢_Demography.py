import streamlit as st
import pandas as pd
from data_processing import finalize_data
import streamlit_authenticator as stauth
import altair as alt
import scipy.stats as stats

# Fetch the credentials and survey data
df_survey, df_creds = finalize_data()

# Process `df_creds` to extract credentials in the required format
def extract_credentials(df_creds):
    credentials = {
        "credentials": {
            "usernames": {}
        },
        "cookie": {
            "name": "growth_center",
            "key": "growth_2024",
            "expiry_days": 30
        }
    }
    for index, row in df_creds.iterrows():
        credentials['credentials']['usernames'][row['username']] = {
            'name': row['name'],  # Add the 'name' field
            'password': row['password'],  # Password should already be hashed
            'unit': row['unit']  # Store the user's unit for later filtering
        }
    return credentials

# Extract credentials from df_creds
credentials = extract_credentials(df_creds)

# Authentication Setup
authenticator = stauth.Authenticate(
    credentials['credentials'],
    credentials['cookie']['name'],
    credentials['cookie']['key'],
    credentials['cookie']['expiry_days']
)

# Display the login form
name, authentication_status, username = authenticator.login('main')

# Handle authentication status
if authentication_status:
    # Get the unit for the logged-in user from the credentials
    user_unit = credentials['credentials']['usernames'][username]['unit']
    
    # Welcome message and user's unit
    #st.sidebar.write(f"Welcome {name} from {user_unit}!")
    
    # Filter survey data based on the logged-in user's unit
    #filtered_survey = df_survey_api[df_survey_api['unit'] == user_unit]
    
    # SECTION - SURVEY DATA
    #st.title(f'Survey Data for {user_unit}')
    st.header('Survey Data', divider='rainbow')
    #st.write(filtered_survey.head())
    
    # Display survey data 
    st.dataframe(df_survey.head())

    # SECTION - PARTICIPATION RATE & RESPONDENT PROFILE
    st.header('Respondent Profile', divider='rainbow')

    # SECTION - DAILY EMOTION
    st.header('Mood Meter', divider='rainbow')

    # SECTION - SATISFACTION SCORE
    st.header('Satisfaction Score', divider='rainbow')

    # SECTION - SATISFACTION COMPARED BY DEMOGRAPHY
    satisfaction_mapping = {
        'overall_satisfaction': 'Overall Satisfaction',
        'average_kd': 'Kebutuhan Dasar',
        'average_ki': 'Kontribusi Individu',
        'average_kr': 'Kerjasama',
        'average_pr': 'Pertumbuhan',
        'average_tu': 'Tujuan',
        'average_mo': 'Model Kerja',
        'average_ke': 'Keterlekatan'
    }

    satisfaction_column = st.selectbox(
        'Select the satisfaction score to display:',
        options=list(satisfaction_mapping.keys()),
        format_func=lambda x: satisfaction_mapping.get(x, x)
    )

    # User selection for comparison column and satisfaction dimension
    comparison_column = st.selectbox(
        'Select the column to compare satisfaction score by:',
        options=['unit', 'subunit', 'division', 'department', 'layer', 'status', 'gender', 'generation', 'marital'],
        format_func=lambda x: x.capitalize()  # Capitalizes the comparison column name for display
    )

    # Display subheader
    st.subheader(f'{satisfaction_mapping[satisfaction_column]} compared by {comparison_column.capitalize()}', divider='gray')

    # Calculate the overall average for the selected satisfaction column
    overall_average = df_survey[satisfaction_column].mean().round(1)

    # Calculate the total sample size (N)
    total_n = df_survey[satisfaction_column].count()

    # Display the overall average and total N before the bar chart
    st.metric(label=f"Overall Average for {satisfaction_mapping[satisfaction_column]}", 
            value=f"{overall_average} (N= {total_n})")

    # Group by the selected column and calculate the average satisfaction score (rounded to 1 decimal)
    df_avg_satisfaction = df_survey.groupby(comparison_column)[satisfaction_column].mean().round(1).reset_index()

    # Sort DataFrame by average satisfaction score in descending order
    df_avg_satisfaction = df_avg_satisfaction.sort_values(by=satisfaction_column, ascending=False)

    # Bar chart comparing average satisfaction scores by the selected column
    chart = alt.Chart(df_avg_satisfaction).mark_bar().encode(
        x=alt.X(f'{comparison_column}:N', title=comparison_column.capitalize(), sort=None),
        y=alt.Y(f'{satisfaction_column}:Q', title=satisfaction_mapping[satisfaction_column].replace('_', ' ').capitalize()),
        tooltip=[alt.Tooltip(comparison_column, title=comparison_column.capitalize()), 
                 alt.Tooltip(satisfaction_column, title=satisfaction_column.replace('_', ' ').capitalize())],
        color=alt.value('#1f77b4')  # Set color for the bars
    ).configure_axisX(
        labelAngle=0,  # Show all x-axis labels without skipping
        labelFontSize=10  # Adjust font size for clarity
    ).configure_legend(
        disable=True  # Remove the legend
    )

    st.altair_chart(chart, use_container_width=True)

    # SECTION - SATISFACTION DIMENSION OF CERTAIN DEMOGRAPHY

    # List of satisfaction columns
    satisfaction_columns = ['overall_satisfaction', 'average_kd', 'average_ki', 'average_kr', 'average_pr', 'average_tu', 'average_mo', 'average_ke']

    # Allow the user to select multiple filter columns (unit, subunit, etc.)
    filter_columns = st.multiselect(
        'Select columns to filter by (optional):',
        options=['unit', 'subunit', 'division', 'department', 'layer', 'status', 'generation', 'gender', 'marital'],
        format_func=lambda x: x.capitalize()
    )

    # Initialize the filtered data as the original DataFrame
    filtered_data = df_survey.copy()

    # List to store selected filter values for display in the subheader
    selected_filters = []

    # Display filter options for each selected filter column
    for filter_col in filter_columns:
        selected_filter_value = st.multiselect(
            f'Select {filter_col.capitalize()} to filter the data:',
            options=filtered_data[filter_col].unique(),
            key=f'filter_{filter_col}'  # Unique key for each filter selectbox
        )
        
        # Check if any values are selected for this filter
        if selected_filter_value:
            # Filter the data to include only rows where the column value is in the selected values
            filtered_data = filtered_data[filtered_data[filter_col].isin(selected_filter_value)]
            
            # Add the selected filter values to the list for subheader display
            selected_filters.append(f"{filter_col.capitalize()}: {', '.join(selected_filter_value)}")

    # Count the number of samples in the filtered data
    sample_size = len(filtered_data)

    # Create a dynamic subheader based on the selected filters
    filter_display = ', '.join(selected_filters) if selected_filters else 'All Data'
    st.subheader(f'Satisfaction Dimension of {filter_display} (N={sample_size})', divider='gray')

    # Calculate the average satisfaction scores for each dimension and overall satisfaction
    df_avg_dimensions = filtered_data[satisfaction_columns].mean().round(1).reset_index()

    # Rename columns for clarity
    df_avg_dimensions.columns = ['dimension', 'average_score']

    # Map the dimension codes to their proper names using satisfaction_mapping
    df_avg_dimensions['dimension'] = df_avg_dimensions['dimension'].map(satisfaction_mapping)

    # Sort the data by the average satisfaction score in descending order
    df_avg_dimensions = df_avg_dimensions.sort_values(by='average_score', ascending=False)

    # Create the bar chart comparing each dimension's average score
    dimension_chart = alt.Chart(df_avg_dimensions).mark_bar().encode(
        x=alt.X('dimension:N', title='Dimension', sort=None),
        y=alt.Y('average_score:Q', title='Average Score'),
        tooltip=[alt.Tooltip('dimension', title='Dimension'), 
                alt.Tooltip('average_score', title='Average Score')],
        color=alt.value('#ff7f0e')  # Set a different color for the bars
    ).configure_axisX(
        labelAngle=0,  # Display x-axis labels clearly
        labelFontSize=9.5  # Adjust font size for clarity
    ).configure_legend(
        disable=True  # Disable the legend
    )

    # Display the bar chart
    st.altair_chart(dimension_chart, use_container_width=True)


    # SECTION - MEAN DIFFERENCE TEST

    # New expander for testing mean differences
    with st.expander("Click here to do mean difference test between groups", expanded=False):
        st.subheader("Mean Difference Analysis", divider='gray')

        # User selects a dimension or overall satisfaction for testing mean difference
        test_dimension = st.selectbox(
            "Select the satisfaction dimension to test mean difference:",
            options=['overall_satisfaction'] + list(satisfaction_columns),
            format_func=lambda x: 'Overall Satisfaction' if x == 'overall_satisfaction' else satisfaction_mapping.get(x, x)
        )

        # User selects a grouping variable (e.g., unit, gender, etc.)
        group_column = st.selectbox(
            "Select the column to group by for testing:",
            options=['unit', 'subunit', 'division', 'department', 'layer', 'status', 'generation', 'gender', 'marital'],
            format_func=lambda x: x.capitalize()
        )

        # User selects the specific groups to compare
        selected_groups = st.multiselect(
            f"Select the groups to compare from {group_column.capitalize()}:",
            options=df_survey[group_column].unique(),
            key='group_selection'
        )

        # Ensure the user selects exactly 2 groups for a t-test, or more for ANOVA
        if len(selected_groups) == 2:
            # Filter data for the selected groups
            group1_data = df_survey[df_survey[group_column] == selected_groups[0]][test_dimension]
            group2_data = df_survey[df_survey[group_column] == selected_groups[1]][test_dimension]

            # Calculate means and sample sizes
            mean_group1 = group1_data.mean()
            mean_group2 = group2_data.mean()
            n_group1 = len(group1_data)
            n_group2 = len(group2_data)

            # Perform t-test for independent samples
            t_stat, p_value = stats.ttest_ind(group1_data, group2_data, equal_var=False)  # Welch's t-test (unequal variances)

            # Display t-test result
            #st.subheader(f"{selected_groups[0]} vs {selected_groups[1]}")
            st.write(f"***{selected_groups[0]}** - **Mean:** {mean_group1:.4f}, **N:** {n_group1}*")
            st.write(f"***{selected_groups[1]}** - **Mean:** {mean_group2:.4f}, **N:** {n_group2}*")
            st.write(f"**t-statistic:** {t_stat:.4f}, **p-value:** {p_value:.4f}")

            # Interpret p-value
            if p_value < 0.05:
                st.success("There is a statistically significant difference between the two groups (p < 0.05).")
            else:
                st.info("There is no statistically significant difference between the two groups (p ≥ 0.05).")
            
        elif len(selected_groups) > 2:
            # Filter data for the selected groups
            filtered_anova_data = df_survey[df_survey[group_column].isin(selected_groups)]
            
            # Prepare data for ANOVA
            groups_data = [filtered_anova_data[filtered_anova_data[group_column] == group][test_dimension] for group in selected_groups]

            # Calculate means and sample sizes for each group
            means = [group_data.mean() for group_data in groups_data]
            ns = [len(group_data) for group_data in groups_data]

            # Perform ANOVA (one-way)
            f_stat, p_value = stats.f_oneway(*groups_data)

            # Display ANOVA result
            #st.subheader(f"Mean Difference Test: {', '.join(selected_groups)}")
            for group, mean, n in zip(selected_groups, means, ns):
                st.write(f"***{group}** - **Mean:** {mean:.4f}, **N:** {n}*")
            st.write(f"**F-statistic:** {f_stat:.4f}, **p-value:** {p_value:.4f}")

            # Interpret p-value
            if p_value < 0.05:
                st.success("There is a statistically significant difference between the groups (p < 0.05).")
            else:
                st.info("There is no statistically significant difference between the groups (p ≥ 0.05).")
            
        else:
            st.warning("Please select at least 2 groups for comparison.")

    # Logout button
    authenticator.logout('Logout', 'sidebar')

elif authentication_status == False:
    st.error("Username/password is incorrect")

elif authentication_status == None:
    st.warning("Please enter your username and password")
