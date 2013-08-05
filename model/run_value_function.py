from __future__ import division

import pickle

from helpers import load_params, ss_wage_flexible
from joblib import Parallel, delayed
import numpy as np

from gen_interp import Interp
from value_function import get_rigid_output, g_p, iter_bellman


def iter_bellman_wrapper(pi):
    """
    Call this from a joblib Parallel like.

    Parameters
    ----------

    pi: inflation rate.  This will need to be abstracted to any argument.
        Or even a dict of arguments!

    Returns
    -------
    None:  Does have side effects.
    """
    params = load_params()
    grid = params['grid'][0]
    v = Interp(grid, -grid + 29)
    Tv, ws, rest = iter_bellman(
        v, tol=0.005, strict=False, log=False, params=params, pi=pi)
    res_dict = {'Tv': Tv, 'ws': ws, 'rest': rest}

    # full_df = pd.DataFrame({'vfs': vfs, 'wss': wss,
                            # 'rests': rests, 'wss': wss})
    # full_df.to_csv('results/vf_results' + str(pi) + '.csv')

    #--------------------------------------------------------------------------
    gp, flex_ws = get_wage_distribution(params)
    res_dict['gp'] = gp
    rigid_out = get_rigid_output(params, ws, flex_ws, gp)
    res_dict['rigid_out'] = rigid_out
    write_results(res_dict, pi)
    pass


def get_wage_distribution(params):
    shock = params['shock'][0]
    grid = params['grid'][0]
    # fine_grid = params['fine_grid'][0]
    g0 = Interp(grid, grid/4, kind='pchip')
    gp = g_p(g0, params['ln_dist'][0], params)
    flex_ws = Interp(shock, ss_wage_flexible(params, shock=shock))
    return gp, flex_ws


def write_results(res_dict, pi):
    """
    Handle the file writing of iter_bellman.

    Parameters
    ----------
    """
    piname = str(pi).replace('.', '')
    with open('results/vf_' + piname + '.pkl', 'w') as f:
        pickle.dump(res_dict['Tv'], f)
    with open('results/ws_' + piname + '.pkl', 'w') as f:
        pickle.dump(res_dict['ws'], f)
    with open('results/gp_' + piname + '.pkl', 'w') as f:
        pickle.dump(res_dict['gp'], f)
    with open('results/rigid_output_' + piname + '_.txt', 'w') as f:
        f.write(str(res_dict['rigid_out']))
    res_dict['rest'].to_hdf('results/results_' + piname + '.h5',
                            'pi_' + piname)
    print('Added results for {}'.format(pi))

if __name__ == '__main__':
    params = load_params()
    pi_low = params['pi_low'][0]
    pi_high = params['pi_high'][0]
    pi_n = params['pi_n'][0]

    pi_grid = np.linspace(pi_low, pi_high, pi_n)
    Parallel(n_jobs=-1)(delayed(iter_bellman_wrapper)(pi) for pi in pi_grid)
