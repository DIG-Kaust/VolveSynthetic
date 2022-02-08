#!/usr/bin/env bash

# RTM of Synthetic Volve (mdd field)
#
# M. Ravasi 10-2021
#........................................................

# madagascar directories
mada_path='/home/ravasim/Documents/Madagascar/RSF/bin'
export DATAPATH='/home/ravasim/Documents/Madagascar/RSFTMP/'
path_source='/home/ravasim/Documents/Madagascar/RSFSRC/book/mrava/mddstoch/volve_synthdata'

nt=8001

date >> log
for is in {110..180..1} 
do

echo $is 
echo $is >> log
date >> log

# full wavefield
< rmdd${is}.rsf ${mada_path}/sftransp |${mada_path}/sfremap1 o1=0 d1=0.0005 n1=7600 | ${mada_path}/sfpad n1=${nt} | ${mada_path}/sfcostaper nw2=10 | ${mada_path}/sfreverse which=1 opt=i verb=y | ${mada_path}/sftransp > datmdd_rev.rsf

# sw 
< ${path_source}/wav_ricker.rsf ${mada_path}/sfwindow n1=${nt} > wav_ricker_short.rsf
< ${path_source}/r.rsf ${mada_path}/sfwindow n2=1 f2=${is} > r${is}.rsf
< wav_ricker_short.rsf ${mada_path}/sftransp | ${mada_path}/sfawefd2d ompchunk=1 ompnth=6 verb=y fsrf=n snap=y dabc=y nb=100 vel=${path_source}/vp_sm.rsf den=${path_source}/rho.rsf sou=r${is}.rsf rec=${path_source}/q.rsf wfl=/dev/null | ${mada_path}/sfwindow j2=10 > swmdd.rsf
< swmdd.rsf ${mada_path}/sfwindow f2=60 | ${mada_path}/sfput o2=0 | ${mada_path}/sfpad n2=801 | ${mada_path}/sfreverse which=2 opt=i memsize=1000 > swmdd_.rsf

# rw
< datmdd_rev.rsf ${mada_path}/sfawefd2d ompchunk=1 ompnth=6 verb=y fsrf=n snap=y dabc=y nb=100 vel=${path_source}/vp_sm.rsf den=${path_source}/rho.rsf sou=${path_source}/r.rsf rec=${path_source}/q.rsf wfl=/dev/null | ${mada_path}/sfwindow j2=10 > rwmdd.rsf

# image
< swmdd_.rsf ${mada_path}/sfadd rwmdd.rsf mode=p | ${mada_path}/sfstack axis=2 | ${mada_path}/sfput n1=401 o1=0 d1=10 n2=551 o2=3000 d2=10 label1=z label2=x unit1=m unit2=m out=stdout > Images/imdd${is}.rsf

sfrm datmdd_rev.rsf swmdd.rsf swmdd_.rsf rwmdd.rsf

date >> log

done

