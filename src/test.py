tests1 = { 'atravesar': 'atrabesar', 'después': 'despues', 'enlace':
    'enlaze elace enlase', 'account': 'acount', ...}

tests2 = {'forbidden': 'forbiden', 'decisions': 'deciscions descisions',
    'supposedly': 'supposidly', 'embellishing': 'embelishing', ...}

def spelltest(tests, bias=None, verbose=False):
    import time
    n, bad, unknown, start = 0, 0, 0, time.clock()
    if bias:
        for target in tests: NWORDS[target] += bias
    for target,wrongs in tests.items():
        for wrong in wrongs.split():
            n += 1
            w = correct(wrong)
            if w!=target:
                bad += 1
                unknown += (target not in NWORDS)
                if verbose:
                    print '%r => %r (%d); expected %r (%d)' % (
                        wrong, w, NWORDS[w], target, NWORDS[target])
    return dict(bad=bad, n=n, bias=bias, pct=int(100. - 100.*bad/n), 
                unknown=unknown, secs=int(time.clock()-start) )

print spelltest(tests1)
print spelltest(tests2) ## only do this after everything is debugged
