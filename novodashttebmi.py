import streamlit as st
import pandas as pd
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
df1 = pd.read_excel("ADSL.xlsx")
df2 = pd.read_excel("ADVS.xlsx")
df3 = pd.read_excel("ADAE.xlsx")
df_bmi = df2[['USUBJID','AVISIT','PARAMCD','AVAL']]
df_bmi = df_bmi.pivot_table(index=['USUBJID','AVISIT'], columns='PARAMCD', values='AVAL',aggfunc='first')
df_bmi = df_bmi.reset_index()
df_bmi.drop(df_bmi[df_bmi.AVISIT =='Screening'].index, inplace=True)
df_bmi = df_bmi.reset_index()
df_new = pd.merge(df1,df2, on='USUBJID')
df_new = df_new[df_new['AVISIT']!='Screening']
df_new = df_new.reset_index()
df_bmi['HEIGHTBL'] = df_new['HEIGHTBL']
df_bmi['TRT'] = df_new['TRTA']
df_bmi['BMI'] = df_bmi['WEIGHT']/((df_bmi['HEIGHTBL']*0.01)**2)
df_bmi['AVISIT'].replace({'Baseline': 0, 'Week 2': 1, 'Week 4':2,
                                            'Week 6':3, 'Week 8':4, 'Week 12':5,
                                            'Week 16':6, 'Week 20':7, 'Week 24':8,
                                            'Week 26':9}, inplace=True)
df_bmi.drop(df_bmi[df_bmi.AVISIT=="End of Treatment"].index,inplace=True)
df_bmi.sort_values(by=['USUBJID','AVISIT'],inplace=True)
df_bmi=df_bmi.reset_index()
df_bmi.drop(labels=['level_0','index','WEIGHT','HEIGHTBL'], axis=1,inplace=True)
trtA = df_bmi[df_bmi['TRT']=='ARM A'].USUBJID.unique().tolist()
trtB = df_bmi[df_bmi['TRT']=='ARM B'].USUBJID.unique().tolist()
trtC = df_bmi[df_bmi['TRT']=='ARM C'].USUBJID.unique().tolist()
df_bmi.drop(labels='TRT', axis=1,inplace=True)
fin_bmi = pd.pivot_table(df_bmi,index='AVISIT',columns='USUBJID',values='BMI')
# fin_bmi.to_csv("fin_bmi.csv")
bmi_data = pd.read_csv("fin_bmi.csv",index_col=0)
df = fin_bmi
maps = {'ARM A': trtA,
           'ARM B':trtB,
        'ARM C': trtC}
# groups and trace visibilities
group = []
vis = []
visList = []
for m in maps.keys():
    for col in df.columns:
        if col in maps[m]:
            vis.append(True)
        else:
            vis.append(False)
    group.append(m)
    visList.append(vis)
    vis = []

# buttons for each group
buttons = []
for i, g in enumerate(group):
    button =  dict(label=g,
                   method = 'restyle',
                    args = ['visible',visList[i]])
    buttons.append(button)

buttons = [{'label': 'all',
                 'method': 'restyle',
                 'args': ['visible', [True, True, True, True, True, True]]}] + buttons

df_ae = df3[['USUBJID','TRTA','TRTSDT','ASTDT','ASTDY', 'AENDY','AENDT','AEDECOD','AESEV']]
df_ae = df_ae[df_ae['ASTDY']>0]
top_10 = df_ae['AEDECOD'].value_counts().index.tolist()[:10]
df_ae = df_ae[df_ae['AEDECOD'].isin(top_10)]
chart_selector = st.sidebar.selectbox("Select the type of chart", ['Dot Plot - Time to Event','Line Chart - BMI'])
if chart_selector=="Dot Plot - Time to Event":
  st.write("### Time to Adverse Event")
  fig = px.scatter(df_ae, y="USUBJID", x="ASTDY", animation_frame="TRTA",color="AEDECOD",symbol="AEDECOD",height=800,hover_name='USUBJID')
  fig.update_traces(marker_size=8)
  fig.update_layout(#title="Time to Adverse Event",
                  xaxis_title="Number of Days",
                  yaxis_title="Subject ID",
                  yaxis = dict(
                  tickmode = 'array',
                  tickvals = df_ae.USUBJID.unique().tolist(),
                  ticktext = df_ae.USUBJID.unique().tolist()),
                  legend_title="Adverse Events"
                  )
  st.plotly_chart(fig,use_container_width = True)
if chart_selector=="Line Chart - BMI":
  fig2 = px.line(bmi_data) 
  fig2.update_layout(
      updatemenus=[
          dict(
          type="dropdown",
          direction="down",
          buttons = buttons)
      ],title="Distribution of BMI across visits", legend_title="Subject ID",
      xaxis_title="Timeline",
      yaxis_title="BMI",
      xaxis = dict(
          #tickmode = 'array',
          tickvals = [0,1,2,3,4,5,6,7,8,9],
          ticktext = ['Baseline', 'Week 2', 'Week 4', 'Week 6','Week 8', 'Week 12', 'Week 16','Week 20','Week 24','Week 26']
      )
  )
  st.plotly_chart(fig2,use_container_width = True)
