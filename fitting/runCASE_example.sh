#!/bin/bash
set -x
echo "pwd"
pwd
echo "ls"
ls

xrdcp -s root://cmseos.fnal.gov//store/user/wmccorma/CASE_COMBINE_CMSSW_10_2_13.tgz ./CMSSW_10_2_13.tgz
source /cvmfs/cms.cern.ch/cmsset_default.sh
tar -xf CMSSW_10_2_13.tgz
rm CMSSW_10_2_13.tgz
cd CASE_ALL/CMSSW_10_2_13/src/
echo "pwd where am i"
pwd
echo "ls what's here"


scramv1 b -r ProjectRename # this handles linking the already compiled code - do NOT recompile
eval `scramv1 runtime -sh` # cmsenv is an alias not on the workers

echo $CMSSW_BASE "is the CMSSW we have on the local worker node"

cd CASEUtils/fitting

rm dijetfit.py
#xrdcp -s root://cmseos.fnal.gov//store/user/wmccorma/dijetfit_1600_3200_70GeV.py ./dijetfit.py
xrdcp -s root://cmseos.fnal.gov//store/user/wmccorma/dijetfit_SLIDING_WITHLIMITS_80GeV_newSignalFracs.py ./dijetfit.py
rm Fitter.py
xrdcp -s root://cmseos.fnal.gov//store/user/wmccorma/Fitter_6paramFTest.py ./Fitter.py
rm DataCardMaker.py
xrdcp -s root://cmseos.fnal.gov//store/user/wmccorma/DataCardMaker_6paramFTest.py ./DataCardMaker.py
rm Utils.py
xrdcp -s root://cmseos.fnal.gov//store/user/wmccorma/Utils_checkBFit.py ./Utils.py

xrdcp -s root://cmseos.fnal.gov//store/user/wmccorma/QUAK_Space_SignalTester.py ./QUAK_Space_SignalTester.py

#xrdcp -s root://cmseos.fnal.gov//store/user/wmccorma/CASE_H5Files_July12.tgz ./
#tar -xf CASE_H5Files_July12.tgz
#xrdcp -s root://cmseos.fnal.gov//store/user/wmccorma/CASE_H5Files_mjjFlat_35BkgFiles_Aug9.tgz ./
#tar -xf CASE_H5Files_mjjFlat_35BkgFiles_Aug9.tgz

xrdcp -s root://cmseos.fnal.gov//store/user/wmccorma/CASE_H5Files_mjjFlat_35BkgFiles_9Bins_newSigFracs_Oct06.tgz ./
tar -xf CASE_H5Files_mjjFlat_35BkgFiles_9Bins_newSigFracs_Oct06.tgz


xrdfs root://cmseos.fnal.gov/ mkdir /store/user/wmccorma/CASE_Oct06_testAllSlices_WITHLIMITS/${1}_${2}
xrdcp -s -f ./h5s_mjjFlat_35BkgFiles_newSigFracs/${1}/*.h5 root://cmseos.fnal.gov//store/user/wmccorma/CASE_Oct06_testAllSlices_WITHLIMITS/${1}_${2}/
for m in {1800..2700..100}
do
    #python QUAK_Space_SignalTester.py -d ./h5s_mjjFlat_35BkgFiles_newSigFracs/${1} --masspoint ${m} -t ${2} -l $((${m}-800)) -u $((${m}+800))
    #python QUAK_Space_SignalTester.py -d ./h5s_mjjFlat_35BkgFiles_newSigFracs/${1} --masspoint ${m} -t ${2} -l $((${m}-1200)) -u $((${m}+800))
    #python QUAK_Space_SignalTester.py -d ./h5s_mjjFlat_35BkgFiles_newSigFracs/${1} --masspoint ${m} -t ${2} -l $((${m}-1200)) -u $((${m}+1200))
    python QUAK_Space_SignalTester.py -d ./h5s_mjjFlat_35BkgFiles_newSigFracs/${1} --masspoint ${m} -t ${2} -l $((${m}-$((800+25*(${m}-2200)/100)))) -u $((${m}+$((800+25*(${m}-2200)/100))))
    xrdcp -s -f ./h5s_mjjFlat_35BkgFiles_newSigFracs/${1}/*COMBO*.root root://cmseos.fnal.gov//store/user/wmccorma/CASE_Oct06_testAllSlices_WITHLIMITS/${1}_${2}/
    xrdcp -s -f ./h5s_mjjFlat_35BkgFiles_newSigFracs/${1}/*lim*.root root://cmseos.fnal.gov//store/user/wmccorma/CASE_Oct06_testAllSlices_WITHLIMITS/${1}_${2}/
    xrdcp -s -f ./h5s_mjjFlat_35BkgFiles_newSigFracs/${1}/signalTotals_M*.txt root://cmseos.fnal.gov//store/user/wmccorma/CASE_Oct06_testAllSlices_WITHLIMITS/${1}_${2}/
    xrdcp -s -f ./h5s_mjjFlat_35BkgFiles_newSigFracs/${1}/limitInfo*.txt root://cmseos.fnal.gov//store/user/wmccorma/CASE_Oct06_testAllSlices_WITHLIMITS/${1}_${2}/
done


echo "ls"
ls

echo "pwd"
pwd

hostname
date
