import os
from Fitter import Fitter
from DataCardMaker import DataCardMaker
from Utils import load_h5_sig, load_h5_sb, load_h5_fracSig, load_h5_numEv, truncate, apply_blinding
from Utils import f_test, calculateChi2, PlotFitResults, checkSBFit
from Utils import check_rough_sig, roundTo
from array import array
import pickle
import json
import random
import optparse

import tdrstyle
import ROOT
ROOT.gStyle.SetOptStat(0)
ROOT.gStyle.SetOptTitle(0)
tdrstyle.setTDRStyle()
ROOT.gROOT.SetBatch(True)
ROOT.RooRandom.randomGenerator().SetSeed(random.randint(0, 1e+6))


def fit_signalmodel(input_file, sig_file_name, mass, x_bins, fine_bins,
                    plot_dir, return_fit=False, dcb_model=False, fit_range = 0.2):
    fine_bin_size = 4
    bins_fine = int(x_bins[-1]-x_bins[0])/fine_bin_size

    mlow = (1.0 - fit_range) * mass
    mhigh = (1.0 + fit_range) * mass

    bins_sig_fit = array(
        'f', truncate(
             [x_bins[0] + ib*fine_bin_size for ib in range(bins_fine + 1)],
             mlow, mhigh)
        )

    large_bins_sig_fit = array('f', truncate(x_bins, mlow, mhigh))
    roobins_sig_fit = ROOT.RooBinning(len(large_bins_sig_fit) - 1,
                                      array('d', large_bins_sig_fit),
                                      "mjjbins_sig")

    histos_sig = ROOT.TH1F("mjj_sig", "mjj_sig",
                           len(bins_sig_fit) - 1, bins_sig_fit)

    load_h5_sig(input_file, histos_sig, mass)
    sig_outfile = ROOT.TFile(sig_file_name, "RECREATE")
    fitter = Fitter(['mjj_fine'])

    if dcb_model:
        fitter.signalDCB('model_s', "mjj_fine", mass)
    else:
        fitter.signalResonance('model_s', "mjj_fine", mass)

    fitter.w.var("MH").setVal(mass)
    fitter.importBinnedData(histos_sig, ['mjj_fine'], 'data')
    fres = fitter.fit('model_s', 'data', [ROOT.RooFit.Save(1)])
    #fres.Print()
    mjj_fine = fitter.getVar('mjj_fine')
    mjj_fine.setBins(len(bins_sig_fit))

    chi2_fine = fitter.projection("model_s", "data", "mjj_fine",
                                  plot_dir + "signal_fit.png")

    fitter.projection("model_s", "data", "mjj_fine",
                      plot_dir + "signal_fit_log.png", 0, False)

    chi2 = fitter.projection("model_s", "data", "mjj_fine",
                             plot_dir + "signal_fit_binned.png",
                             roobins_sig_fit, logy=False)

    fitter.projection("model_s", "data", "mjj_fine",
                      plot_dir + "signal_fit_log_binned.png",
                      roobins_sig_fit, logy=False)

    sig_outfile.cd()
    histos_sig.Write()

    if dcb_model:
        graphs = {'mean': ROOT.TGraphErrors(),
                  'sigma': ROOT.TGraphErrors(),
                  'alpha': ROOT.TGraphErrors(),
                  'alpha2': ROOT.TGraphErrors(),
                  'sign': ROOT.TGraphErrors(),
                  'sign2': ROOT.TGraphErrors()}
    else:
        graphs = {'mean': ROOT.TGraphErrors(),
                  'sigma': ROOT.TGraphErrors(),
                  'alpha': ROOT.TGraphErrors(),
                  'sign': ROOT.TGraphErrors(),
                  'scalesigma': ROOT.TGraphErrors(),
                  'sigfrac': ROOT.TGraphErrors()}

    for var, graph in graphs.iteritems():
        value, error = fitter.fetch(var)
        graph.SetPoint(0, mass, value)
        graph.SetPointError(0, 0.0, error)

    sig_outfile.cd()
    for name, graph in graphs.iteritems():
        graph.Write(name)

    sig_outfile.Close()

    print (
        """
        #############################
        signal fit chi2 (fine binning), %.3f
        signal fit chi2 (large binning), %.3f
        #############################
        """ % (chi2_fine, chi2)
        )

    if return_fit:
        return fitter
    else:
        return None


def cardWriter(options,histos_sb,qcd_fname,nPars_QCD,sig_file_name,extraName="",signalOnly=False, fracSig=1.):
    if(not signalOnly):
        sb_fname = "sb_fit.root"
        sb_outfile = ROOT.TFile(sb_fname, 'RECREATE')
        sb_outfile.cd()
        histos_sb.Write("mjj_sb")
        sb_outfile.Close()
        sig_data_name = 'mjj_sb'
    if options.tag == None:
        sb_label = "raw"
    else:
        sb_label = options.tag

    card = DataCardMaker(sb_label,extraName,signalOnly)
    if options.dcb_model:
        if options.tag == None:
            card.addDCBSignalShape('model_signal_mjj', 'mjj', sig_file_name,
                                   {'CMS_scale_j': 1.0}, {'CMS_res_j': 1.0})
        else:
            card.addDCBSignalShape('model_signal_mjj', 'mjj', sig_file_name,
                                   {'CMS_scale_j': 1.0}, {'CMS_res_j': 1.0})
    else:
        if options.tag == None:
            card.addSignalShape('model_signal_mjj', 'mjj', sig_file_name,
                                {'CMS_scale_j': 1.0}, {'CMS_res_j': 1.0})
        else:
            card.addSignalShape('model_signal_mjj', 'mjj', sig_file_name,
                                {'CMS_scale_j': 1.0}, {'CMS_res_j': 1.0})
    constant = options.sig_norm

    if options.tag == None:
        sig_norm = card.addFixedYieldFromFile('model_signal_mjj', 0, sig_file_name,
                                              "mjj_sig", constant=constant)
    else:
        #sig_norm = card.addFloatingYield('model_signal_mjj', 0, sig_file_name, "mjj_sig", 0., 1000.)
        constant = constant*10.
        sig_norm = card.addFixedYieldFromFile('model_signal_mjj', 0, sig_file_name,
                                              "mjj_sig", constant=constant*fracSig)
        #sig_norm = card.addFixedYieldFromFilev2('model_signal_mjj', 0, sig_file_name,
        #                                      "mjj_sig", constant=constant)
    #sig_norm = card.addFloatingYield('model_signal_mjj', 0, sig_file_name,
    #                                 "mjj_sig", constant=False)
    if(not signalOnly):
        card.addSystematic("CMS_scale_j", "param", [0.0, 0.012])
        card.addSystematic("CMS_res_j", "param", [0.0, 0.08])
        if((not (options.tag == None)) and (not options.corner)):
            if(not extraName=="_FLOAT"):
                card.addSystematic("model_signal_mjj_"+str(options.tag)+"_norm", "param", [1.0, .1])
            card.addSystematic("model_signal_mjj_"+str(options.tag)+"_norm", "rateParam", 1.0, bin="JJ_"+str(options.tag), process="model_signal_mjj", variables="[0.,2.]")

    if(not signalOnly):
        if options.tag == None:
            card.addQCDShapeNoTag('model_qcd_mjj', 'mjj', qcd_fname, nPars_QCD)
            card.addFloatingYield('model_qcd_mjj', 1, sb_fname, "mjj_sb")
        else:
            card.addQCDShape('model_qcd_mjj', 'mjj', qcd_fname, nPars_QCD)
            card.addFloatingYield('model_qcd_mjj', 1, sb_fname, "mjj_sb")
        for i in range(1, nPars_QCD + 1):
            if options.tag == None:
                card.addSystematic("CMS_JJ_p%i" % i, "flatParam", [])
            else:
                card.addSystematic("CMS_JJ_p%i_JJ_" % i + str(options.tag), "flatParam", [])
                
        if options.tag == None:
            card.addSystematic("model_qcd_mjj_JJ_norm", "flatParam", [])
        else:
            card.addSystematic("model_qcd_mjj_JJ_"+str(options.tag)+"_norm", "flatParam", [])
            #card.addSystematic("model_signal_mjj_JJ_"+str(options.tag)+"_norm", "flatParam", [])

        card.importBinnedData("sb_fit.root", sig_data_name,
                              ["mjj"], 'data_obs', 1.0)

        if(options.sig_norm_unc > 0):
            card.addSystematic("SigEff", "lnN", values = {"model_signal_mjj" : 1. + options.sig_norm_unc})
    card.makeCard()
    card.delete()
    
    return sig_norm


def dijetfit(options):
    label = options.label
    plot_dir = options.plotDir
    if(plot_dir[-1] != '/'):
        plot_dir += '/'

    os.system("mkdir %s" % plot_dir)
    os.system("mkdir %s" % plot_dir)

    fine_bin_size = 4
    mass = options.mass 





    binsx = [1460, 1530, 1607, 1687, 1770, 1856, 1945, 2037, 2132, 2231, 2332, 2438,
             2546, 2659, 2775, 2895, 3019, 3147, 3279, 3416, 3558, 3704, 3854,
             4010, 4171, 4337, 4509, 4686, 4869, 5058, 5253, 5500, 5663, 5877,
             6099, 6328, 6564, 6808]
    #binsx = [2132, 2231, 2332, 2438,
    #         2546, 2659, 2775, 2895, 3019, 3147, 3279, 3416, 3558, 3704, 3854,
    #         4010, 4171, 4337, 4509, 4686, 4869, 5058, 5253, 5500, 5663, 5877,
    #         6099, 6328, 6564, 6808]
    #binsx = [2132, 2231, 2332, 2438,
    #         2546, 2659, 2775, 2895, 3019, 3147, 3279, 3416, 3558, 3704, 3854,
    #         4010, 4171, 4337, 4509]
    #binsx = [1607, 1687, 1770, 1856, 1945, 2037, 2132, 2231, 2332, 2438,
    #         2546, 2659, 2775, 2895, 3019, 3147, 3279, 3416, 3558, 3704, 3854,
    #         4010, 4171, 4337, 4509, 4686, 4869, 5058, 5253, 5500, 5663, 5877]
    
    #binsx = [1460, 1530, 1607, 1687, 1770, 1856, 1945, 2037, 2132, 2231, 2332, 2438,
    #         2546, 2659, 2775, 2895, 3019, 3147, 3279]

    #binsx = [2231, 2332, 2438,
    #         2546, 2659, 2775, 2895, 3019, 3147, 3279, 3416, 3558, 3704, 3854,
    #         4010, 4171]

    #binsx = [3019, 3147, 3279, 3416, 3558, 3704, 3854,
    #         4010, 4171, 4337, 4509, 4686, 4869, 5058, 5253, 5500, 5663, 5877,
    #         6099, 6328, 6564, 6808]

    #binsx=range(1600,6088,88)
    
    #binsx=range(1600,3800,88)+range(3800,6176,176)
    
    #binsx=range(1600,4000,88)
    #binsx=range(1600,4000,44)
    #binsx=range(1600,4000,176)
    
    #binsx=range(1600,6000,176)
    #binsx=range(3000,6900,176)
    
    #binsx=range(2000,6000,176)
    #binsx=range(1900,3800,88)+range(3800,6176,176)
    #binsx=range(1600,6088,98)
    #binsx=range(1460,3800,90)+range(3800,6300,250)

    if(options.mjj_min > 0 and options.mjj_min < binsx[-1]):
        start_idx = 0
        while(binsx[start_idx] < options.mjj_min):
            start_idx +=1
        binsx = binsx[start_idx:]

        if(abs(options.mjj_min - binsx[0]) < 50.):
            binsx[0] = options.mjj_min
        else:
            binsx.insert(0, options.mjj_min)
        print("Will start fit from %.0f GeV" % binsx[0])

    # round to smallest precision we are storing mass values with, otherwise
    # get weird effects related to bin size
    roundTo(binsx, fine_bin_size)


    roobins = ROOT.RooBinning(len(binsx)-1, array('d', binsx), "mjjbins")
    bins_fine = int(binsx[-1] - binsx[0])/fine_bin_size









    fracSig = 1.0
    if options.tag == None:
        sb_label = "raw"
    else:
        sb_label = options.tag
        fracSig = load_h5_fracSig(options.inputFile)
    if(options.noReFit and os.path.exists(("datacard_JJ_{l2}.txt").format(l2=sb_label)) and os.path.exists(("datacard_JJ_{l2}_FLOAT.txt").format(l2=sb_label))):

        if(not os.path.exists(options.sig_shape)):
            print("Sig file %s doesn't exist" % options.sig_shape)
            exit(1)
        sig_file_name = options.sig_shape
        sig_norm = cardWriter(options,"","","",sig_file_name,"",options.noReFit,fracSig)
        if(not options.tag == None):
            sig_norm2 = cardWriter(options,"","","",sig_file_name,"_FLOAT", options.noReFit)

            #if options.tag == None:
            #    cmd = (
            #        "text2workspace.py datacard_JJ_{l2}.txt "
            #        + "-o workspace_JJ_{l1}_{l2}.root "
            #        + "&& combine -M Significance workspace_JJ_{l1}_{l2}.root "
            #        + "-m {mass} -n significance_{l1}_{l2} "
            #        + "&& combine -M Significance workspace_JJ_{l1}_{l2}.root "
            #        + "-m {mass} --pvalue -n pvalue_{l1}_{l2} "
            #        #+ "&& combine -M AsymptoticLimits workspace_JJ_{l1}_{l2}.root "
            #        #+ "-m {mass} -n lim_{l1}_{l2}"
            #    ).format(mass=mass, l1=label, l2=sb_label)
            #else:
            #    cmd = (
            #        "text2workspace.py datacard_JJ_{l2}_FLOAT.txt "
            #        + "-o workspace_JJ_{l1}_{l2}.root "
            #    ).format(mass=mass, l1=label, l2=sb_label)
            #print(cmd)
            #os.system(cmd)
            
            #numEv = 50000
            #if(not options.tag == None):
            #    numEv = load_h5_numEv(options.inputFile)
            #    
            #if(not options.tag == None):
            #    sbfit_chi2, sbfit_ndof = checkSBFit('workspace_JJ_{l1}_{l2}.root'.format(l1=label, l2=sb_label),
            #                                        sb_label, roobins, label + "_" + sb_label, 4, plot_dir, numEv)
        return 0











    histos_sb = ROOT.TH1F("mjj_sb", "mjj_sb" ,bins_fine, binsx[0], binsx[-1])
    
    # useful to check if doing blinding correctly
    #load_h5_sb(options.inputFile, histos_sb, sb1_edge=sb1_edge + 40.,
    #           sb2_edge=sb2_edge - 40.)
    
    load_h5_sb(options.inputFile, histos_sb)
    print("************ Found %i total events \n" % histos_sb.GetEntries())

    if(options.refit_sig):
        print ("########## FIT SIGNAL AND SAVE PARAMETERS ############")
        sig_file_name = "sig_fit.root"

        fit_signalmodel(options.inputFile, sig_file_name, mass, binsx, bins_fine, plot_dir,return_fit=False,
                        dcb_model=options.dcb_model)

    else:  # use precomputed signal shape
        if(not os.path.exists(options.sig_shape)):
            print("Sig file %s doesn't exist" % options.sig_shape)
            exit(1)
        sig_file_name = options.sig_shape



    print("\n\n ############# FIT BACKGROUND AND SAVE PARAMETERS ###########")
    #nParsToTry = [2, 3, 4]
    #nParsToTry = [2,3,4,6]
    nParsToTry = [2,3,4,6]
    #nParsToTry = [2,3,4,6]
    chi2s = [0]*len(nParsToTry)
    ndofs = [0]*len(nParsToTry)
    probs = [0]*len(nParsToTry)
    qcd_fnames = [""]*len(nParsToTry)
    sb1_edge = 2232
    sb2_edge = 2776

    regions = [("SB1", binsx[0], sb1_edge),
               ("SB2", sb2_edge, binsx[-1]),
               ("SR", sb1_edge, sb2_edge),
               ("FULL", binsx[0], binsx[-1])]

    blind_range = ROOT.RooFit.Range("SB1,SB2")
    full_range = ROOT.RooFit.Range("FULL")
    fit_ranges = [(binsx[0], sb1_edge), (sb2_edge, binsx[-1])]

    histos_sb_blind = apply_blinding(histos_sb, ranges=fit_ranges)
    num_blind = histos_sb_blind.Integral()

    if options.blinded:
        fitting_histogram = histos_sb_blind
        data_name = "data_qcd_blind"
        fit_range = blind_range
        chi2_range = fit_ranges
        norm = ROOT.RooFit.Normalization(num_blind, ROOT.RooAbsReal.NumEvent)

    else:
        fitting_histogram = histos_sb
        data_name = "data_qcd"
        fit_range = full_range
        chi2_range = None
        norm = ROOT.RooFit.Normalization(histos_sb.Integral(),
                                         ROOT.RooAbsReal.NumEvent)

    for i, nPars in enumerate(nParsToTry):
        print("Trying %i parameter background fit" % nPars)
        qcd_fnames[i] = str(nPars) + 'par_qcd_fit%i.root' % i
        qcd_outfile = ROOT.TFile(qcd_fnames[i], 'RECREATE')

        model_name = "model_b" + str(i)
        fitter_QCD = Fitter(['mjj_fine'])
        fitter_QCD.qcdShape(model_name, 'mjj_fine', nPars)
        fitter_QCD.importBinnedData(fitting_histogram, ['mjj_fine'], data_name,
                                    regions=regions)

        # For some reason (???) the first fit gives some weird results, but if
        # you fit it twice it works ok??? This should be fixed...
        
        fres = fitter_QCD.fit(model_name, data_name,
                              options=[ROOT.RooFit.Save(1),
                                       ROOT.RooFit.Verbose(0),
                                       fit_range])
        fres = fitter_QCD.fit(model_name, data_name,
                              options=[ROOT.RooFit.Save(1),
                                       ROOT.RooFit.Verbose(0),
                                       fit_range])

        chi2_fine = fitter_QCD.projection(
            model_name, data_name, "mjj_fine",
            plot_dir + str(nPars) + "par_qcd_fit.png", 0, False)

        #chi2_binned = fitter_QCD.projection(
        #     model_name, data_name, "mjj_fine",
        #     plot_dir + str(nPars) + "par_qcd_fit_binned.png",roobins,True)

        qcd_outfile.cd()
        histos_sb_blind.Write()

        mjj = fitter_QCD.getVar('mjj_fine')
        mjj.setBins(bins_fine)
        model = fitter_QCD.getFunc(model_name)
        dataset = fitter_QCD.getData(data_name)

        frame = mjj.frame()
        dataset.plotOn(frame, ROOT.RooFit.DataError(ROOT.RooAbsData.Poisson),
                       ROOT.RooFit.Name(data_name), ROOT.RooFit.Invisible(),
                       ROOT.RooFit.Binning(roobins))

        model.plotOn(frame, ROOT.RooFit.VisualizeError(fres, 1),
                     ROOT.RooFit.FillColor(ROOT.kRed - 7),
                     ROOT.RooFit.LineColor(ROOT.kRed - 7),
                     ROOT.RooFit.Name(fres.GetName()), 
                     fit_range.Clone(), norm)

        model.plotOn(frame, ROOT.RooFit.LineColor(ROOT.kRed + 1),
                     ROOT.RooFit.Name(model_name), 
                     fit_range.Clone(), norm)
        

        # Compute integrals over signal region
        #mjj_set = ROOT.RooArgSet(mjj)
        #sig_region_integral = model.createIntegral(
        #    mjj_set,
        #    ROOT.RooFit.NormSet(mjj_set),
        #    ROOT.RooFit.Range("SR")).getVal()
        #
        #full_integral = model.createIntegral(mjj_set,
        #                                     ROOT.RooFit.NormSet(mjj_set),
        #                                     full_range).getVal()
        #
        #print("Sig region integral " , sig_region_integral)
        #print("Full integral " , full_integral)
        #num_full = num_blind * (1 + sig_region_integral/full_integral)
        #full_norm = ROOT.RooFit.Normalization(histos_sb.Integral(),
        #                                      ROOT.RooAbsReal.NumEvent)

        dataset.plotOn(frame, ROOT.RooFit.DataError(ROOT.RooAbsData.Poisson),
                       ROOT.RooFit.Name(data_name), ROOT.RooFit.XErrorSize(0),
                       ROOT.RooFit.Binning(roobins))

        # for correct pulls:
        model.plotOn(frame, ROOT.RooFit.Invisible(),
                     ROOT.RooFit.Name(model_name), full_range, norm)

        # average bin edges instead of bin center
        framePulls = mjj.frame()
        useBinAverage = True
        hpull = frame.pullHist(data_name, model_name, useBinAverage)
        framePulls.addPlotable(hpull, "X0 P E1")

        my_chi2, my_ndof = calculateChi2(hpull, nPars, ranges=chi2_range)
        my_prob = ROOT.TMath.Prob(my_chi2, my_ndof)
        """
        PlotFitResults(frame, fres.GetName(), nPars, framePulls, data_name,
                       model_name, my_chi2, my_ndof,
                       str(nPars) + "par_qcd_fit_binned{}".format(
                           "_blinded" if options.blinded else ""),
                       plot_dir)
        """
        PlotFitResults(frame, fres.GetName(), nPars, framePulls, data_name,
                       model_name, my_chi2, my_ndof,
                       str(nPars) + "par_qcd_fit_binned{}".format(
                           "_blinded" if options.blinded else ""),
                       plot_dir, False, False,6000)

        graphs = {}
        for p in range(nPars):
            graphs['p%i' % (p + 1)] = ROOT.TGraphErrors()

        for var, graph in graphs.iteritems():
            print('hello, ', var)
            value, error = fitter_QCD.fetch(var)
            graph.SetPoint(0, mass, value)
            graph.SetPointError(0, 0.0, error)

        qcd_outfile.cd()
        for name, graph in graphs.iteritems():
            graph.Write(name)
        qcd_outfile.Close()

        print("#############################")
        print("% i Parameter results: " % nPars)
        print("bkg fit chi2/nbins (fine binning) ", chi2_fine)
        print("My chi2, ndof, prob", my_chi2, my_ndof, my_prob)
        print("My chi/ndof, chi2/nbins", my_chi2/my_ndof,
              my_chi2/(my_ndof + nPars))
        print("#############################")

        chi2s[i] = my_chi2
        ndofs[i] = my_ndof
        probs[i] = my_prob
        fitter_QCD.delete()

    best_i = f_test(nParsToTry, ndofs, chi2s)
    nPars_QCD = nParsToTry[best_i]
    qcd_fname = qcd_fnames[best_i]
    print("\n Chose %i parameters based on F-test ! \n" % nPars_QCD)

    # Fit to total data
    #histos_sb.Print("range")
    #histos_qcd.Print("range")
    #histos_sig.Print("range")
    print("************ Found", histos_sb.GetEntries(), "total events")

    sb_fname = "sb_fit.root"
    sb_outfile = ROOT.TFile(sb_fname, 'RECREATE')
    sb_outfile.cd()
    histos_sb.Write("mjj_sb")
    sb_outfile.Close()
    sig_data_name = 'mjj_sb'
    fracSig = 1.0
    if options.tag == None:
        sb_label = "raw"
    else:
        sb_label = options.tag
        fracSig = load_h5_fracSig(options.inputFile)



    sig_norm = cardWriter(options,histos_sb,qcd_fname,nPars_QCD,sig_file_name,"",False,fracSig)
    if(not options.tag == None):
        sig_norm2 = cardWriter(options,histos_sb,qcd_fname,nPars_QCD,sig_file_name,"_FLOAT", False)
    """
    card = DataCardMaker(sb_label)
    if options.dcb_model:
        if options.tag == None:
            card.addDCBSignalShape('model_signal_mjj', 'mjj', sig_file_name,
                                   {'CMS_scale_j': 1.0}, {'CMS_res_j': 1.0})
        else:
            card.addDCBSignalShape('model_signal_mjj', 'mjj', sig_file_name,
                                   {'CMS_scale_j': 1.0}, {'CMS_res_j': 1.0})
    else:
        if options.tag == None:
            card.addSignalShape('model_signal_mjj', 'mjj', sig_file_name,
                                {'CMS_scale_j': 1.0}, {'CMS_res_j': 1.0})
        else:
            card.addSignalShape('model_signal_mjj', 'mjj', sig_file_name,
                                {'CMS_scale_j': 1.0}, {'CMS_res_j': 1.0})
    constant = options.sig_norm

    if options.tag == None:
        sig_norm = card.addFixedYieldFromFile('model_signal_mjj', 0, sig_file_name,
                                              "mjj_sig", constant=constant)
    else:
        #sig_norm = card.addFloatingYield('model_signal_mjj', 0, sig_file_name, "mjj_sig", 0., 1000.)
        sig_norm = card.addFixedYieldFromFile('model_signal_mjj', 0, sig_file_name,
                                              "mjj_sig", constant=constant)
        #sig_norm = card.addFixedYieldFromFilev2('model_signal_mjj', 0, sig_file_name,
        #                                      "mjj_sig", constant=constant)
    #sig_norm = card.addFloatingYield('model_signal_mjj', 0, sig_file_name,
    #                                 "mjj_sig", constant=False)
    card.addSystematic("CMS_scale_j", "param", [0.0, 0.012])
    card.addSystematic("CMS_res_j", "param", [0.0, 0.08])
    if(not (options.tag == None)):
        #card.addSystematic("model_signal_mjj_"+str(options.tag)+"_norm", "param", [1.0, 2.0])
        card.addSystematic("model_signal_mjj_"+str(options.tag)+"_norm", "rateParam", "1.0 [0.,2.]", bin="JJ_"+str(options.tag), process="model_signal_mjj")

    if options.tag == None:
        card.addQCDShapeNoTag('model_qcd_mjj', 'mjj', qcd_fname, nPars_QCD)
        card.addFloatingYield('model_qcd_mjj', 1, sb_fname, "mjj_sb")
    else:
        card.addQCDShape('model_qcd_mjj', 'mjj', qcd_fname, nPars_QCD)
        card.addFloatingYield('model_qcd_mjj', 1, sb_fname, "mjj_sb")
    for i in range(1, nPars_QCD + 1):
        if options.tag == None:
            card.addSystematic("CMS_JJ_p%i" % i, "flatParam", [])
        else:
            card.addSystematic("CMS_JJ_p%i_JJ_" % i + str(options.tag), "flatParam", [])
    
    if options.tag == None:
        card.addSystematic("model_qcd_mjj_JJ_norm", "flatParam", [])
    else:
        card.addSystematic("model_qcd_mjj_JJ_"+str(options.tag)+"_norm", "flatParam", [])
        #card.addSystematic("model_signal_mjj_JJ_"+str(options.tag)+"_norm", "flatParam", [])

    card.importBinnedData("sb_fit.root", sig_data_name,
                          ["mjj"], 'data_obs', 1.0)

    if(options.sig_norm_unc > 0):
        card.addSystematic("SigEff", "lnN", values = {"model_signal_mjj" : 1. + options.sig_norm_unc})
    card.makeCard()
    card.delete()
    """
    if options.tag == None:
        cmd = (
            "text2workspace.py datacard_JJ_{l2}.txt "
            + "-o workspace_JJ_{l1}_{l2}.root "
            + "&& combine -M Significance workspace_JJ_{l1}_{l2}.root "
            + "-m {mass} -n significance_{l1}_{l2} "
            + "&& combine -M Significance workspace_JJ_{l1}_{l2}.root "
            + "-m {mass} --pvalue -n pvalue_{l1}_{l2} "
            #+ "&& combine -M AsymptoticLimits workspace_JJ_{l1}_{l2}.root "
            #+ "-m {mass} -n lim_{l1}_{l2}"
            ).format(mass=mass, l1=label, l2=sb_label)
    else:
        cmd = (
            "text2workspace.py datacard_JJ_{l2}_FLOAT.txt "
            + "-o workspace_JJ_{l1}_{l2}.root "
            ).format(mass=mass, l1=label, l2=sb_label)
    print(cmd)
    os.system(cmd)

    numEv = 50000
    if(not options.tag == None):
        numEv = load_h5_numEv(options.inputFile)

    if(not options.tag == None):
        sbfit_chi2, sbfit_ndof = checkSBFit('workspace_JJ_{l1}_{l2}.root'.format(l1=label, l2=sb_label),
                                            sb_label, roobins, label + "_" + sb_label, nPars_QCD, plot_dir, numEv)
        return 0

    sbfit_chi2, sbfit_ndof = checkSBFit('workspace_JJ_{l1}_{l2}.root'.format(l1=label, l2=sb_label),
                                        sb_label, roobins, label + "_" + sb_label, nPars_QCD, plot_dir, numEv)

    sbfit_prob = ROOT.TMath.Prob(sbfit_chi2, sbfit_ndof)

    f_signif_name = ('higgsCombinesignificance_{l1}_{l2}.'
                     + 'Significance.mH{mass:.0f}.root'
                     ).format(mass=mass, l1=label, l2=sb_label)
    f_limit_name = ('higgsCombinelim_{l1}_{l2}.'
                    + 'AsymptoticLimits.mH{mass:.0f}.root'
                    ).format(mass=mass, l1=label, l2=sb_label)
    f_pval_name = ('higgsCombinepvalue_{l1}_{l2}.'
                   + 'Significance.mH{mass:.0f}.root'
                   ).format(mass=mass, l1=label, l2=sb_label)

    f_signif = ROOT.TFile(f_signif_name, "READ")
    res1 = f_signif.Get("limit")
    res1.GetEntry(0)
    signif = res1.limit
    print("Significance is %.3f \n" % signif)

    f_limit = ROOT.TFile(f_limit_name, "READ")
    res2 = f_limit.Get("limit")
    eps = 0.01
    obs_limit = -1
    exp_limit = exp_low = exp_high = exp_two_low = exp_two_high = -1
    
    for i in range(6):
        res2.GetEntry(i)
        if(res2.quantileExpected == -1):  # obs limit
            obs_limit = res2.limit
        elif(abs(res2.quantileExpected - 0.5) < eps):  # exp limit
            exp_limit = res2.limit
        elif(abs(res2.quantileExpected - 0.025) < eps):  # 2sigma, low
            exp_two_low = res2.limit
        elif(abs(res2.quantileExpected - 0.16) < eps):  # 1sigma, low
            exp_low = res2.limit
        elif(abs(res2.quantileExpected - 0.84) < eps):  # 1sigma, high
            exp_high = res2.limit
        elif(abs(res2.quantileExpected - 0.975) < eps):  # 2sigma, high
            exp_two_high = res2.limit

    print("Obs limit is %.3f (%.1f events)" % (obs_limit, obs_limit*sig_norm))
    print("Expected was %.3f (%.1f events)" % (exp_limit, exp_limit*sig_norm))
    print("Expected range %.1f-%.1f (one sigma), %.1f-%.1f (two sigma)" % (exp_low * sig_norm, exp_high*sig_norm, exp_two_low * sig_norm, exp_two_high * sig_norm))

    f_pval = ROOT.TFile(f_pval_name, "READ")
    res3 = f_pval.Get("limit")
    res3.GetEntry(0)
    pval = res3.limit
    print("p-value is %.3f \n" % pval)

    # TODO: Comment back in
    #check_rough_sig(options.inputFile, options.mass*0.9, options.mass*1.1)
    f_signif.Close()
    f_limit.Close()
    f_pval.Close()
    results = dict()

    # QCD fit results
    results['bkgfit_chi2'] = chi2s[best_i]
    results['bkgfit_ndof'] = ndofs[best_i]
    results['bkgfit_prob'] = probs[best_i]
    results['sbfit_chi2'] = sbfit_chi2
    results['sbfit_ndof'] = sbfit_ndof
    results['sbfit_prob'] = sbfit_prob
    results['nPars_QCD'] = nPars_QCD
    results['signif'] = signif
    results['pval'] = pval
    results['obs_lim_events'] = obs_limit*sig_norm
    results['exp_lim_events'] = exp_limit*sig_norm
    results['exp_lim_1sig_low'] = exp_low * sig_norm
    results['exp_lim_2sig_low'] = exp_two_low * sig_norm
    results['exp_lim_1sig_high'] = exp_high * sig_norm
    results['exp_lim_2sig_high'] = exp_two_high* sig_norm
    results['sig_norm_unc'] = options.sig_norm_unc
    results['mass'] = options.mass
    results['mjj_min'] = options.mjj_min

    print("Saving fit results to %s" % plot_dir + "fit_results_{}.pkl".format(options.mass))
    with open(plot_dir + "fit_results_{}.pkl".format(options.mass), "w") as f:
        pickle.dump(results, f)
        
    print("Also saving fit results to %s" % plot_dir + "fit_results_{}.json".format(options.mass))
    with open(plot_dir + "fit_results_{}.json".format(options.mass), "w") as jsonfile:
        json.dump(results, jsonfile)

    return results


def fitting_options():
    parser = optparse.OptionParser()
    parser.add_option("--mjj_min", type=float, default=-1.0,
                      help="Minimum mjj for the fit")
    parser.add_option("--sig_norm", type=float, default=1.0,
                      help="Scale signal pdf normalization by this amount")
    parser.add_option("-s", "--sig_shape", default="signal_shape_m2500.root",
                      help="Pre-saved signal shape")
    parser.add_option("--refit_sig", default=False, action="store_true",
                      help="""Fit the signal events (using truth labels)
                      to get signal shape""")
    parser.add_option("-M", "-M", dest="mass", type=float, default=2500.,
                      help="Injected signal mass")
    parser.add_option("-i", "--inputFile", dest="inputFile",
                      default='fit_inputs/no_selection_03p.h5',
                      help="input h5 file")
    parser.add_option("-p", "--plotDir", dest="plotDir", default='plots/',
                      help="Where to put the plots")
    parser.add_option("-l", "--label", dest="label", default='test',
                      help="Label for file names")
    parser.add_option("-t", "--tag", dest="tag", default=None,
                      help="Label for file names")
    parser.add_option("-c", "--corner", dest="corner", default=False,
                      help="Is this the corner bin?")
    parser.add_option("--noReFit", dest="noReFit", default=False,
                      help="Should I refit background or use pre-existing files (for QUAK)")
    parser.add_option("-b", "--blinded", dest="blinded", action="store_true",
                      default=False,
                      help="Blinding the signal region for the fit.")
    parser.add_option("--dcb-model", dest="dcb_model", action="store_true",
                      default=False,
                      help="""Whether to use double crystal ball model instead
                      of default model (gaussian core with single crystal ball)""")
    parser.add_option("--sig_norm_unc", dest="sig_norm_unc", type=float, default= -1.0, help="Fractional uncertainty on signal normalization")
    return parser


if __name__ == "__main__":
    parser = fitting_options()
    (options, args) = parser.parse_args()
    dijetfit(options)

