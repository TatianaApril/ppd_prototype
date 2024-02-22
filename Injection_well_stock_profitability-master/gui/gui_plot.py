import pandas as pd
import numpy as np
import plotly.graph_objects as go

from plotly.graph_objects import Figure
from constants import path



# def get_graph(
#     self,
#     well: str,
#     last_prod: datetime,
#     df: pd.DataFrame):
#     colors = ['aquamarine', 'lightpink', 'chartreuse', 'cornflowerblue', 'mediumpurple', 'aqua', 'plum']
#     well_df = df.loc[df["wells"]==well].drop(columns=['wells'])
#     well_df = well_df.loc[:, (well_df != 0).any(axis=0)]
#
#     indexes_of_df = well_df["Ячейка"]+ well_df["Параметр"]
#     well_df.index = ['base liq', 'base oil'] + indexes_of_df.tolist()[2:-2] + ['sum dellta liq', 'sum delta oil']
#     new_columns = well_df.columns[2:] < last_prod
#     well_df = well_df.loc[:, np.insert(new_columns, 0, [True, True])]
#     indexes = well_df.index.tolist()[1::2]
#     oil_df = well_df.loc[well_df.index.isin(indexes)]
#     liq_df = well_df.loc[~well_df.index.isin(indexes)]
#     delta_oil = oil_df.iloc[1:-1,:]
#     delta_liq = liq_df.iloc[1:-1,:]
#
#     ppd_oil = []
#     for ind in delta_oil.index:
#         value = delta_oil.iloc[:, 2:].loc[ind, delta_oil.iloc[:, 2:].loc[ind, :] > 0]
#         if len(value) == 0:
#             delta_oil = delta_oil.drop(ind)
#         else:
#             value = value.index[0]
#             ppd_oil += [value]
#     delta_oil.insert(1, 'PPD', ppd_oil)
#     delta_oil = delta_oil.sort_values(by=['PPD']).drop(columns=['PPD'])
#     if delta_oil.empty:
#         filler = pd.Series(["нет эффекта", "нет эффекта"] + [0 for column in delta_oil.columns[2:]], index=delta_oil.columns)
#         delta_oil = pd.concat([delta_oil, filler.to_frame().T], sort=False)
#     else:
#         delta_oil.iloc[0, :] = delta_oil.iloc[0, :].add(oil_df.loc['base oil'])
#     delta_oil = delta_oil.cumsum().drop(columns=['Ячейка', 'Параметр'])
#
#     ppd_liq = []
#     for ind in delta_liq.index:
#         value = delta_liq.iloc[:, 2:].loc[ind, delta_liq.iloc[:, 2:].loc[ind, :] > 0]
#         if len(value) == 0:
#             delta_liq = delta_liq.drop(ind)
#         else:
#             value = value.index[0]
#             ppd_liq += [value]
#     delta_liq.insert(1, 'PPD', ppd_liq)
#     delta_liq = delta_liq.sort_values(by=['PPD']).drop(columns=['PPD'])
#     if delta_liq.empty:
#         filler = pd.Series(["нет эффекта", "нет эффекта"] + [0 for column in delta_liq.columns[2:]], index=delta_liq.columns)
#         delta_liq = pd.concat([delta_liq, filler.to_frame().T])
#     else:
#         delta_liq.iloc[0, :] = delta_liq.iloc[0, :].add(liq_df.loc['base liq'])
#     delta_liq = delta_liq.cumsum().drop(columns=['Ячейка', 'Параметр'])
#
#     #fig_field = Figure()
#     fig_field = make_subplots(rows=1, cols=2)
#     dates = list(oil_df.columns)[2:]
#     indexes_oil = list(delta_oil.index)
#     indexes_oil.reverse()
#     indexes_liq = list(delta_liq.index)
#     indexes_liq.reverse()
#     for ind in indexes_oil:
#         fig_field.add_trace(go.Scatter(x=dates, y=delta_oil.loc[ind].squeeze(),
#                                        name=ind,
#                                        fill='tozeroy', fillcolor=colors[list(delta_oil.index).index(ind)],
#                                        hoveron='points+fills',
#                                        marker=dict(color=colors[list(delta_oil.index).index(ind)],
#                                                    #size=5,
#                                                    ),
#                                        opacity=0.5, ), row=1, col=1)
#     for ind in indexes_liq:
#         fig_field.add_trace(go.Scatter(x=dates, y=delta_liq.loc[ind].squeeze(),
#                                        name=ind,
#                                        fill='tozeroy', fillcolor=colors[list(delta_liq.index).index(ind)],
#                                        hoveron='points+fills',
#                                        marker=dict(color=colors[list(delta_liq.index).index(ind)],
#                                                    # size=5,
#                                                    ),
#                                        opacity=0.5, ), row=1, col=2)
#
#     fig_field.add_trace(go.Scatter(x=dates, y=oil_df.loc['base oil'].squeeze()[2:],
#                                    name='Дебит нефти База',
#                                    fill='tozeroy', fillcolor='dodgerblue',
#                                    hoveron='points+fills',
#                                    opacity=0.3, ), row=1, col=1)
#     fig_field.add_trace(go.Scatter(x=dates, y=liq_df.loc['base liq'].squeeze()[2:],
#                                    name='Дебит жидкости База',
#                                    fill='tozeroy', fillcolor='dodgerblue',
#                                    hoveron='points+fills',
#                                    opacity=0.3, ), row=1, col=2)
#     fig_field.update_layout(title_text='<b>Дебит нефти и Дебит жидкости для скважины ' + well + '</b>',
#                             title_x=0.5, autosize=False, width=1400, height=700)
#     fig_field.update_layout(
#         xaxis_title="Дата",
#         yaxis_title="Дебит, т/сут",
#         template="plotly_white",
#         margin=dict(r=10, t=35, b=10, l=10),
#         #showlegend=False
#     )
#     fig_field.update_xaxes(zeroline=True, zerolinewidth=4, zerolinecolor='slategray',
#                            showgrid=True, gridwidth=1, gridcolor='slategray')
#     fig_field.update_yaxes(zeroline=True, zerolinewidth=4, zerolinecolor='slategray',
#                            showgrid=True, gridwidth=1, gridcolor='slategray')
#     fig_field.show()


def get_loqs(field):
    coord_dir = path + "\\input" + '\\' + field
    output_dir = path + "\\output" + '\\new'

    coord = pd.read_excel(coord_dir + "\\Координаты.xlsx").loc[:, ['№ скважины', 'Координата X', 'Координата Y']]
    cells = pd.read_excel(output_dir + "\\new" + field + ".xlsx").loc[:, ['Unnamed: 0', 'Ячейка']]
    coord = coord.astype({'№ скважины': 'str'})
    cells = cells.astype({'Unnamed: 0': 'str', 'Ячейка': 'str'})

    wells = coord['№ скважины'].values.tolist()
    inj_wells = cells['Ячейка'].unique().tolist()
    inj_wells.pop(0)
    flag = ['red' if well in inj_wells else 'seagreen' for well in wells]
    flag = pd.DataFrame(data=flag, index=wells, columns=['type'])

    coord = coord.set_index(['№ скважины'], drop=False)
    data = pd.concat([coord, flag], axis=1)

    cells = cells.loc[cells['Ячейка'] != '0']
    cells_dict = {}
    for inj in inj_wells:
        wells_in_cell = cells.loc[cells['Ячейка'] == inj]['Unnamed: 0'].unique().tolist()
        wells_in_cell.append(inj)
        cells_dict[inj] = [data.loc[data['№ скважины'].isin(wells_in_cell)]['Координата X'].tolist(),
                           data.loc[data['№ скважины'].isin(wells_in_cell)]['Координата Y'].tolist()]
    return data, cells_dict


def draw_things(field):
    data, cells = get_loqs(field)
    colors = ['aquamarine', 'lightpink', 'chartreuse', 'cornflowerblue', 'mediumpurple', 'aqua', 'plum', 'darkviolet',
              'red', 'blue', 'olivedrab', 'gold', 'blueviolet', 'maroon', 'orange', 'orangered', 'orchid', 'forestgreen',
              'lime', 'mediumseagreen', 'midnightblue', 'crimson', 'yellow']

    fig_field = Figure()
    fig_field.add_trace(go.Scatter(x=data['Координата X'], y=data['Координата Y'],
                                   mode='markers+text',
                                   textposition='top right',
                                   marker=dict(color=data['type'],
                                               size=10,),
                                   text=data['№ скважины'],))

    for cell in cells.keys():
        ind = np.random.randint(low=0, high=18, size=(1,))[0]
        fig_field.add_trace(go.Scatter(x=cells[cell][0], y=cells[cell][1],
                                 fill='toself', fillcolor=colors[ind],
                                 hoveron='points+fills',
                                 line_color='darkviolet',
                                 opacity= 0.3,))

    fig_field.update_layout(title_text='Карта Тайлаковское м',
            title_x=0.5, autosize=False, width=1000, height=650)
    fig_field.update_layout(
        xaxis_title="X coord",
        yaxis_title="Y coord",
        template="plotly_white",
        margin=dict(r=10, t=35, b=10, l=10),
        showlegend=False
    )
    fig_field.update_xaxes(zeroline=True, zerolinewidth=4, zerolinecolor='slategray',
            showgrid=True, gridwidth=1, gridcolor='slategray')
    fig_field.update_yaxes(zeroline=True, zerolinewidth=4, zerolinecolor='slategray',
            showgrid=True, gridwidth=1, gridcolor='slategray')
    fig_field.show()


field = 'Тайлаковское'
draw_things(field)
