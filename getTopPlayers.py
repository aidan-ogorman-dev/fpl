import heatmap as hm

def getTopValuePlayers(n=10, pos='all'):
    elements = hm.downloadFplData("elements")
    element_types = hm.downloadFplData("element_types")
    teams = hm.downloadFplData("teams")

    elements['position'] = elements.element_type.map(element_types.set_index('id').singular_name)
    elements['team'] = elements.team.map(teams.set_index('id').name)
    elements['value'] = elements.value_season.astype(float)

    if pos != 'all':
        elements = elements[elements['position'] == pos]

    # Checking for the best value players, value = total_points / now_cost
    return elements[['position','second_name','team','value']].sort_values(by='value',ascending=False).head(n)
