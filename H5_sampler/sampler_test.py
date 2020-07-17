from Sampler import * 

np.random.seed(123)

pbTofb = 1000.
holdout_frac = 0.1
qcd1 = Sampler("../H5_maker/test_files/QCD_HT1000to1500_test.h5", pbTofb * 1088., 1., holdout_frac = holdout_frac)
qcd2 = Sampler("../H5_maker/test_files/QCD_HT1500to2000_test.h5", pbTofb * 99.11, 1., holdout_frac = holdout_frac)
qcd3 = Sampler("../H5_maker/test_files/QCD_HT2000toInf_test.h5", pbTofb * 20.23, 1., holdout_frac = holdout_frac)
sig = Sampler("../H5_maker/test_files/WprimeToWZToWhadZhad_narrow_M-3500_TuneCP5_13TeV-madgraph_test.h5", 30000., 1., holdout_frac = holdout_frac)

#ws = [qcd1, qcd2, qcd3, sig]
ws = [qcd1]
keys= ['event_info', 'jet_kinematics', 'truth_label', 'jet1_extraInfo', 'jet1_PFCands']
#keys= []
BB = BlackBox(ws, keys)
#print(BB['truth_label'].shape)
#print(BB['jet_kinematics'].shape)

BB.writeOut('BB_test_Wprime2.h5')
BB.writeHoldOut('BB_test_Wprime_holdout.h5')

f1 = h5py.File("BB_test_Wprime2.h5")
f_out = h5py.File("BB_test_Wprime_holdout.h5")
f_orig = h5py.File("../H5_maker/test_files/QCD_HT1000to1500_test.h5")

e1 = f1['event_info'][:,0]
e_out = f_out['event_info'][:,0]
e_orig = f_orig['event_info'][:,0]

print(e_orig[99000], e_orig[0])
print(np.where(e_out == e_orig[99000]))
print(np.where(e_out == e_orig[0]))
print(np.where(e1 == e_orig[99000]))
print(np.where(e1 == e_orig[0]))

