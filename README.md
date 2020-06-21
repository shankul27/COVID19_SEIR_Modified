# COVID19_SEIR_Modified
Keeping in mind India’s containment strategy for the novel coronavirus (subsequently named SARS-CoV-2) causing the disease Covid-19, a modification to existing SEIR Model has been done for accurate prediction of R-naught.(Works for all Indian states)

File description:

- 21-06 1204 mh 03-04 Active Cases.xls
- 21-06 1204 mh 03-04 New Cases.xls
- 21-06 1204 mh 03-04 Raw File.xls
- 21-06 1204 mh 03-04 Total Cases.xls
**Output files as on 21 June for Maharashtra**

- E and I Distribution.xlsx
- E and I Template.xlsx
 **Templates to calculate Initially Exposed and Initially Infected patients from govt data given. Input for model.**

- Modified SEIR Model_v3.ipynb
- Modified SEIR Model_v3.py
**Jupyter notebook code and .py file.** 

- SEIR_v3_19 April predictions.pdf
**Prediction values as done on 19th April for next 2 weeks**

- ReadMe_SEIR_3 May.pdf
**Updated Read Me and prediction values as calculated on 3rd May for next 2 weeks**


**Modified SEIR Model**

Keeping in mind India’s containment strategy for the novel coronavirus (subsequently named SARS-CoV-2) causing the disease Covid-19, a Detected & Isolated(ID) stage has been added in the conventional SEIR Model. So, as soon as an infected patient is identified and is tested positive, he/she moves to Detected & Isolated(ID) stage. At this stage, the patient doesn’t infect anyone anymore as he/she is completely isolated. In short, ID is the govt data for active cases given out every day. To read about conventional SEIR Model, click here.
 

S: Susceptible population

E: Exposed population (exposed to the virus but not infectious yet)

I: Infectious population (asymptomatic or symptomatic patients who are infectious but not detected yet)

ID: Detected & Isolated population (detected patients who have been isolated. Even though this population is still infectious, it doesn’t infect anyone anymore as patients at this stage are completely isolated. It is the govt data for active cases)

R: Recovered or Dead population



β: rate of transmission (transmissions per S-I contact per time)

σ: rate of progression (inverse of incubation period)

γ: rate of detection for infectious individuals (inverse of disease onset to diagnosis time)

δ: rate of recovery (inverse of recovery period)

Equations:

	dS/dt=-βSI/N
	dE/dt=βSI/N-σE
	dI/dt= σE- γI
	(dI_D)/dt= γI- δI_D
	dR/dt= δI_D
	R(reproduction number)=  β/γ
	N = S + E + I + ID + R


**Read "ReadMe_SEIR_3 May.pdf" for detailed description**
