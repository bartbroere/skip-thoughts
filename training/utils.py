"""
Helper functions for skip-thoughts
"""
from collections import OrderedDict

import numpy
import six
import theano
import theano.tensor as tensor


def zipp(params, tparams):
    """
    Push parameters to Theano shared variables
    """
    if six.PY3:
        for kk, vv in params.items():
            tparams[kk].set_value(vv)
    if six.PY2:
        for kk, vv in params.items():
            tparams[kk].set_value(vv)


def unzip(zipped):
    """
    Pull parameters from Theano shared variables
    """
    new_params = OrderedDict()
    if six.PY3:
        for kk, vv in zipped.items():
            new_params[kk] = vv.get_value()
    if six.PY2:
        for kk, vv in zipped.iteritems():
            new_params[kk] = vv.get_value()
    return new_params


def itemlist(tparams):
    """
    Get the list of parameters. 
    Note that tparams must be OrderedDict
    """
    if six.PY2:
        return [vv for kk, vv in tparams.iteritems()]
    if six.PY3:
        return [vv for kk, vv in tparams.items()]


def _p(pp, name):
    """
    Make prefix-appended name
    """
    return '%s_%s'%(pp, name)


def init_tparams(params):
    """
    Initialize Theano shared variables according to the initial parameters
    """
    tparams = OrderedDict()
    if six.PY2:
        for kk, pp in params.iteritems():
            tparams[kk] = theano.shared(params[kk], name=kk)
    if six.PY3:
        for kk, pp in params.items():
            tparams[kk] = theano.shared(params[kk], name=kk)
    return tparams


def load_params(path, params):
    """
    Load parameters
    """
    pp = numpy.load(path)
    if six.PY3:
        for kk, vv in params.items():
            if kk not in pp:
                warnings.warn('%s is not in the archive'%kk)
                continue
            params[kk] = pp[kk]
    if six.PY2:
        for kk, vv in params.iteritems():
            if kk not in pp:
                warnings.warn('%s is not in the archive'%kk)
                continue
            params[kk] = pp[kk]
    return params


def ortho_weight(ndim):
    """
    Orthogonal weight init, for recurrent layers
    """
    W = numpy.random.randn(ndim, ndim)
    u, s, v = numpy.linalg.svd(W)
    return u.astype('float32')


def norm_weight(nin,nout=None, scale=0.1, ortho=True):
    """
    Uniform initalization from [-scale, scale]
    If matrix is square and ortho=True, use ortho instead
    """
    if nout == None:
        nout = nin
    if nout == nin and ortho:
        W = ortho_weight(nin)
    else:
        W = numpy.random.uniform(low=-scale, high=scale, size=(nin, nout))
    return W.astype('float32')


def tanh(x):
    """
    Tanh activation function
    """
    return tensor.tanh(x)


def linear(x):
    """
    Linear activation function
    """
    return x


def concatenate(tensor_list, axis=0):
    """
    Alternative implementation of `theano.tensor.concatenate`.
    """
    concat_size = sum(tt.shape[axis] for tt in tensor_list)

    output_shape = ()
    for k in range(axis):
        output_shape += (tensor_list[0].shape[k],)
    output_shape += (concat_size,)
    for k in range(axis + 1, tensor_list[0].ndim):
        output_shape += (tensor_list[0].shape[k],)

    out = tensor.zeros(output_shape)
    offset = 0
    for tt in tensor_list:
        indices = ()
        for k in range(axis):
            indices += (slice(None),)
        indices += (slice(offset, offset + tt.shape[axis]),)
        for k in range(axis + 1, tensor_list[0].ndim):
            indices += (slice(None),)

        out = tensor.set_subtensor(out[indices], tt)
        offset += tt.shape[axis]

    return out

