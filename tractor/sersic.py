'''
This file is part of the Tractor project.
Copyright 2014, Dustin Lang and David W. Hogg.
Licensed under the GPLv2; see the file COPYING for details.

`sersic.py`
===========

General Sersic galaxy model.
'''
from __future__ import print_function
if __name__ == '__main__':
    import matplotlib
    matplotlib.use('Agg')

import numpy as np

from scipy.interpolate import InterpolatedUnivariateSpline

from tractor import mixture_profiles as mp
from tractor.engine import *
from tractor.utils import *
from tractor.cache import *
from tractor.galaxy import *

class SersicMixture(object):
    singleton = None

    @staticmethod
    def getProfile(sindex):
        if SersicMixture.singleton is None:
            SersicMixture.singleton = SersicMixture()
        return SersicMixture.singleton._getProfile(sindex)

    def __init__(self):

        # A set of ranges [ser_lo, ser_hi], plus a list of fit parameters
        # that have a constant number of components.
        fits = [
        # 0.3 to 0.4: 3 components
        (0.3, 0.4, [
            ( 0.3, [ 58.7009, 26.6643, -77.6263,  ], [ 0.374934, 0.259725, 0.309937,  ]),
            ( 0.31, [ 55.832, 26.0986, -74.1271,  ], [ 0.383453, 0.266779, 0.316079,  ]),
            ( 0.32, [ 52.1761, 20.7647, -65.0721,  ], [ 0.393596, 0.270377, 0.324867,  ]),
            ( 0.33, [ 48.2145, 20.5634, -60.8428,  ], [ 0.404221, 0.278975, 0.331068,  ]),
            ( 0.34, [ 44.6425, 19.8606, -56.5018,  ], [ 0.415356, 0.287766, 0.33808,  ]),
            ( 0.35 , [ 38.474, 19.0401, -49.4458,  ], [ 0.430137, 0.296236, 0.342944,  ]),
            ( 0.36 , [ 35.4008, 15.8085, -43.0745,  ], [ 0.443372, 0.304082, 0.35272,  ]),
            ( 0.37 , [ 31.2277, 9.84678, -32.8717,  ], [ 0.459762, 0.306352, 0.364545,  ]),
            ( 0.38 , [ 31.7832, 9.33791, -32.8517,  ], [ 0.469717, 0.322657, 0.37966,  ]),
            ( 0.39 , [ 27.5299, 8.56064, -27.7538,  ], [ 0.487979, 0.337244, 0.387988,  ]),
            ( 0.4 , [ 25.3526, 8.26534, -25.2139,  ], [ 0.504439, 0.35851, 0.401166,  ]),
        ]),
        # 0.4 to 0.55: 2 components
        (0.4, 0.55, [
            ( 0.4, [ 30.6846, -22.2722,  ], [ 0.508451, 0.446199,  ]),
            ( 0.41, [ 25.0737, -16.5994,  ], [ 0.524289, 0.446576,  ]),
            ( 0.42, [ 18.0254, -9.4867,  ], [ 0.550982, 0.434251,  ]),
            ( 0.43, [ 13.6102, -5.00379,  ], [ 0.584497, 0.409865,  ]),
            ( 0.44, [ 11.7669, -3.09259,  ], [ 0.612188, 0.389683,  ]),
            ( 0.45, [ 10.7878, -2.04641,  ], [ 0.635513, 0.373375,  ]),
            ( 0.46, [ 10.1779, -1.37019,  ], [ 0.655982, 0.359586,  ]),
            ( 0.47 , [ 9.76207, -0.888915,  ], [ 0.6744, 0.347566,  ]),
            ( 0.48 , [ 9.4625, -0.524704,  ], [ 0.69123, 0.336936,  ]),
            ( 0.49 , [ 9.23869, -0.237081,  ], [ 0.706771, 0.327762,  ]),
            ( 0.5 , [ 9.06469, 0., ], [ 0.721344, 0.317480, ]),
            ( 0.51 , [ 8.93379, 0.192965,  ], [ 0.734739, 0.307521,  ]),
            ( 0.52 , [ 8.82887, 0.359221,  ], [ 0.747417, 0.300307,  ]),
            ( 0.53 , [ 8.74585, 0.502753,  ], [ 0.759346, 0.293121,  ]),
            ( 0.54 , [ 8.68019, 0.628124,  ], [ 0.770591, 0.286212,  ]),
            ( 0.55 , [ 8.6284, 0.738804,  ], [ 0.781204, 0.279618,  ]),
        ]),
        # 0.55 to 0.6: 3 components
        (0.55, 0.6, [
            ( 0.55, [ 7.74689, 1.58844, 0.0471616,  ], [ 0.819452, 0.417783, 0.087336,  ]),
            ( 0.6 , [ 7.24439, 2.34223, 0.101213,  ], [ 0.903276, 0.400292, 0.0809628,  ]),
        ]),
        # 0.6 to 0.7: 4 components
        (0.6, 0.7, [
            ( 0.6, [ 6.51642, 2.93043, 0.23537, 0.0110102,  ], [ 0.936973, 0.470973, 0.145644, 0.0262609,  ]),
            ( 0.65, [ 6.20741, 3.40835, 0.356027, 0.0186731,  ], [ 1.02778, 0.464541, 0.138526, 0.0241383,  ]),
            ( 0.7 , [ 6.09066, 3.69635, 0.462077, 0.0267968,  ], [ 1.10839, 0.456139, 0.130467, 0.0219376,  ]),
        ]),
        # 0.7 to 0.8: 5 components
        (0.7, 0.8, [
            ( 0.7 , [ 5.84168, 3.79731, 0.577526, 0.0579033, 0.00354215,  ], [ 1.12585, 0.48453, 0.161388, 0.042217, 0.0069345,  ]),
            ( 0.75 , [ 5.76156, 3.9978, 0.710656, 0.0784835, 0.00500513,  ], [ 1.20661, 0.48315, 0.156679, 0.0399674, 0.00632141,  ]),
            (0.8 , [ 5.81724, 4.10126, 0.796872, 0.0949571, 0.00637949,  ], [ 1.27229, 0.472825, 0.147499, 0.0367043, 0.00562926,  ]),
            ]),
        # 0.8 to 1.5: 6 components
        (0.8, 1.5, [
            ( 0.8, [ 5.72857, 4.08637, 0.856856, 0.12965, 0.0149739, 0.00101254,  ], [ 1.28015, 0.486267, 0.164269, 0.0495874, 0.012034, 0.001834,  ]),            
            ( 0.85 , [ 5.79045, 4.17745, 0.935745, 0.146717, 0.0190671, 0.00142406,  ], [ 1.34252, 0.477737, 0.154878, 0.0459309, 0.0114826, 0.00173367,  ]),
            ( 0.9 , [ 5.8557, 4.23792, 1.02098, 0.174855, 0.0229433, 0.0017022,  ], [ 1.39994, 0.47177, 0.149963, 0.0438891, 0.0104706, 0.00152136,  ]),
            ( 0.95 , [ 5.9249, 4.29628, 1.10244, 0.196489, 0.0260153, 0.00193019,  ], [ 1.45307, 0.466037, 0.144107, 0.0408279, 0.00939357, 0.00130824,  ]),
            ( 1.0 , [ 5.9993, 4.33731, 1.1797, 0.223345, 0.0308597, 0.00236367,  ], [ 1.50134, 0.460918, 0.140004, 0.0391621, 0.00886677, 0.0012064,  ]),
            ( 1.1 , [ 6.15062, 4.41112, 1.3184, 0.274191, 0.0403516, 0.00320267,  ], [ 1.58689, 0.450782, 0.13188, 0.0356906, 0.00775213, 0.00100251,  ]),
            ( 1.2 , [ 6.30488, 4.46833, 1.44113, 0.325257, 0.0503063, 0.00417751,  ], [ 1.65866, 0.440764, 0.124769, 0.0327207, 0.00682769, 0.000840013,  ]),
            ( 1.3 , [ 6.45554, 4.5196, 1.55166, 0.370943, 0.0599356, 0.00513795,  ], [ 1.71804, 0.430598, 0.117757, 0.0297864, 0.00597877, 0.000701129,  ]),
            ( 1.4 , [ 6.60022, 4.57474, 1.64799, 0.41237, 0.0688686, 0.00608043,  ], [ 1.76906, 0.420073, 0.110836, 0.0270161, 0.00520979, 0.000584642,  ]),
            ( 1.5 , [ 6.74056, 4.62707, 1.73452, 0.450323, 0.0774227, 0.00701844,  ], [ 1.81111, 0.409301, 0.104252, 0.0244973, 0.00454782, 0.000489254,  ]),
        ]),
        # 1.5 to 3: 7 components
        (1.5, 3., [
            ( 1.5 , [ 6.65296, 4.5365, 1.77608, 0.534095, 0.121048, 0.0193193, 0.00168448,  ],
              [ 1.82965, 0.427338, 0.118659, 0.0325505, 0.0078754, 0.00149129, 0.000162814,  ]),
            ( 2.0 , [ 7.17044, 4.75678, 2.16275, 0.741344, 0.188867, 0.0326777, 0.00301683,  ],
              [ 1.9857, 0.389519, 0.0944922, 0.022482, 0.0046957, 0.000750913, 6.74e-05,  ]),
            ( 2.5 , [ 7.65858, 4.9943, 2.39882, 0.865786, 0.230782, 0.04241, 0.0042324,  ],
              [ 2.02962, 0.340732, 0.0718239, 0.014861, 0.00271533, 0.000383584, 3.00206e-05,  ]),
            ( 3.0 , [ 8.14037, 5.24329, 2.54101, 0.923932, 0.249893, 0.0470254, 0.00479733,  ],
              [ 1.99866, 0.287531, 0.0523859, 0.00945259, 0.00152236, 0.0001892, 1.27979e-05,  ]),
        ]),
        # 3 to 6: 8 components
            (3., 6., [
                ( 3.0 , [ 7.87232, 5.07258, 2.66081, 1.11232, 0.365881, 0.0926224, 0.0165507, 0.00161176,  ],
                  [ 2.09507, 0.330596, 0.0687515, 0.0145811, 0.00289201, 0.000496723, 6.45785e-05, 4.44168e-06,  ]),
                ( 3.5 , [ 8.26554, 5.31143, 2.79218, 1.16256, 0.383548, 0.0976501, 0.017588, 0.00172762,  ],
                  [ 2.04798, 0.283894, 0.0518779, 0.00976488, 0.00173505, 0.000267361, 3.10708e-05, 1.87943e-06,  ]),
                ( 4.0 , [ 8.65627, 5.50634, 2.87134, 1.19673, 0.400426, 0.10483, 0.0198332, 0.00218661,  ],
                  [ 1.95977, 0.240023, 0.0393048, 0.00674924, 0.00110933, 0.000160124, 1.77664e-05, 1.07394e-06,  ]),
                ( 4.5 , [ 9.00456, 5.64352, 2.92525, 1.23383, 0.427533, 0.117941, 0.0244185, 0.00328944,  ],
                  [ 1.84749, 0.203298, 0.03064, 0.004962, 0.000782651, 0.000110466, 1.24447e-05, 8.27834e-07,  ]),
                ( 5.0 , [ 9.2961, 5.76668, 2.99406, 1.28498, 0.459058, 0.13421, 0.0305669, 0.00507611,  ],
                  [ 1.75252, 0.176279, 0.0248229, 0.00382292, 0.000585089, 8.23458e-05, 9.65048e-06, 7.17946e-07,  ]),
                ( 5.5 , [ 9.55807, 5.85539, 3.0431, 1.33049, 0.492889, 0.152725, 0.0381639, 0.00763464,  ],
                  [ 1.6416, 0.152463, 0.0203278, 0.00302516, 0.000455831, 6.46416e-05, 7.92232e-06, 6.48294e-07,  ]),
                ( 6.0 , [ 9.78493, 5.92322, 3.08588, 1.37586, 0.528438, 0.17316, 0.0471653, 0.0111286,  ],
                  [ 1.52974, 0.132573, 0.0169092, 0.00245403, 0.000366917, 5.27406e-05, 6.76649e-06, 6.00237e-07,  ]),
            ]),
            ]
        
        # GalSim: supports n=0.3 to 6.2.
        
        # self.fits = [
        #     # (0.5,
        #     # np.array([  0.00000000e+000,   0.00000000e+000,   5.97360116e+198,
        #     #          7.26746001e-037,   2.50004003e-119,   9.77713758e-002,
        #     #          3.76242606e+000,   5.20454258e+000]),
        #     # np.array([  4.39317232e-43,   5.60638305e-26,   2.08879632e-25,
        #     #          1.26626995e-17,   1.58106523e-17,   7.01549406e-01,
        #     #          7.21125242e-01,   7.21890993e-01]),
        #     # ),
        #     # (0.55,
        #     # np.array([  1.59481046e+307,   3.15487712e+307,   2.45652327e-004,
        #     #          4.36909452e-003,   4.71731489e-002,   4.70269591e-001,
        #     #          3.71062814e+000,   5.15450190e+000]),
        #     # np.array([  3.52830040e-68,   2.06589509e-25,   6.35140546e-03,
        #     #          3.39547886e-02,   1.16386327e-01,   3.11207647e-01,
        #     #          6.23025538e-01,   8.88126344e-01]),
        #     # ),
        #     (0.6,
        #      np.array([2.35059121e-05,   4.13721322e-04,   3.92293893e-03,
        #                2.85625019e-02,   1.89838613e-01,   1.20615614e+00,
        #                4.74797981e+00,   3.52402557e+00]),
        #      np.array([9.56466036e-04,   5.63033141e-03,   2.09789252e-02,
        #                6.26359534e-02,   1.62128157e-01,   3.69124775e-01,
        #                6.99199094e-01,   1.06945187e+00]),
        #      ),
        #     (0.65,
        #      np.array([6.33289982e-05,   9.92144846e-04,   8.80546187e-03,
        #                6.04526939e-02,   3.64161094e-01,   1.84433400e+00,
        #                5.01041449e+00,   2.71713117e+00]),
        #      np.array([1.02431077e-03,   6.00267283e-03,   2.24606615e-02,
        #                6.75504786e-02,   1.75591563e-01,   3.99764693e-01,
        #                7.73156172e-01,   1.26419221e+00]),
        #      ),
        #     (0.7,
        #      np.array([1.39910412e-04,   2.11974313e-03,   1.77871639e-02,
        #                1.13073467e-01,   5.99838314e-01,   2.43606518e+00,
        #                4.97726634e+00,   2.15764611e+00]),
        #      np.array([1.07167590e-03,   6.54686686e-03,   2.48658528e-02,
        #                7.49393553e-02,   1.93700754e-01,   4.38556714e-01,
        #                8.61967334e-01,   1.48450726e+00]),
        #      ),
        #     (0.8,
        #      np.array([3.11928667e-04,   4.47378538e-03,   3.54873170e-02,
        #                2.07033725e-01,   9.45282820e-01,   3.03897766e+00,
        #                4.83305346e+00,   1.81226322e+00]),
        #      np.array([8.90900573e-04,   5.83282884e-03,   2.33187424e-02,
        #                7.33352158e-02,   1.97225551e-01,   4.68406904e-01,
        #                9.93007283e-01,   1.91959493e+00]),
        #      ),
        #     (0.9,
        #      np.array([5.26094326e-04,   7.19992667e-03,   5.42573298e-02,
        #                2.93808638e-01,   1.20034838e+00,   3.35614909e+00,
        #                4.75813890e+00,   1.75240066e+00]),
        #      np.array([7.14984597e-04,   4.97740520e-03,   2.08638701e-02,
        #                6.84402817e-02,   1.92119676e-01,   4.80831073e-01,
        #                1.09767934e+00,   2.35783460e+00]),
        #      ),
        #     # exp
        #     (1.,
        #      np.array([7.73835603e-04,   1.01672452e-02,   7.31297606e-02,
        #                3.71875005e-01,   1.39727069e+00,   3.56054423e+00,
        #                4.74340409e+00,   1.78731853e+00]),
        #      np.array([5.72481639e-04,   4.21236311e-03,   1.84425003e-02,
        #                6.29785639e-02,   1.84402973e-01,   4.85424877e-01,
        #                1.18547337e+00,   2.79872887e+00]),
        #      ),
        #     (1.25,
        #      np.array([1.43424042e-03,   1.73362596e-02,   1.13799622e-01,
        #                5.17202414e-01,   1.70456683e+00,   3.84122107e+00,
        #                4.87413759e+00,   2.08569105e+00]),
        #      np.array([3.26997106e-04,   2.70835745e-03,   1.30785763e-02,
        #                4.90588258e-02,   1.58683880e-01,   4.68953025e-01,
        #                1.32631667e+00,   3.83737061e+00]),
        #      ),
        #     (1.5,
        #      np.array([2.03745495e-03,   2.31813045e-02,   1.42838322e-01,
        #                6.05393876e-01,   1.85993681e+00,   3.98203612e+00,
        #                5.10207126e+00,   2.53254513e+00]),
        #      np.array([1.88236828e-04,   1.72537665e-03,   9.09041026e-03,
        #                3.71208318e-02,   1.31303364e-01,   4.29173028e-01,
        #                1.37227840e+00,   4.70057547e+00]),
        #      ),
        #     (1.75,
        #         np.array([2.50657937e-03,   2.72749636e-02,   1.60825323e-01,
        #                   6.52207158e-01,   1.92821692e+00,   4.05148405e+00,
        #                   5.35173671e+00,   3.06654746e+00]),
        #         np.array([1.09326774e-04,   1.09659966e-03,   6.25155085e-03,
        #                   2.75753740e-02,   1.05729535e-01,   3.77827360e-01,
        #                   1.34325363e+00,   5.31805274e+00]),
        #      ),
        #     # ser2
        #     (2.,
        #      np.array([2.83066070e-03,   2.98109751e-02,   1.70462302e-01,
        #                6.72109095e-01,   1.94637497e+00,   4.07818245e+00,
        #                5.58981857e+00,   3.64571339e+00]),
        #      np.array([6.41326241e-05,   6.98618884e-04,   4.28218364e-03,
        #                2.02745634e-02,   8.36658982e-02,   3.24006007e-01,
        #                1.26549998e+00,   5.68924078e+00]),
        #      ),
        #     (2.25,
        #      np.array([3.02233733e-03,   3.10959566e-02,   1.74091827e-01,
        #                6.74457937e-01,   1.93387183e+00,   4.07555480e+00,
        #                5.80412767e+00,   4.24327026e+00]),
        #      np.array([3.79516055e-05,   4.46695835e-04,   2.92969367e-03,
        #                1.48143362e-02,   6.54274109e-02,   2.72741926e-01,
        #                1.16012436e+00,   5.84499592e+00]),
        #      ),
        #     (2.5,
        #      np.array([3.09907888e-03,   3.13969645e-02,   1.73360850e-01,
        #                6.64847427e-01,   1.90082698e+00,   4.04984377e+00,
        #                5.99057823e+00,   4.84416683e+00]),
        #      np.array([2.25913531e-05,   2.86414090e-04,   2.00271733e-03,
        #                1.07730420e-02,   5.06946307e-02,   2.26291195e-01,
        #                1.04135407e+00,   5.82166367e+00]),
        #      ),
        #     (2.75,
        #      np.array([3.07759263e-03,   3.09199432e-02,   1.69375193e-01,
        #                6.46610533e-01,   1.85258212e+00,   4.00373109e+00,
        #                6.14743945e+00,   5.44062854e+00]),
        #      np.array([1.34771532e-05,   1.83790379e-04,   1.36657861e-03,
        #                7.79600019e-03,   3.89487163e-02,   1.85392485e-01,
        #                9.18220664e-01,   5.65190045e+00]),
        #      ),
        #     # ser3
        #     (3.,
        #      np.array([2.97478081e-03,   2.98325539e-02,   1.62926966e-01,
        #                6.21897569e-01,   1.79221947e+00,   3.93826776e+00,
        #                6.27309371e+00,   6.02826557e+00]),
        #      np.array([8.02949133e-06,   1.17776376e-04,   9.29524545e-04,
        #                5.60991573e-03,   2.96692431e-02,   1.50068210e-01,
        #                7.96528251e-01,   5.36403456e+00]),
        #      ),
        #     (3.25,
        #      np.array([2.81333543e-03,   2.83103276e-02,   1.54743106e-01,
        #                5.92538218e-01,   1.72231584e+00,   3.85446072e+00,
        #                6.36549870e+00,   6.60246632e+00]),
        #      np.array([4.77515101e-06,   7.53310436e-05,   6.30003331e-04,
        #                4.01365507e-03,   2.24120138e-02,   1.20086835e-01,
        #                6.80450508e-01,   4.98555042e+00]),
        #      ),
        #     (3.5,
        #      np.array([2.63493918e-03,   2.66202873e-02,   1.45833127e-01,
        #                5.61055473e-01,   1.64694115e+00,   3.75564199e+00,
        #                6.42306039e+00,   7.15406756e+00]),
        #      np.array([2.86364388e-06,   4.83717889e-05,   4.27246310e-04,
        #                2.86453738e-03,   1.68362578e-02,   9.52427526e-02,
        #                5.73853421e-01,   4.54960434e+00]),
        #      ),
        #     (3.75,
        #      np.array([2.52556233e-03,   2.52687568e-02,   1.38061528e-01,
        #                5.32259513e-01,   1.57489025e+00,   3.65196012e+00,
        #                6.44759766e+00,   7.66322744e+00]),
        #      np.array([1.79898320e-06,   3.19025602e-05,   2.94738112e-04,
        #                2.06601434e-03,   1.27125806e-02,   7.55475779e-02,
        #                4.81498066e-01,   4.10421637e+00]),
        #      ),
        #     # dev
        #     (4.,
        #      np.array([2.62202676e-03,   2.50014044e-02,   1.34130119e-01,
        #                5.13259912e-01,   1.52004848e+00,   3.56204592e+00,
        #                6.44844889e+00,   8.10104944e+00]),
        #      np.array([1.26864655e-06,   2.25833632e-05,   2.13622743e-04,
        #                1.54481548e-03,   9.85336661e-03,   6.10053309e-02,
        #                4.08099539e-01,   3.70794983e+00]),
        #      ),
        #     (4.25,
        #      np.array([2.98703553e-03,   2.60418901e-02,   1.34745429e-01,
        #                5.05981783e-01,   1.48704427e+00,   3.49526076e+00,
        #                6.43784889e+00,   8.46064115e+00]),
        #      np.array([1.02024747e-06,   1.74340853e-05,   1.64846771e-04,
        #                1.21125378e-03,   7.91888730e-03,   5.06072396e-02,
        #                3.52330049e-01,   3.38157214e+00]),
        #      ),
        #     (4.5,
        #      np.array([3.57010614e-03,   2.79496099e-02,   1.38169983e-01,
        #                5.05879847e-01,   1.46787842e+00,   3.44443589e+00,
        #                6.42125506e+00,   8.76168208e+00]),
        #      np.array([8.86446183e-07,   1.42626489e-05,   1.32908651e-04,
        #                9.82479942e-04,   6.53278969e-03,   4.28068927e-02,
        #                3.08213788e-01,   3.10322461e+00]),
        #      ),
        #     (4.75,
        #      np.array([4.34147576e-03,   3.04293019e-02,   1.43230140e-01,
        #                5.09832167e-01,   1.45679015e+00,   3.40356818e+00,
        #                6.40074908e+00,   9.01902624e+00]),
        #      np.array([8.01531774e-07,   1.20948120e-05,   1.10300128e-04,
        #                8.15434233e-04,   5.48651484e-03,   3.66906220e-02,
        #                2.71953278e-01,   2.85731362e+00]),
        #      ),
        #     # ser5
        #     (5.,
        #      np.array([5.30069413e-03,   3.33623146e-02,   1.49418074e-01,
        #                5.16448916e-01,   1.45115226e+00,   3.36990018e+00,
        #                6.37772131e+00,   9.24101590e+00]),
        #      np.array([7.41574279e-07,   1.05154771e-05,   9.35192405e-05,
        #                6.88777943e-04,   4.67219862e-03,   3.17741406e-02,
        #                2.41556167e-01,   2.63694124e+00]),
        #      ),
        #     (5.25,
        #      np.array([6.45944550e-03,   3.67009077e-02,   1.56495371e-01,
        #                5.25048515e-01,   1.44962975e+00,   3.34201845e+00,
        #                6.35327017e+00,   9.43317911e+00]),
        #      np.array([6.96302951e-07,   9.31687929e-06,   8.06697436e-05,
        #                5.90325057e-04,   4.02564583e-03,   2.77601343e-02,
        #                2.15789342e-01,   2.43845348e+00])
        #      ),
        #     (5.5,
        #      np.array([7.83422239e-03,   4.04238492e-02,   1.64329516e-01,
        #                5.35236245e-01,   1.45142179e+00,   3.31906077e+00,
        #                6.32826172e+00,   9.59975321e+00]),
        #      np.array([6.60557943e-07,   8.38015660e-06,   7.05996176e-05,
        #                5.12344075e-04,   3.50453676e-03,   2.44453624e-02,
        #                1.93782688e-01,   2.25936724e+00]),
        #      ),
        #     (5.75,
        #      np.array([9.44354234e-03,   4.45212136e-02,   1.72835877e-01,
        #                5.46749762e-01,   1.45597815e+00,   3.30040905e+00,
        #                6.30333260e+00,   9.74419729e+00]),
        #      np.array([6.31427920e-07,   7.63131191e-06,   6.25591461e-05,
        #                4.49619447e-04,   3.07929986e-03,   2.16823076e-02,
        #                1.74874928e-01,   2.09764087e+00]),
        #      ),
        #     (6.,
        #      np.array([0.0113067,  0.04898785,  0.18195408,  0.55939775,  1.46288372,
        #                3.28556791,  6.27896305,  9.86946446]),
        #      np.array([6.07125356e-07,   7.02153046e-06,   5.60375312e-05,
        #                3.98494081e-04,   2.72853912e-03,   1.93601976e-02,
        #                1.58544866e-01,   1.95149972e+00]),
        #      ),
        #     (6.25,
        #      np.array([0.01344308,  0.05382052,  0.19163668,  0.57302986,  1.47180585,
        #                3.2741163,  6.25548875,  9.97808294]),
        #      np.array([5.86478729e-07,   6.51723629e-06,   5.06751401e-05,
        #                3.56331345e-04,   2.43639735e-03,   1.73940780e-02,
        #                1.44372912e-01,   1.81933298e+00]),
        #      ),
        # ]

        self.fits = []
        for lo, hi, grid in fits:
            (s,a,v) = grid[0]
            K = len(a)
            # spline degree
            spline_k = 3
            if len(grid) <= 3:
                spline_k = 1
            amp_funcs = [InterpolatedUnivariateSpline(
                [ser for ser,amps,varr in grid],
                [amps[i] for ser,amps,varr in grid], k=spline_k)
                for i in range(K)]
            logvar_funcs = [InterpolatedUnivariateSpline(
                [ser for ser,amps,varr in grid],
                [np.log(varr[i]) for ser,amps,varr in grid], k=spline_k)
                for i in range(K)]
            self.fits.append((lo, hi, amp_funcs, logvar_funcs))
        (lo,hi,a,v) = self.fits[0]
        self.lowest = lo
        (lo,hi,a,v) = self.fits[-1]
        self.highest = hi

    def _getProfile(self, sindex):
        amp_funcs = logvar_funcs = None
        # clamp
        if sindex <= self.lowest:
            (lo,hi,a,v) = self.fits[0]
            amp_funcs = a
            logvar_funcs = v
        elif sindex >= self.highest:
            (lo,hi,a,v) = self.fits[-1]
            amp_funcs = a
            logvar_funcs = v
        else:
            for lo,hi,a,v in self.fits:
                if sindex >= lo and sindex <= hi:
                    amp_funcs = a
                    logvar_funcs = v
                    break
        
        amps = np.array([f(sindex) for f in amp_funcs])
        varr = np.exp(np.array([f(sindex) for f in logvar_funcs]))
        amps /= amps.sum()
        return mp.MixtureOfGaussians(amps, np.zeros((len(amps), 2)), varr)

class SersicIndex(ScalarParam):
    stepsize = 0.01


class SersicGalaxy(HoggGalaxy):
    nre = 8.

    @staticmethod
    def getNamedParams():
        return dict(pos=0, brightness=1, shape=2, sersicindex=3)

    def __init__(self, pos, brightness, shape, sersicindex, **kwargs):
        # super(SersicMultiParams.__init__(self, pos, brightness, shape, sersicindex)
        #self.name = self.getName()
        self.nre = SersicGalaxy.nre
        super(SersicGalaxy, self).__init__(pos, brightness, shape, sersicindex)
        #**kwargs)
        #self.sersicindex = sersicindex

    def __str__(self):
        return (super(SersicGalaxy, self).__str__() +
                ', Sersic index %.2f' % self.sersicindex.val)

    def getName(self):
        return 'SersicGalaxy'

    def getProfile(self):
        return SersicMixture.getProfile(self.sersicindex.val)

    def copy(self):
        return SersicGalaxy(self.pos.copy(), self.brightness.copy(),
                            self.shape.copy(), self.sersicindex.copy())

    def _getUnitFluxDeps(self, img, px, py):
        return hash(('unitpatch', self.getName(), px, py,
                     img.getWcs().hashkey(),
                     img.getPsf().hashkey(),
                     self.shape.hashkey(),
                     self.sersicindex.hashkey()))

    def getParamDerivatives(self, img, modelMask=None):
        # superclass produces derivatives wrt pos, brightness, and shape.
        derivs = super(SersicGalaxy, self).getParamDerivatives(
            img, modelMask=modelMask)

        pos0 = self.getPosition()
        (px0, py0) = img.getWcs().positionToPixel(pos0, self)
        patch0 = self.getUnitFluxModelPatch(img, px=px0, py=py0, modelMask=modelMask)
        if patch0 is None:
            derivs.append(None)
            return derivs
        counts = img.getPhotoCal().brightnessToCounts(self.brightness)

        # derivatives wrt Sersic index
        isteps = self.sersicindex.getStepSizes()
        if not self.isParamFrozen('sersicindex'):
            inames = self.sersicindex.getParamNames()
            oldvals = self.sersicindex.getParams()
            for i, istep in enumerate(isteps):
                oldval = self.sersicindex.setParam(i, oldvals[i] + istep)
                patchx = self.getUnitFluxModelPatch(
                    img, px=px0, py=py0, modelMask=modelMask)
                self.sersicindex.setParam(i, oldval)
                if patchx is None:
                    print('patchx is None:')
                    print('  ', self)
                    print('  stepping galaxy sersicindex',
                          self.sersicindex.getParamNames()[i])
                    print('  stepped', isteps[i])
                    print('  to', self.sersicindex.getParams()[i])
                    derivs.append(None)

                dx = (patchx - patch0) * (counts / istep)
                dx.setName('d(%s)/d(%s)' % (self.dname, inames[i]))
                derivs.append(dx)
        return derivs


if __name__ == '__main__':
    from basics import *
    from ellipses import *
    from astrometry.util.plotutils import PlotSequence
    import pylab as plt

    # mix = SersicMixture()
    # plt.clf()
    # for (n, amps, vars) in mix.fits:
    #     plt.loglog(vars, amps, 'b.-')
    #     plt.text(vars[0], amps[0], '%.2f' % n, ha='right', va='top')
    # plt.xlabel('Variance')
    # plt.ylabel('Amplitude')
    # plt.savefig('serfits.png')

    s = SersicGalaxy(PixPos(100., 100.),
                     Flux(1000.),
                     EllipseE(5., -0.5, 0.),
                     SersicIndex(2.5))
    print(s)
    print(s.getProfile())

    s.sersicindex.setValue(4.0)
    print(s.getProfile())

    d = DevGalaxy(s.pos, s.brightness, s.shape)
    print(d)
    print(d.getProfile())

    # Extrapolation!
    # s.sersicindex.setValue(0.5)
    # print s.getProfile()

    ps = PlotSequence('ser')

    # example PSF (from WISE W1 fit)
    w = np.array([0.77953706,  0.16022146,  0.06024237])
    mu = np.array([[-0.01826623, -0.01823262],
                   [-0.21878855, -0.0432496],
                   [-0.83365747, -0.13039277]])
    sigma = np.array([[[7.72925584e-01,   5.23305564e-02],
                       [5.23305564e-02,   8.89078473e-01]],
                      [[9.84585869e+00,   7.79378820e-01],
                       [7.79378820e-01,   8.84764455e+00]],
                      [[2.02664489e+02,  -8.16667434e-01],
                       [-8.16667434e-01,   1.87881670e+02]]])

    psf = GaussianMixturePSF(w, mu, sigma)

    data = np.zeros((200, 200))
    invvar = np.zeros_like(data)
    tim = Image(data=data, invvar=invvar, psf=psf)

    tractor = Tractor([tim], [s])

    nn = np.linspace(0.5, 5.5, 12)
    cols = int(np.ceil(np.sqrt(len(nn))))
    rows = int(np.ceil(len(nn) / float(cols)))

    xslices = []
    disable_galaxy_cache()

    plt.clf()
    for i, n in enumerate(nn):
        s.sersicindex.setValue(n)
        print(s.getParams())
        #print(s.getProfile())

        mod = tractor.getModelImage(0)

        plt.subplot(rows, cols, i + 1)
        #plt.imshow(np.log10(np.maximum(1e-16, mod)), interpolation='nearest',
        plt.imshow(mod, interpolation='nearest', origin='lower')
        plt.axis([50,150,50,150])
        plt.title('index %.2f' % n)

        xslices.append(mod[100,:])
    ps.savefig()

    plt.clf()
    for x in xslices:
        plt.plot(x, '-')
    ps.savefig()
