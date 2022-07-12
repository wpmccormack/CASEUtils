import os
import optparse
import shutil

def fitting_options():
    parser = optparse.OptionParser()
    parser.add_option("-l", "--h5Loc", dest="h5Loc", default="/uscms_data/d1/wmccorma/CASE_ALL/CMSSW_12_4_0_pre2/src/h5Dir", help="top dir where you make h5 files, default is /uscms_data/d1/wmccorma/CASE_ALL/CMSSW_12_4_0_pre2/src/h5Dir/")
    parser.add_option("-d", "--dirName", dest="dirName", default="DUMMYDIR", help="dir name with h5 files? (e.g. sigTrainXYY_X3000_Y80_UL17_bkgTrainQCDBKG_INJECT_XYY_X3000_Y80_UL17_XS_100fb_15BkgFiles_10percConsidered_5Bins)")
    parser.add_option("-t", "--sigTemplate", dest="sigTemplate", default="DUMMYDIR", help="sigTemplateWithInterpolation (choose one of the sigTemplateMakerWithInterpolation directories, e.g. sigTemplateMakerWithInterpolation_WpToBpT_Bp400_Top170)")
    parser.add_option("--minMscan", dest="minMscan", type=int, default=-1, help="starting mass for scan")
    parser.add_option("--maxMscan", dest="maxMscan", type=int, default=-1, help="ending mass for scan")
    parser.add_option("-g", "--massgaps", dest="massgaps", type=int, default=-1, help="step size between masses")
    return parser

if __name__ == "__main__":
    parser = fitting_options()
    (options, args) = parser.parse_args()

    

    h5Loc = options.h5Loc
    if(not os.path.isdir(h5Loc)):
        print("h5 top directory does not exist!")
        h5Loc = str(raw_input('top dir where you make h5 files, default is /uscms_data/d1/wmccorma/CASE_ALL/CMSSW_12_4_0_pre2/src/h5Dir : ') or "/uscms_data/d1/wmccorma/CASE_ALL/CMSSW_12_4_0_pre2/src/h5Dir/")
        if(not os.path.isdir(h5Loc)):
            print("h5 directory still does not exist!")
            exit()
    print("using "+h5Loc)

    dirName = options.dirName
    print(dirName)
    if(dirName == "DUMMYDIR"):
        dirName = str(raw_input('dir name with h5 files? (e.g. sigTrainXYY_X3000_Y80_UL17_bkgTrainQCDBKG_INJECT_XYY_X3000_Y80_UL17_XS_100fb_15BkgFiles_10percConsidered_5Bins) : ') or "DUMMYDIR")
    print(dirName)
    stTries = 0
    while(not os.path.isdir(h5Loc+'/'+dirName) and stTries < 5):
        print("that dir not available.  Please choose from: ")
        print(os.listdir(h5Loc))
        dirName = str(raw_input('dir name with h5 files? (e.g. sigTrainXYY_X3000_Y80_UL17_bkgTrainQCDBKG_INJECT_XYY_X3000_Y80_UL17_XS_100fb_15BkgFiles_10percConsidered_5Bins) : ') or "DUMMYDIR")
        stTries += 1
    if(not os.path.isdir(h5Loc+'/'+dirName)):
        print("you had five tries to get it right...")
        exit()

    fullPathToH5s = h5Loc+'/'+dirName+"/"

    sigTemplate = options.sigTemplate
    if(sigTemplate == "DUMMYDIR"):
        sigTemplate = str(raw_input('sigTemplateWithInterpolation (choose one of the sigTemplateMakerWithInterpolation directories, e.g. sigTemplateMakerWithInterpolation_WpToBpT_Bp400_Top170) : ') or "DUMMYDIR")
    stTries = 0
    while(not os.path.isdir('./'+sigTemplate) and stTries < 5):
        print("that dir not available.  Please choose from: ")
        print(os.listdir(h5Loc))
        sigTemplate = str(raw_input('sigTemplateWithInterpolation (choose one of the sigTemplateMakerWithInterpolation directories, e.g. sigTemplateMakerWithInterpolation_WpToBpT_Bp400_Top170) : ') or "DUMMYDIR")
        stTries += 1
    if(not os.path.isdir('./'+sigTemplate)):
        print("you had five tries to get it right...")
        exit()

    minMscan = options.minMscan
    if(minMscan < 0):
        minMscan = int(input("starting mass for significance scan? "))
    maxMscan = options.maxMscan
    if(maxMscan < 0):
        maxMscan = int(input("ending mass for significance scan? "))
    massgaps = options.massgaps
    if(massgaps < 0):
        massgaps = int(input("step size between masses "))

    newDirName = dirName+'_'+sigTemplate

    if(os.path.isdir("./"+newDirName)):
        redo = raw_input("Directory already exists.  Do you want to overwrite? [y/n] ")
        if(redo == "y" or redo == "Y"):
            shutil.rmtree("./"+newDirName)
            os.system("cp -r "+fullPathToH5s+" ./"+newDirName)
            os.chdir("./"+newDirName)
        else:
            exit()
    else:
        os.system("cp -r "+fullPathToH5s+" ./"+newDirName)
        os.chdir("./"+newDirName)

    os.system("ln -s ../*.py .")
    os.system("ln -s ../"+sigTemplate+"/ .")

    dc_templ_file = open("./significanceFull_TEMPLATE.sh")
    dc_file = open("significanceFull.sh","w")
    for line in dc_templ_file:
        line=line.replace('MASSMIN', str(minMscan))
        line=line.replace('MASSMAX', str(maxMscan))
        line=line.replace('GAPS', str(massgaps))
        line=line.replace('SIGTEMPLATEDIR', str(sigTemplate))
        dc_file.write(line)
    dc_file.close()
    dc_templ_file.close()

    dc_templ_file = open("./significanceCorner_TEMPLATE.sh")
    dc_file = open("significanceCorner.sh","w")
    for line in dc_templ_file:
        line=line.replace('MASSMIN', str(minMscan))
        line=line.replace('MASSMAX', str(maxMscan))
        line=line.replace('GAPS', str(massgaps))
        line=line.replace('SIGTEMPLATEDIR', str(sigTemplate))
        dc_file.write(line)
    dc_file.close()
    dc_templ_file.close()


    print(os.getcwd())
    cmd1 = "source ./significanceFull.sh"
    print(cmd1)
    os.system(cmd1)

