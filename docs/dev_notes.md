# Dev notes
- The dynamic topology static deg (DTSD) experiment is run by using the `kheperaiv_diffusion_motion_controller` and the `sensor_degradation_filter_loop_functions` libraries.
- In simulation, the assumed accuracy of a robot (if it's supposed to have a different one from its actual accuracy) is set in the `<loop_functions>` node. This is because:
    - we can't control --- at least not easily --- which robots are flawed and which aren't if we assign the values using the controller,
    - if we want to use the same controller for real robots, we can technically cross-compile specific robots to have flawed assumed accuracies, but using loop functions is way more streamlined
    - the actual accuracy of the robot is set in the `<controllers>` node because it applies to all the robots.

- The `StaticDegradationAlpha` class refers to the static degradation filter without adaptive activation. The results from using this filter is available but not included in the paper.
- The `StaticDegradationBravo` class refers to the ASDF filter; it's simply `StaticDegradationAlpha` with the activation mechanism. The paper "_Adaptive Self-Calibration for Minimalistic Collective Perception using Imperfect Robot Swarms_" discusses the proposal of this filter.
- The `DynamicDegradationCharlie` class refers to the dynamic degradation filter that does posterior approximation using pure vanilla VI. What this means is that the distribution family is fixed and we optimize the ELBO for the distribution parameters.
    - The degradation model is assumed to follow a Wiener process with drift $\eta$ and variance $\sigma^2$:

        $x(t) = x(0) + \eta t + \sigma W(t)$ where $W(t)$ is the standard Wiener process (a.k.a. standard Brownian motion).

    - Thus the prediction model used in this filter is as follows.

        ```cpp
        x_pred[k+1] = x_pos[k] + B * (k+1 - k); \\ predicted mean with assumed drift of B
        var_pred[k+1] = var_pos[k] + R; \\ predicted variance with assumed diffusion variance of R
        ```
    - The observations `n` can be kept in a queue (since it's non-stationary). What this means is that the past `N` observations are kept in this queue. If an observation queue is used then the fill ratio reference used by the binomial likelihood (_i.e._, the informed estimate) is computed as a weighted average of past `N` informed estimates.

- The `tests/test_elbo_class.cpp` script is provided to test the GSL integration functionality and NLopt optimization functionality.