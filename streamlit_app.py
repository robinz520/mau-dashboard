import streamlit as st
import pandas as pd
import math
from pathlib import Path
from datetime import datetime

# Set the title and favicon that appear in the Browser's tab bar.
st.set_page_config(
    page_title='RingCentral MAU Dashboard',
    page_icon=':chart_with_upwards_trend:',
)

# -----------------------------------------------------------------------------
# Declare some useful functions.

@st.cache_data
def get_mau_data():
    """Grab MAU data from a CSV file."""
    
    DATA_FILENAME = Path(__file__).parent/'mau_data.csv'
    raw_mau_df = pd.read_csv(DATA_FILENAME)
    
    # 转换日期列
    raw_mau_df['Date'] = pd.to_datetime(raw_mau_df['Date'])
    
    # 重命名列以匹配数据
    raw_mau_df = raw_mau_df.rename(columns={
        'unifiedAppName': 'App Name',
        'May 20 2024, 12:00AM - May 15 2025, 7:09PM': 'MAU'
    })
    
    return raw_mau_df

mau_df = get_mau_data()

# -----------------------------------------------------------------------------
# Draw the actual page

# Set the title that appears at the top of the page.
'''
# :chart_with_upwards_trend: RingCentral MAU Dashboard

Browse Monthly Active Users (MAU) data for RingCentral applications. This dashboard shows the growth and trends of active users over time.
'''

# Add some spacing
''
''

# 获取日期范围
min_date = mau_df['Date'].min().date()
max_date = mau_df['Date'].max().date()

# 使用日期选择器替代滑块
col1, col2 = st.columns(2)
with col1:
    from_date = st.date_input('Start date', min_date)
with col2:
    to_date = st.date_input('End date', max_date)

# 获取所有应用名称
apps = mau_df['App Name'].unique()

if not len(apps):
    st.warning("No applications found in the data")

selected_apps = st.multiselect(
    'Select applications to view',
    apps,
    ['RCAppDesktop', 'RCAppMobile', 'RCAppWeb', 'RingCentralForTeams'])  # 默认选择主要应用

''
''
''

# Filter the data
filtered_mau_df = mau_df[
    (mau_df['App Name'].isin(selected_apps))
    & (mau_df['Date'].dt.date <= to_date)
    & (from_date <= mau_df['Date'].dt.date)
]

st.header('MAU Growth Over Time', divider='gray')

''

# 使用 Altair 图表替代 line_chart
import altair as alt

chart = alt.Chart(filtered_mau_df).mark_line().encode(
    x='Date:T',
    y='MAU:Q',
    color='App Name:N'
).properties(
    width='container',
    height=400
)

st.altair_chart(chart, use_container_width=True)

''
''

first_date = mau_df[mau_df['Date'].dt.date == from_date]
last_date = mau_df[mau_df['Date'].dt.date == to_date]

st.header(f'MAU Comparison ({from_date} vs {to_date})', divider='gray')

''

cols = st.columns(4)

for i, app in enumerate(selected_apps):
    col = cols[i % len(cols)]

    with col:
        first_mau = first_date[first_date['App Name'] == app]['MAU'].iat[0]
        last_mau = last_date[last_date['App Name'] == app]['MAU'].iat[0]

        if math.isnan(first_mau):
            growth = 'n/a'
            delta_color = 'off'
        else:
            growth = f'{last_mau / first_mau:,.2f}x'
            delta_color = 'normal'

        st.metric(
            label=f'{app} MAU',
            value=f'{last_mau:,.0f}',
            delta=growth,
            delta_color=delta_color
        )
