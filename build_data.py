import json
from pathlib import Path
ROOT=Path(__file__).parent
people=['Jamie','Goga','Flaujae','Emma','Dom','Johnnie','Brycen','Jacie']
champs={'Men':['JMU','North Carolina','North Carolina','Washington','Washington','Indiana','Indiana','Washington'],'Women':['Stanford','North Carolina','Purdue','Baylor','Virginia','Stanford','Vanderbilt','Colorado']}
# Entries are in physical bracket order: upper-left, lower-left, upper-right, lower-right.
men_regions=[
 [('Syracuse','Sacred Heart'),('Creighton','Omaha'),('Cornell','FDU'),('San Diego','Grand Canyon')],
 [('Vermont','North Florida'),('Stanford','Tulsa'),('Marshall','Bowling Green'),('Wake Forest','Longwood')],
 [('Missouri St.','Saint Louis'),('Washington','Cleveland St.'),('Oregon St.','CSU Bakersfield'),('NC State','Col. of Charleston')],
 [('UNCW','Liberty'),('Portland','California'),('Charlotte','Lehigh'),('Bryant','Houston Christian')]
]
men_byes=[['Georgetown','UCLA','Rutgers','Pittsburgh'],['Clemson','Kansas City','Michigan St.','Akron'],['Indiana','West Virginia','Louisville','Maryland'],['North Carolina','South Carolina','Wisconsin','SMU']]
women_regions=[
 [('North Carolina','UNC Asheville'),('Washington','Auburn'),('Stanford','Santa Clara'),('Jackson St.','Alabama'),('Duke','UNCW'),('Western Mich.','Michigan'),('West Virginia','Old Dominion'),('Bryant','Virginia')],
 [('Wake Forest','Boston U.'),('Saint Louis','Arkansas'),('Penn St.','Villanova'),('Abilene Christian','Texas Tech'),('Purdue','Southern Ill.'),('Houston','Texas'),('Tennessee','Liberty'),('Lipscomb','Ohio St.')],
 [('Vanderbilt','UT Martin'),('Wisconsin','Louisville'),('Florida St.','UCF'),('UAB','South Carolina'),('Colorado','Air Force'),('Brown','Clemson'),('Kentucky','Virginia Tech'),('Lamar University','Baylor')],
 [('Notre Dame','Milwaukee'),('Samford','Mississippi St.'),('Utah St.','Utah Valley'),('Weber St.','BYU'),('Kansas','Oral Roberts'),('Quinnipiac','UCLA'),('Xavier','Oklahoma'),('Central Conn. St.','Michigan St.')]
]
# First-round ids for women are 4 regions x 8 games; men 4 regions x 4 games, then 16 second-round games.
def create(gender):
    games=[]
    if gender=='Women':
        for region,pairs in enumerate(women_regions):
            for n,(a,b) in enumerate(pairs):
                games.append(dict(id=f'R1-{region+1}-{n+1}',round=1,region=f'Quadrant {region+1}',team1=a,team2=b,winner='',feeders=[]))
        count=8
    else:
        for region,pairs in enumerate(men_regions):
            for n,(a,b) in enumerate(pairs):
                games.append(dict(id=f'R1-{region+1}-{n+1}',round=1,region=f'Quadrant {region+1}',team1=a,team2=b,winner='',feeders=[]))
        count=8
    for r in range(2,7):
        for region in range(4 if r<=4 else (2 if r==5 else 1)):
            n_games={2:4,3:2,4:1,5:1,6:1}[r]
            for n in range(n_games):
                if r==2 and gender=='Men':
                    a=men_byes[region][n]; b=''
                    feeders=[f'R1-{region+1}-{n+1}']
                elif r==2:
                    a=b=''; feeders=[f'R1-{region+1}-{2*n+1}',f'R1-{region+1}-{2*n+2}']
                elif r<=4:
                    a=b='';feeders=[f'R{r-1}-{region+1}-{2*n+1}',f'R{r-1}-{region+1}-{2*n+2}']
                elif r==5:
                    a=b='';feeders=[f'R4-{region*2+1}-1',f'R4-{region*2+2}-1']
                else:
                    a=b='';feeders=['R5-1-1','R5-2-1']
                games.append(dict(id=f'R{r}-{region+1}-{n+1}',round=r,region=f'Quadrant {region+1}' if r<=4 else 'Final Four',team1=a,team2=b,winner='',feeders=feeders))
    picks={p:{} for p in people}
    # Champion picks are transcribed; all other rounds are editable and initially unverified.
    for p,c in zip(people,champs[gender]):picks[p]['R6-1-1']=c
    return {'gender':gender,'year':2026,'participants':people,'games':games,'picks':picks,'updated_at':None,'champions_transcribed':True}
if __name__ == '__main__':
    folder=ROOT/'data'
    folder.mkdir(exist_ok=True)
    for g in ['Men','Women']:
        path=folder/f'{g.lower()}.json'
        if path.exists():
            print(f'Skipping {path.name}: existing picks and results preserved')
            continue
        data=create(g)
        path.write_text(json.dumps(data,indent=2))
        print(f'Created {path.name} with {len(data["games"])} games')
