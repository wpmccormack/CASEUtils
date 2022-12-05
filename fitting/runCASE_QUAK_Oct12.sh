#!/bin/bash
#set -x

#Run with e.g.
#source runCASE_Oct12.sh sigTrainQstar2000_W400_UL17-and-Wp3000_B400_UL17-and-XYY_X3000_Y80_UL17_bkgTrainQCDBKG_mjjFlat_mjj800_ptCut300_INJECT_XYY_X3000_Y80_UL17_XS_1fb_35BkgFiles_10percConsidered_9Bins sigTemplateMakerWithInterpolation_XToYYprimeTo4Q_MY80_MYprime170

echo "pwd"
pwd
echo "ls"
ls

xrdcp -s root://cmseos.fnal.gov//store/user/wmccorma/CMSSW_10_2_13_Oct12_pullGeneral.tgz ./CMSSW_10_2_13.tgz
#xrdcp -s root://cmseos.fnal.gov//store/user/wmccorma/CMSSW_10_2_13_Oct12_originalBranch.tgz ./CMSSW_10_2_13.tgz
#xrdcp -s root://cmseos.fnal.gov//store/user/wmccorma/CMSSW_10_2_13_Oct12.tgz ./CMSSW_10_2_13.tgz
source /cvmfs/cms.cern.ch/cmsset_default.sh
tar -xf CMSSW_10_2_13.tgz
rm CMSSW_10_2_13.tgz
cd CMSSW_10_2_13/src/
echo "pwd where am i"
pwd
echo "ls what's here"


scramv1 b -r ProjectRename # this handles linking the already compiled code - do NOT recompile
eval `scramv1 runtime -sh` # cmsenv is an alias not on the workers

echo $CMSSW_BASE "is the CMSSW we have on the local worker node"

cd CASEUtils/fitting

#rm dijetfit.py
##xrdcp -s root://cmseos.fnal.gov//store/user/wmccorma/dijetfit_1600_3200_70GeV.py ./dijetfit.py
#xrdcp -s root://cmseos.fnal.gov//store/user/wmccorma/dijetfit_SLIDING_WITHLIMITS_80GeV_newSignalFracs.py ./dijetfit.py
#rm Fitter.py
#xrdcp -s root://cmseos.fnal.gov//store/user/wmccorma/Fitter_6paramFTest.py ./Fitter.py
#rm DataCardMaker.py
#xrdcp -s root://cmseos.fnal.gov//store/user/wmccorma/DataCardMaker_6paramFTest.py ./DataCardMaker.py
#rm Utils.py
#xrdcp -s root://cmseos.fnal.gov//store/user/wmccorma/Utils_checkBFit.py ./Utils.py
#
##xrdcp -s root://cmseos.fnal.gov//store/user/wmccorma/QUAK_Space_SignalTester.py ./QUAK_Space_SignalTester.py
#cp /uscms_data/d1/wmccorma/CASE_ALL/CMSSW_10_2_13/src/CASEUtils/fitting/QUAK_Space_SignalTester.py ./QUAK_Space_SignalTester.py
##xrdcp -s root://cmseos.fnal.gov//store/user/wmccorma/CASE_H5Files_July12.tgz ./
##tar -xf CASE_H5Files_July12.tgz
##xrdcp -s root://cmseos.fnal.gov//store/user/wmccorma/CASE_H5Files_mjjFlat_35BkgFiles_Aug9.tgz ./
##tar -xf CASE_H5Files_mjjFlat_35BkgFiles_Aug9.tgz

xrdcp -s root://cmseos.fnal.gov//store/user/wmccorma/CASE_H5Files_mjjFlat_35BkgFiles_9Bins_newSigFracs_Oct06.tgz ./
tar -xf CASE_H5Files_mjjFlat_35BkgFiles_9Bins_newSigFracs_Oct06.tgz


#xrdfs root://cmseos.fnal.gov/ mkdir /store/user/wmccorma/CASE_Oct05_testAllSlices_WITHLIMITS/${1}_${2}
#xrdcp -s -f ./h5s_mjjFlat_35BkgFiles_newSigFracs/${1}/*.h5 root://cmseos.fnal.gov//store/user/wmccorma/CASE_Oct05_testAllSlices_WITHLIMITS/${1}_${2}/
for m in {4800..4800..100}
do
    #python QUAK_Space_SignalTester.py -d ./h5s_mjjFlat_35BkgFiles_newSigFracs/${1} --masspoint ${m} -t ${2} -l $((${m}-800)) -u $((${m}+800))
    #python QUAK_Space_SignalTester.py -d ./h5s_mjjFlat_35BkgFiles_newSigFracs/${1} --masspoint ${m} -t ${2} -l $((${m}-1200)) -u $((${m}+800))
    python QUAK_Space_SignalTester_BYROW.py -d ./h5s_mjjFlat_35BkgFiles_newSigFracs/${1} --masspoint ${m} -t ${2} -l $((${m}-$((800+25*(${m}-2200)/100)))) -u $((${m}+$((800+25*(${m}-2200)/100))))
    #xrdcp -s -f ./h5s_mjjFlat_35BkgFiles_newSigFracs/${1}/*COMBO*.root root://cmseos.fnal.gov//store/user/wmccorma/CASE_Oct05_testAllSlices_WITHLIMITS/${1}_${2}/
    #xrdcp -s -f ./h5s_mjjFlat_35BkgFiles_newSigFracs/${1}/*lim*.root root://cmseos.fnal.gov//store/user/wmccorma/CASE_Oct05_testAllSlices_WITHLIMITS/${1}_${2}/
    #xrdcp -s -f ./h5s_mjjFlat_35BkgFiles_newSigFracs/${1}/signalTotals_M*.txt root://cmseos.fnal.gov//store/user/wmccorma/CASE_Oct05_testAllSlices_WITHLIMITS/${1}_${2}/
done


echo "ls"
ls

echo "pwd"
pwd

hostname
date
