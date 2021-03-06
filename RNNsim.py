import numpy as np
from utils import seqs2cov

def simrnn(inputseqs, width, phi, varw, varu, varb, varv=1, seed=None):
    '''Samples a finite-width GP kernel of an RNN over input sequences `inputseqs`.
    A simple RNN with scalar output every time step evolves like

        s^t = phi(W s^{t-1} + U x^{t} + b)
        y^t = <v, s^t>

    where

        x^t is the input at time t
        s^t is the state of the RNN at time t
        W is the state-to-state weight matrix
        U is the input-to-state weight matrix
        b is the bias
        v is the readout weight
        y^t is the output at time t

    If n is the number of neurons and x^t has dimension m, and

        W_{pq} ~ N(0, varw / n)
        U_{pq} ~ N(0, varu / m)
        b_p ~ N(0, varb)
        v_p ~ N(0, varv / n)

    then all outputs of an RNN over all time steps and all input sequences
    are jointly Gaussian in the limit as n -> infinity.
    This Gaussian distribution has dimension

        \sum_seq length(seq)

    This function approximates the kernel of this Gaussian by
    instantiating a finite width RNN.

    Inputs:
        inputseqs: a list of sequences of vectors
            Each element of `inputseqs` is a matrix with size
                seqlen x vectordim
        width: number of hidden units; equals n above
        phi: activation function
        varw: variance of state-to-state weigts
        varu: variance of input-to-state weights
        varb: variance of biases
        seed: random seed
    Outputs:
        the empirical covariance of (y^t) over all input sequences
        and all t.
        This matrix has a block structure, where the first diagonal
        block is the autocovariance of y^t generated from the 1st sequence,
        the second diagonal is that of the 2nd sequence, etc.
    '''
    if seed is not None:
        np.random.seed(seed)
    inpdim = len(inputseqs[0][0])
    maxlength = max([len(s) for s in inputseqs])
    W = np.random.randn(width, width) * np.sqrt(varw) / np.sqrt(width)
    U = np.random.randn(width, inpdim) * np.sqrt(varu) / np.sqrt(inpdim)
    b = np.random.randn(width) * np.sqrt(varb)
    ss = []
    for seq in inputseqs:
        tildeh = 0
        for x in seq:
            x = np.array(x)
            h = tildeh + U @ x + b
            s = phi(h)
            ss.append(s)
            tildeh = W @ s
    return varv * seqs2cov(ss)