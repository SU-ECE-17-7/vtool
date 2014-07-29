#!/usr/bin/env python2.7
# This tests cython stuff not linalg stuff :P
from __future__ import absolute_import, division, print_function
import utool
import vtool
from vtool import keypoint as ktool
from vtool import linalg
import numpy as np

GLOBAL_SETUP = '''
import numpy as np
import numpy.linalg as npl
import vtool
'''


def _run_benchmark(setup_, func_list, argstr, number=1000):
    import timeit
    setup = GLOBAL_SETUP + '\n' + setup_
    print('----------')
    print('BENCHMARK: ' + utool.get_caller_name())
    for func in func_list:
        func_name = func if isinstance(func, str) else func.func_name
        print('Running: %s' % func_name)
        stmt = func_name + argstr
        try:
            total_time = timeit.timeit(stmt=stmt, setup=setup, number=number)
        except ImportError as ex:
            utool.printex(ex, iswarning=True)
        except Exception as ex:
            utool.printex(ex, iswarning=False)
            raise
        print(' * timed: %r seconds in %s' % (total_time, func_name))
    return locals()


def test_linalg():
    hist1 = np.random.rand(4, 2).astype(np.float32)
    hist2 = np.random.rand(4, 2).astype(np.float32)

    target = ((hist1 - hist2) ** 2).sum(-1)
    dist1 = vtool.linalg.L2_sqrd(hist1, hist2)
    dist2 = vtool.linalg.L2_sqrd_float32(hist1, hist2)

    print('target = %r' % (target,))
    print('dist1 = %r' % (dist1,))
    print('dist2 = %r' % (dist2,))

    assert np.all(target == dist1), 'someone screwed up the L2 distance func'
    assert np.allclose(dist2, dist1), 'cython version has diverged'
    return locals()


def test_invVR_det():
    invVRs = np.random.rand(4, 3, 3).astype(np.float64)

    out1 = ktool.get_invVR_mats_sqrd_scale(invVRs)
    out2 = ktool.get_invVR_mats_sqrd_scale_float64(invVRs)

    print('out1 = %r' % (out1,))
    print('out2 = %r' % (out2,))

    assert np.allclose(out1, out2), 'cython invV det version has diverged'
    return locals()


def test_det_dist():
    det1 = np.random.rand(100).astype(np.float64)
    det2 = np.random.rand(100).astype(np.float64)

    out1 = linalg.det_distance(det1, det2)
    out2 = linalg.det_distance_float64(det1, det2)

    print('out1 = %r' % (out1,))
    print('out2 = %r' % (out2,))

    assert np.allclose(out1, out2), 'cython invV det version has diverged'
    return locals()


def benchmark_det_dist():
    setup = utool.unindent(
        '''
        det1 = np.random.rand(100).astype(np.float64)
        det2 = np.random.rand(100).astype(np.float64)
        ''')
    func_list = [
        'vtool.linalg.det_distance',
        'vtool.linalg.det_distance_float64',
    ]
    argstr = '(det1, det2)'
    return _run_benchmark(setup, func_list, argstr)


def benchmark_invVR_det():
    setup = utool.unindent(
        '''
        import numpy as np
        import numpy.linalg as npl
        import vtool
        invVRs = np.random.rand(100, 3, 3).astype(np.float64)
        ''')
    func_list = [
        'vtool.keypoint.get_invVR_mats_sqrd_scale',
        'vtool.keypoint.get_invVR_mats_sqrd_scale_float64',
    ]
    argstr = '(invVRs)'
    return _run_benchmark(setup, func_list, argstr)


def benchmark_L2_dist():
    setup = utool.unindent(
        '''
        hist1 = np.random.rand(100, 128).astype(np.float32)
        hist2 = np.random.rand(100, 128).astype(np.float32)
        ''')
    func_list = [
        'vtool.linalg.L2_sqrd',
        'vtool.linalg.L2_sqrd_float32',
    ]
    argstr = '(hist1, hist2)'
    return _run_benchmark(setup, func_list, argstr)


if __name__ == '__main__':
    try:
        from vtool import linalg_cython  # NOQA
        print('[vtool] cython is on')
    except ImportError as ex:
        utool.printex(ex, iswarning=True)
        print('[vtool] cython is off')
        # raise
    #from vtool import linalg
    test_locals1 = utool.run_test(test_linalg)
    test_locals2 = utool.run_test(test_invVR_det)
    test_locals2 = utool.run_test(test_det_dist)
    benchmark_L2_dist()
    benchmark_invVR_det()
    benchmark_det_dist()
    #execstr = utool.execstr_dict(test_linalg, 'test_locals')
    #exec(execstr)