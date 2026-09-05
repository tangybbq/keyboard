#!/usr/bin/env python3
"""Shift the whole board 0.7125 mm left so the mirror axis lands on x = 135.000."""
import json
DX = -0.7125
NOW = {
 'SW_LR1':(30.075,52.466), 'SW_LA1':(45.198,60.217), 'SW_LS1':(65.445,40.136),
 'SW_LO1':(66.197,57.115), 'SW_LN1':(87.593,38.69),  'SW_LT1':(85.465,55.56),
 'SW_LI1':(107.727,61.613),'SW_LE1':(98.72,76.032),
 'SW_LSP1':(105.291,109.487),'SW_LBK1':(118.744547,121.45),
 'SW_RR1':(241.35,52.466), 'SW_RA1':(226.227,60.217), 'SW_RS1':(205.98,40.136),
 'SW_RO1':(205.227,57.115),'SW_RN1':(183.832,38.69), 'SW_RT1':(185.959,55.56),
 'SW_RI1':(163.697,61.613),'SW_RE1':(172.705,76.032),
 'SW_RSP1':(166.134,109.487),'SW_RBK1':(152.68,121.45),
 'D_LR1':(25.734,50.244),  'D_LA1':(40.857,57.996),  'D_LS1':(65.232,35.265),
 'D_LO1':(65.985,52.244),  'D_LN1':(88.204,33.852),  'D_LT1':(86.076,50.722),
 'D_LI1':(110.311,57.478), 'D_LE1':(101.304,71.897),
 'D_LSP1':(101.645,106.249),'D_LBK1':(115.099,118.212),
 'D_RR1':(245.69,50.244),  'D_RA1':(230.567,57.996), 'D_RS1':(206.192,35.265),
 'D_RO1':(205.439,52.244), 'D_RN1':(183.221,33.852), 'D_RT1':(185.349,50.722),
 'D_RI1':(161.114,57.478), 'D_RE1':(170.121,71.898),
 'D_RSP1':(169.78,106.25), 'D_RBK1':(156.326,118.212),
 'A1':(135.715,59.7251), 'RESET1':(130.0,87.0), 'J2':(310.96,130.716),
 'LED1':(286.51,116.581),'LED2':(295.51,116.581),
 'LED3':(286.51,125.581),'LED4':(295.51,125.581),
}
new = {r:(round(x+DX,4), y) for r,(x,y) in NOW.items()}
new['A1'] = (135.0, NOW['A1'][1])      # snap the MCU exactly onto the axis
# Derive every right-hand part from its left twin rather than shifting it
# independently - the rotation step left ~1 um of rounding in the pairs, and this
# is a free opportunity to make the mirror exact.
AXIS = 135.0
for r in list(new):
    p = r.split('_')
    if len(p) < 2 or not p[1].startswith('L'): continue
    tw = p[0] + '_R' + p[1][1:]
    if tw in new: new[tw] = (round(2*AXIS - new[r][0], 4), new[r][1])
AX = (new['SW_LR1'][0] + new['SW_RR1'][0]) / 2
print(f"mirror axis: {AX:.4f}   (A1 at {new['A1'][0]})")
bad=[]
for r in new:
    p=r.split('_')
    if len(p)<2 or not p[1].startswith('L'): continue
    tw = p[0]+'_R'+p[1][1:]
    if tw in new and (abs(new[r][0]+new[tw][0]-2*AX) > 1e-9
                     or abs(new[r][1]-new[tw][1]) > 1e-9): bad.append(r)
print(f"mirror pairs still exact: {not bad}", bad or "")
for r in sorted(new): print(f"{r} {new[r][0]} {new[r][1]}")
json.dump(new, open('shifted.json','w'), indent=1)
