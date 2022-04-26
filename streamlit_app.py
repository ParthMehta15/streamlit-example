from collections import namedtuple
import altair as alt
import math
import pandas as pd
import streamlit as st


prob_storm = 0.5
sensitivity = 0.799
specificity = 0.559

#if harvest_now:
exp_payout_harvest_now = 12 * (6000*5 + 2000*10 + 2000*15)  #960,000

#if storm
exp_payout_no_mold = 12*(5000*5 + 1000*10)  #420,000
exp_payout_mold = 12*(5000*5 + 1000*10 + 2000*120)  #3,300,000

#if no storm
exp_payout_no_sugar = 12 * (6000*5 + 2000*10 + 2000*15)   #960,000
exp_payout_typical_sugar = 12 * (5000*5 + 1000*10 + 2500*15 + 1500*30)    #1,410,000
exp_payout_high_sugar = 12 * (4000*5 + 2500*10 + 2000*15 + 1000*30 + 500*40)  #1,500,000


#Specificity-> True negative rate (Specificity = (True Negative)/(True Negative + False Positive)) -> TN -> D No rain
#Sensitivity-> True positivetive rate (Sensitivity = (True Positive)/(True Positive + False Negative) -> TP -> D Rain

def predict(prob_storm, sensitivity, specificity, payout_harvest, payout_no_harvest_storm, payout_no_harvest_no_storm):
  p_dns = specificity * (1-prob_storm) + (1-sensitivity) * prob_storm
  p_ns_dns = specificity * (1-prob_storm) / p_dns
  path = ''
  # print('P(DNS): ',p_dns)
  # print('P(NS|DNS): ',p_ns_dns)

  p_ds = sensitivity * prob_storm + (1-specificity) * (1 - prob_storm) # (1-p_dns)
  p_s_ds = sensitivity * prob_storm / p_ds
  # print('P(DS): ',p_ds)
  # print('P(S|DS): ',p_s_ds)

  exp_ds = max(payout_harvest, payout_no_harvest_no_storm*(1-p_s_ds) + payout_no_harvest_storm * p_s_ds)
  exp_nds = max(payout_harvest, payout_no_harvest_no_storm*p_ns_dns + payout_no_harvest_storm * (1-p_ns_dns))

  expected_payout_detector = p_dns * exp_nds + p_ds * exp_ds

  final_expected_payout = max(expected_payout_detector,payout_harvest)
  if payout_harvest >= expected_payout_detector:
      path = 'HARVEST NOW'
  else:
      path = 'WAIT TO HARVEST'

  # print('Expected Value: ',expected_payout)
  return final_expected_payout, path


# with st.echo(code_location='below'):

st.header('HARVEST DECISION AND PAYOUT')

chance_of_mold = st.slider(label = "Chance of botrytis ", min_value = 0, max_value = 100, step = 1)
no_sugar = st.slider(label = "Chance of no sugar", min_value = 0, max_value = 100, step = 1)
high_sugar = 0
typical_sugar = 0
if no_sugar != 100:
    typical_sugar = st.slider(label = "Chance of typical sugar",  min_value = 0, max_value = 100 - no_sugar, step = 1)
if no_sugar+typical_sugar!=100:
    high_sugar = st.slider(label = "Chance of high sugar",  min_value = 0, max_value = 100 - no_sugar - typical_sugar , step = 1)

st.text('Chance of botrytis mold: ' +str(chance_of_mold)+'%')
st.text('Chance of no sugar: ' + str(no_sugar)+'%')
st.text('Chance of typical sugar: ' + str(typical_sugar)+'%')
st.text('Chance of high sugar: ' + str(high_sugar)+'%')

if no_sugar+typical_sugar+high_sugar ==100:

    #total of all sugar = 100
    expected_payout_wo_storm = (exp_payout_no_sugar*no_sugar + exp_payout_typical_sugar*typical_sugar + exp_payout_high_sugar*high_sugar)/100
    expected_payout_with_storm = (exp_payout_mold*chance_of_mold + exp_payout_no_mold*(100-chance_of_mold))/100

    final_expected_value, decision = predict(prob_storm, sensitivity, specificity, exp_payout_harvest_now, expected_payout_with_storm, expected_payout_wo_storm)


    st.subheader('FINAL EXPECTED PAYOUT VALUE: $'+str(final_expected_value))
    st.subheader('DECISION: '+str(decision))
else:
    st.subheader('Chances of sugar should sum to 100')
