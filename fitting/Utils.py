import h5py, math, commands, random
from array import array
import numpy as np
import time, sys, os, optparse, json, copy

import ROOT
ROOT.gStyle.SetOptStat(0)
ROOT.gStyle.SetOptTitle(0)
import CMS_lumi, tdrstyle
tdrstyle.setTDRStyle()
ROOT.gROOT.SetBatch(True)
ROOT.RooRandom.randomGenerator().SetSeed(random.randint(0, 1e+6))

# function to extract string from function -> in order write a proper json file
def returnString(func,ftype):
    if func.GetName().find("corr")!=-1:
        st = "("+str(func.GetParameter(0))+" + ("+str(func.GetParameter(1))+")*MJ1 + ("+str(func.GetParameter(2))+")*MJ2  + ("+str(func.GetParameter(3))+")*MJ1*MJ2)"
        if func.GetName().find("sigma")!=-1:
            st = "("+str(func.GetParameter(0))+" + ("+str(func.GetParameter(1))+")*MJ1 + ("+str(func.GetParameter(2))+")*MJ2 )"
        return st
    else:
        if ftype.find("pol")!=-1:
            st='(0'
            if func.GetName().find("corr")!=-1: 
                n = 1. #func.Integral(55,215)
                st = "(0"
                for i in range(0,func.GetNpar()):
                    st = st+"+("+str(func.GetParameter(i))+")"+("*(MJ1+MJ2)/2."*i)
                st+=")/"+str(n)
            else:
                for i in range(0,func.GetNpar()):
                    st=st+"+("+str(func.GetParameter(i))+")"+("*MH"*i)
                st+=")"
            return st
        if ftype.find("1/sqrt")!=-1:
            st='(0'
            if func.GetName().find("corr")!=-1:
                n = 1. # func.Integral(55,215)
                st = str(func.GetParameter(0))+"+("+str(func.GetParameter(1))+")*1/sqrt((MJ1+MJ2)/2.)/"+str(n)
            else:
                st = str(func.GetParameter(0))+"+("+str(func.GetParameter(1))+")"+")*1/sqrt(MH)"
                st+=")"
            return st
        if ftype.find("sqrt")!=-1 and ftype.find("1/")==-1:
            n =1.
            st='(0'
            if func.GetName().find("corr")!=-1: st = str(func.GetParameter(0))+"+("+str(func.GetParameter(1))+")"+"*sqrt((MJ1+MJ2)/2.))/"+str(n)
            else:
                st = str(func.GetParameter(0))+"+("+str(func.GetParameter(1))+")"+"*sqrt(MH)"
                st+=")"
            return st    
        if ftype.find("llog")!=-1:
            return str(func.GetParameter(0))+"+"+str(func.GetParameter(1))+"*log(MH)"
        if ftype.find("laur")!=-1:
            st='(0'
            for i in range(0,func.GetNpar()):
                st=st+"+("+str(func.GetParameter(i))+")"+"/MH^"+str(i)
            st+=")"
            return st    
        if ftype.find("spline")!=-1:
            print "write json for spline function: a list and not a string will be returned in this case"
            st=[]
            nnknots = func.GetNp()
            for i in range(0,nnknots):
                x = ROOT.Double(0) 
                y = ROOT.Double(0) 
                func.GetKnot(i,x,y)
                st.append([x,y])
            return st
        else:
            return ""

def get_palette(mode):

 palette = {}
 palette['gv'] = [] 
 
 colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728',
              '#9467bd', '#8c564b', '#e377c2', '#7f7f7f',
              '#bcbd22', '#17becf']

 for c in colors:
  palette['gv'].append(c)
 
 return palette[mode]
 
def getBinning(binsMVV,minx,maxx,bins):
    l=[]
    if binsMVV=="":
        print " do this"
        print binsMVV
        for i in range(0,bins+1):
            l.append(minx + i* (maxx - minx)/bins)
    else:
        print "dot that"
        print binsMVV
        s = binsMVV.split(",")
        for w in s:
            l.append(int(w))
    return l

def truncate(binning,mmin,mmax):
    res=[]
    for b in binning:
        if b >= mmin and b <= mmax:
            res.append(b)
    return res


def PlotFitResults(frame,fitErrs,nPars,pulls,data_name,pdf_names,chi2,ndof,canvname, plot_dir, has_sig = False, dolog=True, setMax = 1E4):

    c1 =ROOT.TCanvas("c1","",800,800)
    if(dolog):
        c1.SetLogy()
    c1.Divide(1,2,0,0,0)
    if(dolog):
        c1.SetLogy()
    c1.cd(1)
    p11_1 = c1.GetPad(1)
    p11_1.SetPad(0.01,0.26,0.99,0.98)
    if(dolog):
        p11_1.SetLogy()
    p11_1.SetRightMargin(0.05)

    p11_1.SetTopMargin(0.1)
    p11_1.SetBottomMargin(0.02)
    p11_1.SetFillColor(0)
    p11_1.SetBorderMode(0)
    p11_1.SetFrameFillStyle(0)
    p11_1.SetFrameBorderMode(0)
    frame.GetYaxis().SetTitleSize(0.06)
    frame.GetYaxis().SetTitleOffset(0.98)
    frame.SetMinimum(0.2)
    #frame.SetMaximum(1E7)
    frame.SetMaximum(setMax)
    frame.SetName("mjjFit")
    frame.GetYaxis().SetTitle("Events / 100 GeV")
    frame.SetTitle("")
    frame.Draw()
        
    legend = ROOT.TLegend(0.45097293,0.64183362,0.6681766,0.879833)
    legend2 = ROOT.TLegend(0.45097293,0.64183362,0.6681766,0.879833)
    legend.SetTextSize(0.046)
    legend.SetLineColor(0)
    legend.SetShadowColor(0)
    legend.SetLineStyle(1)
    legend.SetLineWidth(1)
    legend.SetFillColor(0)
    legend.SetFillStyle(0)
    legend.SetMargin(0.35)
    legend2.SetTextSize(0.038)
    legend2.SetLineColor(0)
    legend2.SetShadowColor(0)
    legend2.SetLineStyle(1)
    legend2.SetLineWidth(1)
    legend2.SetFillColor(0)
    legend2.SetFillStyle(0)
    legend2.SetMargin(0.35)
    legend.AddEntry(frame.findObject(data_name),"Data","lpe")
    if(not has_sig): 
        legend.AddEntry(frame.findObject(pdf_names[0]),"%i par. background fit"%nPars,"l")

    else: 
        legend.AddEntry(frame.findObject(pdf_names[0]),"Signal + Background Fit ","l")
    legend2.AddEntry("","","")
    legend2.AddEntry("","","")
    legend2.AddEntry("","","")
    legend2.AddEntry("","","")
    legend2.AddEntry(frame.findObject(fitErrs),"","f")
    legend2.AddEntry("","","")

    legend2.Draw("same")
    legend.Draw("same")

    pt = ROOT.TPaveText(0.18,0.06,0.54,0.17,"NDC")
    pt.SetTextFont(42)
    pt.SetTextAlign(12)
    pt.SetFillColor(0)
    pt.SetBorderSize(0)
    pt.SetFillStyle(0)
    pt.AddText("Chi2/ndf = %.2f/%i = %.2f"%(chi2,ndof,chi2/ndof))
    pt.AddText("Prob = %.3f"%ROOT.TMath.Prob(chi2,ndof))
    pt.Draw()
    
    c1.Update()

    c1.cd(2)
    p11_2 = c1.GetPad(2)
    p11_2.SetPad(0.01,0.02,0.99,0.27)
    p11_2.SetBottomMargin(0.35)
    p11_2.SetRightMargin(0.05)
    p11_2.SetGridx(0)
    p11_2.SetGridy(0)
    pulls.SetMinimum(-5)
    pulls.SetMaximum(5)
    pulls.SetTitle("")
    pulls.SetXTitle("Dijet invariant mass (GeV)")
    pulls.GetXaxis().SetTitleSize(0.06)
    pulls.SetYTitle("#frac{Data-Fit}{#sigma_{data}}")
    pulls.GetYaxis().SetTitleSize(0.15)
    pulls.GetYaxis().CenterTitle()
    pulls.GetYaxis().SetTitleOffset(0.30)
    pulls.GetYaxis().SetLabelSize(0.15)
    pulls.GetXaxis().SetTitleSize(0.17)
    pulls.GetXaxis().SetTitleOffset(0.91)
    pulls.GetXaxis().SetLabelSize(0.12)
    pulls.GetXaxis().SetNdivisions(906)
    pulls.GetYaxis().SetNdivisions(305)
    pulls.Draw("same")
    line = ROOT.TLine(frame.GetXaxis().GetXmin() , 0 , frame.GetXaxis().GetXmax(),0)
    line1  = ROOT.TLine(frame.GetXaxis().GetXmin(), 1 ,frame.GetXaxis().GetXmax(),1)
    line2  = ROOT.TLine(frame.GetXaxis().GetXmin(), -1 ,frame.GetXaxis().GetXmax(),-1)
    line1.SetLineStyle(2)
    line1.SetLineWidth(2)
    line2.SetLineStyle(2)
    line2.SetLineWidth(2)
    line.Draw("same")
    line1.Draw("same")
    line2.Draw("same")   
    c1.Update()

    canvname+='.png'
    c1.SaveAs(plot_dir + canvname)
    #c1.SaveAs(canvname.replace("png","C"),"C")

def calculateChi2(g_pulls, nPars, ranges = None):
     
    NumberOfVarBins = 0
    NumberOfObservations_VarBin = 0
    chi2_VarBin = 0.
     

    a_x = array('d', [0.])
    a_val = array('d', [0.])
    for p in range (0,g_pulls.GetN()):
    
        g_pulls.GetPoint(p, a_x, a_val)
        x = a_x[0]
        pull = a_val[0]

        #print x,pull

        add = True
        if(ranges is not None and len(ranges) > 0):
            add = False
            for range_ in ranges:
                if(x >= range_[0] and x<= range_[1]):
                    add = True
         
        if(add):
            NumberOfObservations_VarBin+=1
            chi2_VarBin += pow(pull,2)
            print(p, pow(pull,2), chi2_VarBin)
            
    ndf_VarBin = NumberOfObservations_VarBin - nPars
    return chi2_VarBin,ndf_VarBin

def apply_blinding(h, ranges = None):
    if(ranges is None or len(ranges) == 0):
        print("Must supply list of tuples specifying ranges to include")

    h_clone = h.Clone(h.GetName() + "_blinded")
    axis = h.GetXaxis()
    for i in range(axis.GetNbins()):
        low_edge = axis.GetBinLowEdge(i)
        high_edge = axis.GetBinLowEdge(i)

        inRange = False
        for interval in ranges:
            if(low_edge >= interval[0] and high_edge <= interval[1]):
                inRange = True

        if(not inRange):
            h_clone.SetBinContent(i, 0.)
            h_clone.SetBinError(i, 0.)
    return h_clone

def load(iFile,iVar,iName,iHist,iCut):
    lFile = ROOT.TFile(iFile)
    lTree = lFile.Get("Events")
    pTH  = ROOT.TH1F(iName+"tmp",  iName+"tmp", iHist.GetNbinsX(),iHist.GetXaxis().GetXmin(),iHist.GetXaxis().GetXmax())
    lTree.Draw(iVar+">>"+iName+"tmp",iCut)
    iHist.Add(pTH)
    lFile.Close()


def roundTo(arr, base):
    for i in range(len(arr)):
        x = arr[i]
        new_x = int(base * round(float(x)/base)) + base/2
        arr[i] = new_x



def fill_hist(v, h, event_num = None):
    h.Sumw2()
    #print("%i events in the dataset " % len(v))
    if(event_num is None):
        for x in v: h.Fill(x)
    else:
        e_dict = dict()
        for idx,x in enumerate(v):
            e_num = event_num[idx]
            e_dict[e_num] = (x, e_dict.get(e_num, (0,0))[1] + 1)

        print("%i unique events"% len(e_dict.keys()))
        for k in e_dict.keys():
            x = e_dict[k][0]
            n = e_dict[k][1]
            h.Fill(x,n)

        print("%.0f filled events" % h.Integral())
    #h.Print("range")


def load_h5_fracSig(h_file):
    with h5py.File(h_file, "r") as f:
        return np.array(f['fracSig'][0])


def load_h5_numEv(h_file):
    with h5py.File(h_file, "r") as f:
        return np.array(f['numEv'][0])


def load_h5_sb(h_file, hist, correctStats=False, sb1_edge = -1., sb2_edge = -1.):
    event_num = None
    with h5py.File(h_file, "r") as f:
        mjj = np.array(f['mjj'][()])
        if(correctStats):
            event_num = f['event_num'][()]

    fill_hist(mjj, hist, event_num)

def load_h5_bkg(h_file, hist, correctStats = False):
    event_num = None
    with h5py.File(h_file, "r") as f:
        mjj = f['mjj'][()]
        is_sig = f['truth_label'][()]
        if(correctStats):
            event_num = f['event_num'][()]

    mask = (is_sig < 0.1)
    if(correctStats): event_num = event_num[mask]
    fill_hist(mjj[mask], hist, event_num)


def load_h5_sig(h_file, hist, sig_mjj, correctStats =False):
    event_num = None
    with h5py.File(h_file, "r") as f:
        try:
            mjj = f['jet_kinematics'][:, 0]
        except:
            mjj = f['mjj'][()]

        num_evts = mjj.shape[0]
        is_sig = f['truth_label'][()].flatten()


        if(is_sig.shape[0] != mjj.shape[0]):
            #fix bug in old h5 maker where is_sig array would be too long
            is_sig = is_sig[:num_evts]
        
        if(correctStats):
            event_num = f['event_num'][()]


    mask = (mjj > 0.8*sig_mjj) & (mjj < 1.2*sig_mjj) & (is_sig > 0.9)
    if(correctStats): event_num = event_num[mask]
    fill_hist(mjj[mask], hist, event_num)

def check_rough_sig(h_file, m_low, m_high):
    with h5py.File(h_file, "r") as f:
        mjj = f['mjj'][()]
        is_sig = f['truth_label'][()]

    in_window = (mjj > m_low) & (mjj < m_high)
    sig_events = is_sig > 0.9
    bkg_events = is_sig < 0.1
    S = mjj[sig_events & in_window].shape[0]
    B = mjj[bkg_events & in_window].shape[0]
    print("Mjj window %f to %f " % (m_low, m_high))
    print("S = %i, B = %i, S/B %f, sigificance ~ %.1f " % (S, B, float(S)/B, S/np.sqrt(B)))
    
def checkSBFit(filename,label,roobins,plotname, nPars, plot_dir, numEv = 10000):
    
    fin = ROOT.TFile.Open(filename,'READ')
    workspace = fin.w

    model_tot = workspace.pdf('model_s')
    model_qcd = workspace.pdf('model_b')
    model_sig = workspace.pdf('shapeSig_model_signal_mjj_JJ_%s' % label)
    var = workspace.var('mjj')
    data = workspace.data('data_obs')


    #sig_norm_var_total = workspace.function('n_exp_binJJ_%s_proc_model_signal_mjj' % label).getVal()
    #var.setRange("int_range", 1500., 6500)
    #set_ = ROOT.RooArgSet(var)
    #sig_norm_var_denom = model_sig.createIntegral(set_, set_, "int_range").getVal()

    #sig_norm_var_coeff = sig_norm_var_total/ sig_norm_var_denom
    #print(sig_norm_var_coeff, sig_norm_var_denom )
    #sig_norm_var_coeff = 1e-4

    #sig_norm_var = ROOT.RooRealVar("sig_norm_var", "Signal Normalization", sig_norm_var_coeff, sig_norm_var_coeff/100., sig_norm_var_coeff*100.)
    #sig_norm_var.Print("v")

    #sig_norm_pdf = ROOT.RooAddPdf("sig_norm", "Signal", ROOT.RooArgList(model_sig), ROOT.RooArgList(sig_norm_var))
    #sig_norm_pdf.Print("v")


    model = model_tot

    model_tot.Print("v")

    
    fres = model.fitTo(data,ROOT.RooFit.SumW2Error(1),ROOT.RooFit.Minos(0),ROOT.RooFit.Verbose(0),ROOT.RooFit.Save(1),ROOT.RooFit.NumCPU(8)) 
    #fres.Print()
    
    frame = var.frame()
    data.plotOn(frame,ROOT.RooFit.DataError(ROOT.RooAbsData.Poisson), ROOT.RooFit.Binning(roobins),ROOT.RooFit.Name("data_obs"),ROOT.RooFit.Invisible())
    model.getPdf('JJ_%s'%label).plotOn(frame,ROOT.RooFit.VisualizeError(fres,1),ROOT.RooFit.FillColor(ROOT.kRed-7),ROOT.RooFit.LineColor(ROOT.kRed-7),ROOT.RooFit.Name(fres.GetName()))
    model.getPdf('JJ_%s'%label).plotOn(frame,ROOT.RooFit.LineColor(ROOT.kRed+1),ROOT.RooFit.Name("model_s"))
    #model_qcd.plotOn(frame,ROOT.RooFit.VisualizeError(fres,1),ROOT.RooFit.FillColor(ROOT.kGreen-7),ROOT.RooFit.LineColor(ROOT.kGreen-7), ROOT.RooFit.Name("Background"))
    #model_qcd.plotOn(frame,ROOT.RooFit.LineColor(ROOT.kRed+1),ROOT.RooFit.Name("Background"))
    #sig_norm_pdf.plotOn(frame,ROOT.RooFit.VisualizeError(fres,1),ROOT.RooFit.FillColor(ROOT.kBlue-7),ROOT.RooFit.LineColor(ROOT.kBlue-7), ROOT.RooFit.Name("Signal"))
    #sig_norm_pdf.plotOn(frame,ROOT.RooFit.LineColor(ROOT.kBlue+1), ROOT.RooFit.Name("Signal"))

    frame3 = var.frame()
    #average bin edges instead of bin center
    useBinAverage = True
    hpull = frame.pullHist("data_obs","model_s",useBinAverage)
    frame3.addPlotable(hpull,"X0 P E1")
    
    data.plotOn(frame,ROOT.RooFit.DataError(ROOT.RooAbsData.Poisson), ROOT.RooFit.Binning(roobins),ROOT.RooFit.Name("data_obs"),ROOT.RooFit.XErrorSize(0))
    chi2,ndof = calculateChi2(hpull, nPars +1)

    pdf_names = ["model_s"] 
    PlotFitResults(frame,fres.GetName(),nPars+1,frame3,"data_obs", pdf_names,chi2,ndof,'sbFit_'+plotname, plot_dir, has_sig = True, dolog = False, setMax = float(numEv)/5.)

    print "chi2,ndof are", chi2, ndof
    return chi2, ndof


def checkBFit(filename,label,roobins,plotname, nPars, plot_dir, numEv = 10000):
    
    fin = ROOT.TFile.Open(filename,'READ')
    workspace = fin.w

    model_tot = workspace.pdf('model_s')
    model_qcd = workspace.pdf('model_b')
    model_sig = workspace.pdf('shapeSig_model_signal_mjj_JJ_%s' % label)
    var = workspace.var('mjj')
    data = workspace.data('data_obs')

    model = model_qcd

    model_tot.Print("v")

    
    fres = model.fitTo(data,ROOT.RooFit.SumW2Error(1),ROOT.RooFit.Minos(0),ROOT.RooFit.Verbose(0),ROOT.RooFit.Save(1),ROOT.RooFit.NumCPU(8)) 
    #fres.Print()
    
    frame = var.frame()
    data.plotOn(frame,ROOT.RooFit.DataError(ROOT.RooAbsData.Poisson), ROOT.RooFit.Binning(roobins),ROOT.RooFit.Name("data_obs"),ROOT.RooFit.Invisible())
    model.getPdf('JJ_%s'%label).plotOn(frame,ROOT.RooFit.VisualizeError(fres,1),ROOT.RooFit.FillColor(ROOT.kRed-7),ROOT.RooFit.LineColor(ROOT.kRed-7),ROOT.RooFit.Name(fres.GetName()))
    model.getPdf('JJ_%s'%label).plotOn(frame,ROOT.RooFit.LineColor(ROOT.kRed+1),ROOT.RooFit.Name("model_b"))
    #model_qcd.plotOn(frame,ROOT.RooFit.VisualizeError(fres,1),ROOT.RooFit.FillColor(ROOT.kGreen-7),ROOT.RooFit.LineColor(ROOT.kGreen-7), ROOT.RooFit.Name("Background"))
    #model_qcd.plotOn(frame,ROOT.RooFit.LineColor(ROOT.kRed+1),ROOT.RooFit.Name("Background"))
    #sig_norm_pdf.plotOn(frame,ROOT.RooFit.VisualizeError(fres,1),ROOT.RooFit.FillColor(ROOT.kBlue-7),ROOT.RooFit.LineColor(ROOT.kBlue-7), ROOT.RooFit.Name("Signal"))
    #sig_norm_pdf.plotOn(frame,ROOT.RooFit.LineColor(ROOT.kBlue+1), ROOT.RooFit.Name("Signal"))

    frame3 = var.frame()
    #average bin edges instead of bin center
    useBinAverage = True
    hpull = frame.pullHist("data_obs","model_b",useBinAverage)
    frame3.addPlotable(hpull,"X0 P E1")
    
    data.plotOn(frame,ROOT.RooFit.DataError(ROOT.RooAbsData.Poisson), ROOT.RooFit.Binning(roobins),ROOT.RooFit.Name("data_obs"),ROOT.RooFit.XErrorSize(0))
    chi2,ndof = calculateChi2(hpull, nPars +1)

    pdf_names = ["model_b"] 
    PlotFitResults(frame,fres.GetName(),nPars+1,frame3,"data_obs", pdf_names,chi2,ndof,'bFit_'+plotname, plot_dir, has_sig = True, dolog = False, setMax = float(numEv)/5.)

    print "background only? chi2,ndof are", chi2, ndof
    return chi2, ndof



def f_test(nParams, nDof, chi2, thresh = 0.05):
    #assumes arrays are in increasing number of params order (ie nParams[0] is minimum number of params)
    print  "\n\n #################### STARTING F TEST #######################" 
    best_i = 0
    for i in range(1, len(nParams)):
        print("F test comparing %i to %i params" % (nParams[best_i], nParams[i]))
        nDof_base = nDof[best_i]
        chi2_base = chi2[best_i]

        nDof_new = nDof[i]
        chi2_new = chi2[i]

        F_num =   max((chi2_base - chi2_new), 0)/(abs(nDof_new - nDof_base))
        F_denom = chi2_new/nDof_new 
        F = F_num / F_denom

        prob = 1. - ROOT.TMath.FDistI(F, abs(nDof_new - nDof_base), nDof_new)

        print("Base chi2 was %.1f, new is %.1f" % (chi2_base, chi2_new))
        print("F is %.2f, prob is %.3f" % (F, prob))

        if(prob < thresh):
            print("Prob below threshold, switching to %i parameters" % nDof_new)
            best_i = i

    return best_i
