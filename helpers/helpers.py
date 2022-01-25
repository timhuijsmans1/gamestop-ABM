def utility_function(w_t, s_t, pi_t, momentum_change, p_momentum=.75, p_contrarian=.25):
    contrarian_change = -1 * momentum_change / 2

    momentum_expectation = pi_t + momentum_change
    contrarian_expectation = pi_t + contrarian_change
    # > 0 means price increase @ P=75%, thus large chance of loss
    if momentum_change > 0:
        loss = abs((w_t - s_t * pi_t) - (w_t - s_t * momentum_expectation))
        gain = abs((w_t - s_t * pi_t) - (w_t - s_t * contrarian_expectation))
        p_loss = p_momentum
        p_gain = p_contrarian

    # < 0 means price decrease @ P=75%, thus large chance of gain
    if momentum_change < 0:
        loss = abs((w_t - s_t * pi_t) - (w_t - s_t * contrarian_expectation))
        gain = abs((w_t - s_t * pi_t) - (w_t - s_t * momentum_expectation))
        p_loss = p_contrarian
        p_gain = p_momentum

    utility_gamble = -p_loss * 2.55 * (loss) ** .88 + p_gain * (gain) ** 3

    return utility_gamble