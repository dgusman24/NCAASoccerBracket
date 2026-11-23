import json
import os
from datetime import datetime,timezone
from pathlib import Path
import pandas as pd
import streamlit as st

ROOT=Path(__file__).parent
DATA=ROOT/'data'; DATA.mkdir(exist_ok=True)
PDFS=ROOT/'pdfs'
# Viewer mode is the safe default for any public deployment.
# Run locally with PICKEM_MODE=editor to enable all editing features.
EDITOR_MODE = os.environ.get('PICKEM_MODE', 'viewer').strip().lower() == 'editor'
ROUND=['First round','Second round','Third round','Quarterfinals','Semifinals','Championship']
PEOPLE=['Jamie','Goga','Flaujae','Emma','Dom','Johnnie','Brycen','Jacie']
NCAA={'Men':'https://www.ncaa.com/sports/soccer-men/d1','Women':'https://www.ncaa.com/sports/soccer-women/d1'}
st.set_page_config(page_title='College Cup Pick’em 2026',page_icon='⚽',layout='wide')
# st.markdown('''<style>.stApp{background:#0c1525;color:#ffffff}[data-testid="stSidebar"]{background:#142239}.block-container{padding-top:1.5rem}h1,h2,h3{color:#f1f5f9!important}</style>''',unsafe_allow_html=True)

st.markdown("""
<style>
/* Main app background */
.stApp {
    background-color: #0c1525;
    color: #ffffff;
}

/* Sidebar background */
[data-testid="stSidebar"] {
    background-color: #142239;
}

/* All standard text and labels */
.stApp p,
.stApp label,
.stApp small,
.stApp h1,
.stApp h2,
.stApp h3,
.stApp h4,
.stApp h5,
.stApp h6 {
    color: #ffffff !important;
}

/* Metric labels: Participants, Games, Points, etc. */
[data-testid="stMetricLabel"],
[data-testid="stMetricLabel"] * {
    color: #ffffff !important;
}

/* Metric values: 8, 47, 190, etc. */
[data-testid="stMetricValue"],
[data-testid="stMetricValue"] * {
    color: #ffffff !important;
}

/* Selectbox and radio labels */
[data-testid="stWidgetLabel"],
[data-testid="stWidgetLabel"] *,
[data-testid="stRadio"] label,
[data-testid="stRadio"] label * {
    color: #ffffff !important;
}

/* Dropdown selected values should stay dark on white */
[data-baseweb="select"] [role="combobox"],
[data-baseweb="select"] [role="combobox"] * {
    color: #202020 !important;
}

/* Sidebar text */
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] span,
[data-testid="stSidebar"] label {
    color: #ffffff !important;
}

/* Main page spacing */
.block-container {
    padding-top: 1.5rem;
}
            /* NCAA homepage link button */
.stLinkButton a {
    background-color: #d8344b !important;
    color: #ffffff !important;
    border: 1px solid #d8344b !important;
    border-radius: 10px !important;
}

/* Keep button text white */
.stLinkButton a *,
.stLinkButton a p {
    color: #ffffff !important;
}

/* Hover effect */
.stLinkButton a:hover {
    background-color: #b7253b !important;
    border-color: #b7253b !important;
}
</style>
""", unsafe_allow_html=True)


def load(g):return json.loads((DATA/f'{g.lower()}.json').read_text())
def save(g,d):
    if not EDITOR_MODE:
        raise PermissionError('This deployment is read-only. Changes can only be saved in local editor mode.')
    d['updated_at']=datetime.now(timezone.utc).isoformat(timespec='seconds')
    (DATA/f'{g.lower()}.json').write_text(json.dumps(d,indent=2,ensure_ascii=False))
def points(r):return 10*2**(r-1)
def game_map(d):return {g['id']:g for g in d['games']}
def participants_for(g,lookup,cache):
    if g['id'] in cache:return cache[g['id']]
    if not g['feeders']:result=[x for x in (g['team1'],g['team2']) if x]
    else:
        result=([g['team1']] if g['team1'] else [])
        for feed in g['feeders']:
            source=lookup[feed]
            if source['winner']:result.append(source['winner'])
    cache[g['id']]=result
    return result

def all_teams(g,lookup,cache):
    if not g['feeders']:return [g['team1'],g['team2']]
    out=([g['team1']] if g['team1'] else [])
    for feeder in g['feeders']:
        for team in all_teams(lookup[feeder],lookup,cache):
            if team not in out:out.append(team)
    return out

def pick_candidates(g,lookup,picks):
    if not g['feeders']:return [g['team1'],g['team2']]
    out=[g['team1']] if g['team1'] else []
    for feeder in g['feeders']:
        team=picks.get(feeder)
        if team and team not in out:out.append(team)
    return out

def score_table(d):
    rows=[]
    for person in d['participants']:
        picks=d['picks'].get(person,{})
        correct=sum(bool(g['winner']) and picks.get(g['id'])==g['winner'] for g in d['games'])
        score=sum(points(g['round']) for g in d['games'] if g['winner'] and picks.get(g['id'])==g['winner'])
        rows.append({'Participant':person,'Points':score,'Correct':correct,'Picks entered':sum(bool(v) for v in picks.values())})
    return pd.DataFrame(rows).sort_values(['Points','Correct','Participant'],ascending=[False,False,True]).reset_index(drop=True)

def pdf_view(person,gender):
    path=PDFS/f'{person}_{gender.lower()}_bracket.pdf'
    if path.exists():
        st.download_button('📄 Download original submitted PDF',path.read_bytes(),file_name=path.name,mime='application/pdf')
    # else:st.warning('Original PDF not found')

def status(g,p):
    if not p:return 'Not entered'
    if not g['winner']:return '⏳ Awaiting result'
    return '✅ Correct' if g['winner']==p else '❌ Incorrect'

# def display_round(d,person=None):
#     picks=d['picks'].get(person,{}) if person else {}
#     rows=[]
#     for g in d['games']:
#         rows.append({'Round':ROUND[g['round']-1],'Game':g['id'],'Match':f"{g['team1'] or 'TBD'} vs {g['team2'] or 'TBD'}",'Actual winner':g['winner'] or 'Pending',**({'Prediction':picks.get(g['id'],'—'),'Status':status(g,picks.get(g['id']))} if person else {})})
#     st.dataframe(pd.DataFrame(rows),hide_index=True,use_container_width=True,height=540)


def display_round(d, person=None):
    picks = d['picks'].get(person, {}) if person else {}
    lookup = game_map(d)

    def get_matchup(g):
        teams = []

        # Include teams already assigned to the game
        if g.get('team1'):
            teams.append(g['team1'])
        if g.get('team2'):
            teams.append(g['team2'])

        # Fill remaining positions from previous-round winners
        for feeder_id in g.get('feeders', []):
            feeder = lookup.get(feeder_id)
            if feeder:
                winner = feeder.get('winner', '')
                if winner:
                    teams.append(winner)
                else:
                    teams.append('TBD')

        # Make sure every game has two slots
        while len(teams) < 2:
            teams.append('TBD')

        return f"{teams[0]} vs {teams[1]}"

    rows = []

    for g in d['games']:
        rows.append({
            'Round': ROUND[g['round'] - 1],
            'Game': g['id'],
            'Match': get_matchup(g),
            'Actual winner': g['winner'] or 'Pending',
            **({
                'Prediction': picks.get(g['id'], '—'),
                'Status': status(g, picks.get(g['id']))
            } if person else {})
        })

    st.dataframe(
        pd.DataFrame(rows),
        hide_index=True,
        use_container_width=True,
        height=540
    )


def graphic(d,person):
    picks=d['picks'].get(person,{})
    st.caption('Green = correct · Red = incorrect · Blue = pending · Gray = not yet transcribed')
    for r in range(1,7):
        with st.expander(f'{ROUND[r-1]} — {points(r)} points per correct pick',expanded=r==6):
            games=[g for g in d['games'] if g['round']==r]
            cols=st.columns(2 if len(games)>1 else 1)
            for i,g in enumerate(games):
                pick=picks.get(g['id'],'')
                color='#19bb91' if g['winner'] and pick==g['winner'] else '#f07079' if g['winner'] and pick else '#4c90e8' if pick else "#ffffff"
                cols[i%len(cols)].markdown(f'''<div style="background:#192943;color:#ffffff;border-left:5px solid {color};padding:11px;margin:6px 0;border-radius:8px"><small>{g['id']} · {g['region']}</small><br><b>{pick or 'Pick not entered'}</b><br><small>Actual: {g['winner'] or 'Pending'} · {status(g,pick)}</small></div>''',unsafe_allow_html=True)

st.sidebar.title('⚽ College Cup Pick’em')
gender=st.sidebar.radio('Tournament',['Men','Women'],horizontal=True)
d=load(gender)
pages=['Home','Leaderboard','Actual Bracket','Participant Picks']
if EDITOR_MODE:
    pages.append('Admin / Enter Results')
page=st.sidebar.radio('Navigate',pages)
st.sidebar.caption('2026 NCAA Division I Soccer · ' + ('Local editor' if EDITOR_MODE else 'Read-only leaderboard'))
if page=='Home':
    st.title('⚽ 2026 College Cup Pick’em')
    st.subheader(f'{gender}’s Tournament')
    a,b,c=st.columns(3)
    a.metric('Participants',len(d['participants']))
    b.metric('Games',len(d['games']))
    c.metric('Results entered',sum(bool(g['winner']) for g in d['games']))
    st.subheader('🏆 Standings')
    st.dataframe(score_table(d),hide_index=True,use_container_width=True)
    st.caption('Predictions and results reflect the latest published data. Some participant picks may still need transcription.')

elif page=='Leaderboard':
    st.title(f'🏆 {gender}’s Leaderboard')
    board=score_table(d)
    st.dataframe(board,hide_index=True,use_container_width=True)
    st.bar_chart(board.set_index('Participant')['Points'])
    st.caption('A pick earns points only when the corresponding actual game has a recorded winner. Missing picks earn zero until entered.')

elif page=='Actual Bracket':
    st.title(f'🌐 {gender}’s Actual Bracket')
    st.link_button('Open NCAA tournament page',NCAA[gender])
    display_round(d)
    st.caption('Results are maintained by the organizer. Future matchups are determined from completed feeder games.')

elif page=='Participant Picks':
    st.title('👥 Participant Brackets')
    person=st.selectbox('Participant',d['participants'])
    row=score_table(d).set_index('Participant').loc[person]
    a,b,c=st.columns(3)
    a.metric('Points',int(row['Points']))
    b.metric('Correct picks',int(row['Correct']))
    c.metric('Predictions entered',f"{int(row['Picks entered'])}/{len(d['games'])}")
    pdf_view(person,gender)
    tab_names=['Visual comparison'] + (['Edit predictions'] if EDITOR_MODE else []) + ['All picks table']
    tabs=st.tabs(tab_names)
    tab1= tabs[0]
    tab2= tabs[1] if EDITOR_MODE else None
    tab3= tabs[-1]
    with tab1:graphic(d,person)
    if EDITOR_MODE:
        with tab2:
            # st.info('Use the original PDF to transcribe each round. Earlier-round predictions determine which teams are available in later rounds. Saved picks are preserved when the app restarts.')
            r=st.selectbox('Round to edit',range(1,7),format_func=lambda x:ROUND[x-1])
            lookup=game_map(d); picks=d['picks'].setdefault(person,{})
            with st.form(f'edit-{gender}-{person}-{r}'):
                new={}
                for g in [g for g in d['games'] if g['round']==r]:
                    candidates=pick_candidates(g,lookup,picks)
                    existing=picks.get(g['id'],'')
                    options=['— Not entered —']+list(dict.fromkeys(candidates+([existing] if existing else [])))
                    label = f"{g['id']} · {' vs '.join(candidates) if candidates else 'TBD vs TBD'}"
                    selected=st.selectbox(label,options,index=options.index(existing) if existing else 0,key=f'pick-{gender}-{person}-{g["id"]}')
                    new[g['id']]='' if selected==options[0] else selected
                if st.form_submit_button('Save this round’s picks',type='primary'):
                    for k,v in new.items():
                        if v:picks[k]=v
                        else:picks.pop(k,None)
                    save(gender,d);st.success('Predictions saved');st.rerun()
            st.caption('For a complete, consistent bracket, enter round 1 first, then continue in order. The championship pick was transcribed from the submitted PDF.')
    with tab3:display_round(d,person)

elif page=='Admin / Enter Results' and EDITOR_MODE:
    st.title('⚙️ Admin / Enter Results')
    st.info('Local editor mode. Public deployments default to read-only.')
    st.caption('Only enter a winner after the match is officially final, including penalty shootouts where applicable.')
    lookup=game_map(d); cache={}
    r=st.selectbox('Round',range(1,7),format_func=lambda x:ROUND[x-1])
    games=[g for g in d['games'] if g['round']==r]
    with st.form(f'results-{gender}-{r}'):
        selections={}
        for g in games:
            options=participants_for(g,lookup,cache)
            if g['winner'] and g['winner'] not in options:options.append(g['winner'])
            choices=['— Pending —']+options
            current=g['winner'] if g['winner'] in choices else '— Pending —'
            selections[g['id']]=st.selectbox(f"{g['id']} · {g['region']}",choices,index=choices.index(current),key=f'result-{gender}-{g["id"]}')
        if st.form_submit_button('Save results for this round',type='primary'):
            for g in games:g['winner']='' if selections[g['id']]=='— Pending —' else selections[g['id']]
            save(gender,d);st.success('Results saved and leaderboard recalculated');st.rerun()
    st.divider()
    st.subheader('Data backup')
    st.download_button('Download current tournament JSON',json.dumps(d,indent=2),file_name=f'{gender.lower()}_backup.json',mime='application/json')
    upload=st.file_uploader('Restore a tournament backup',type=['json'])
    if upload and st.button('Restore uploaded backup'):
        try:
            restored=json.load(upload)
            if not all(k in restored for k in ('games','picks','participants')):raise ValueError('Not a valid backup')
            if restored.get('gender')!=gender:raise ValueError('Backup is for the other tournament')
            save(gender,restored);st.rerun()
        except Exception as e:st.error(str(e))
