#!/usr/bin/env bash

# RTM of Synthetic Volve
#
# M. Ravasi 10-2021
#........................................................

# madagascar directories
mada_path='/home/ravasim/Documents/Madagascar/RSF/bin'
export DATAPATH='/home/ravasim/Documents/Madagascar/RSFTMP/'
path_source='/home/ravasim/Documents/Madagascar/RSFSRC/book/mrava/mddstoch/volve_synthdata'

nt=10001

date >> log
for is in {0..120..1} 
do

echo $is 
echo $is >> log
date >> log

# full wavefield
< dat_full${is}.rsf ${mada_path}/sfwindow n2=1  | ${mada_path}/sftransp |${mada_path}/sfremap1 o1=0 d1=0.0005 n1=9400 | ${mada_path}/sfpad n1=${nt} | ${mada_path}/sfcostaper nw2=10 | ${mada_path}/sfreverse which=1 opt=i verb=y | ${mada_path}/sftransp > dat_rev.rsf

# sw 
< ${path_source}/s.rsf ${mada_path}/sfwindow n2=1 f2=${is} > s${is}.rsf
< ${path_source}/wav_ricker.rsf ${mada_path}/sftransp | ${mada_path}/sfawefd2d ompchunk=1 ompnth=6 verb=y fsrf=n snap=y dabc=y nb=100 vel=${path_source}/vp_sm.rsf den=${path_source}/rho.rsf sou=s${is}.rsf rec=${path_source}/q.rsf wfl=/dev/null | ${mada_path}/sfwindow j2=10 > sw.rsf
< sw.rsf ${mada_path}/sfwindow f2=60 | ${mada_path}/sfput o2=0 | ${mada_path}/sfpad n2=1001 | ${mada_path}/sfreverse which=2 opt=i memsize=1000 > sw_.rsf

# rw
< dat_rev.rsf ${mada_path}/sfawefd2d ompchunk=1 ompnth=6 verb=y fsrf=n snap=y dabc=y nb=100 vel=${path_source}/vp_sm.rsf den=${path_source}/rho.rsf sou=${path_source}/r.rsf rec=${path_source}/q.rsf wfl=/dev/null | ${mada_path}/sfwindow j2=10 > rw.rsf

# image
< sw_.rsf ${mada_path}/sfadd rw.rsf mode=p | ${mada_path}/sfstack axis=2 | ${mada_path}/sfput n1=401 o1=0 d1=10 n2=551 o2=3000 d2=10 label1=z label2=x unit1=m unit2=m out=stdout > Images/i${is}.rsf

sfrm dat_rev.rsf sw.rsf sw_.rsf rw.rsf

date >> log

done

