# How to setup parameter files
## Static topology simulation

Using the template from `examples/param/param_multi_robot_sim_1d_static_degradation.yml`, fill in the desire parameter values.
```yaml
---
numRobots: <INT> # total number of robots
flawedRobotRange: # number of robots with flawed assumed accuracy; each step in this range is run `numTrials` times
  min: <INT> # min number of flawed robots
  max: <INT> # max number of flawed robots
  incSteps: <INT> # number of steps from min to max inclusive
commsPeriod: 10 # in units of simulation steps
flawedSensorAccB: 0.75 # flawed assumed accuracy for black tile sensor
flawedSensorAccW: 0.75 # flawed assumed accuracy for white tile sensor
flawedSensorCovariance: 0 # (co-)variance of flawed assumed accuracy for both sensors (UNUSED)
correctSensorAccB: 0.95 # correct assumed accuracy for black tile sensor
correctSensorAccW: 0.95 # correct assumed accuracy for white tile sensor
targFillRatio: 0.55 # actual fill ratio of the environment
sensorFilterPeriod: 2.5e+2 # in units of simulation steps
numSteps: 1.0e+3 # number of steps (each observation is made per step)
numTrials: 2 # number of trials to repeat per case of # of flawed robots
fullyConnected: True # whether to use a fully connected network or select neighbors using a right-skewed binomial distribution (UNUSED)
method: "BRAVO" # sensor filter method ("ALPHA" = no adaptive estimation of sensor accuracy, "BRAVO" = with adaptive estimation of sensor accuracy)
filterSpecificParams:
  type_2_err_prob: 0.1 # applicable only for "BRAVO"
correctFilter: False # run the filter for robots that have the correct initial accuracy
...
```
Save the file with the name `param_multi_robot_sim_1d_static_degradation.yml` in the directory where you'll be executing the simulation.

## Dynamic topology simulation
The parameter file used for the dynamic simulation is the same as the configuration file used by ARGoS3, which is described in their [official documentation](https://www.argos-sim.info/user_manual.php). Here, only parameters specifically related to the simulated experiments will be discussed. You can find the template from `examples/param/param_multi_robot_sim_1d_static_degradation.argos`

### Number of steps
The value `length * ticks_per_second` becomes the number of steps for a single trial.
```xml
<!-- Duration of a single trial -->
<experiment length="500" ticks_per_second="10" random_seed="0" />
```

### KheperaIV static degradation controller
This is the controller that is used for experiments concerning static black-and-white tile environments. It is recommended that you use the absolute path for the controller library so that the execution location is flexible.

Most of the controller parameter can be left as is. You may be mostly concerned with parameter values related to the filter under the `<sensor_degradation_filter />` node.
```xml
<kheperaiv_diffusion_motion_controller id="kdmc"
            library="build/src/controllers/libsensor_degradation_filter_controllers">
    <actuators>
        <!-- Activate the differential steering actuator -->
        <differential_steering implementation="default" />

        <!-- Activate the RAB actuator -->
        <range_and_bearing implementation="default" />

        <!-- Activate the LED actuator -->
        <leds implementation="default" medium="leds" />
    </actuators>
    <sensors>

        <!-- Activate the ground sensors -->
        <kheperaiv_ground implementation="rot_z_only" />

        <!-- Activate the RAB sensor -->
        <range_and_bearing implementation="medium" medium="rab" show_rays="true"
            noise_std_dev="0" />

        <!-- Activate the proximity sensors -->
        <kheperaiv_proximity implementation="default" show_rays="false" />
    </sensors>
    <params>

        <!-- Diffusion motion parameters -->
        <diffusion go_straight_angle_range="-5:5" delta="0.1" />

        <!-- Ground sensor parameters -->
        <!--
            period_ticks: how many ticks between each observation
            sensor_acc_b: actual sensor accuracy (black tile) to simulate (only applies if sim=true in the static_degeradation_filter node)
            sensor_acc_w: actual sensor accuracy (white tile) to simulate (only applies if sim=true in the static_degeradation_filter node)
            sim: whether the experiment is using simulated or real ground sensors
            dynamic: whether the sensor accuracy dynamically changes over time (according to a Wiener process)
            true_deg_drift_coeff: drift coefficient of the sensor accuracy (applies only if dynamic="true")
            true_deg_diffusion_coeff: diffusion coefficient of the sensor accuracy (applies only if dynamic="true")
        -->
        <!-- Note: both sensor_acc_b and sensor_acc_w are used to parametrize the assumed accuracy of non-flawed robots, so they must still be set
            to valid values even if sim=false -->
        <ground_sensor
            period_ticks="1"
            sensor_acc_b="0.99"
            sensor_acc_w="0.99"
            sim="true"
            dynamic="true"
            true_deg_drift_coeff="-5e-5"
            true_deg_diffusion_coeff="1e-4"
        />

        <!-- Communication period in ticks -->
        <comms period_ticks="10" />

        <!-- Differential drive parameters -->
        <wheel_turning hard_turn_angle_threshold="90"
            soft_turn_angle_threshold="70"
            no_turn_angle_threshold="10"
            max_speed="10" /> <!-- speed in cm/s -->

        <!-- Static degradation filter parameters -->
        <!--
            method: filter type ("ALPHA" = no adaptive estimation of static sensor accuracy, "BRAVO" = with adaptive estimation of static sensor accuracy, "CHARLIE" = estimation of dynamic sensor accuracy)
            period_ticks: how many ticks between each (nominal) activation of the filter
            observation_queue_size: size of queue to store observations (to calculate variable n and t); set to 0 if not using queue (same effect as setting to 1 but more efficient)
        -->
        <sensor_degradation_filter method="ALPHA" period_ticks="1000" observation_queue_size="100">
            <!-- BRAVO-specific parameter for adaptive activation; only used if method="BRAVO" -->
            <!-- type_2_err_prob: type 2 error probability a.k.a. false negative rate -->
            <params type_2_err_prob="0.05" />

            <!-- CHARLIE-specific parameters for adaptive activation; only used if method="CHARLIER" -->
            <!--
                pred_deg_model_B: assumed drift coefficient used in prediction model
                pred_deg_variance_R: assumed *squared* diffusion coefficient (i.e., variance) used in the prediction model
                init_mean_MAP: initial guess for the surrogate distribution mean in the MAP estimation problem
                init_var_ELBO: initial guess for the surrogate distribution variance in the ELBO optimization problem
            -->
            <params
                pred_deg_model_B="-5e-5"
                pred_deg_variance_R="1e-4"
                init_mean_MAP="0.99"
                init_var_ELBO="0.001"
            />
        </sensor_degradation_filter>
    </params>
</kheperaiv_diffusion_motion_controller>
```

### Loop functions
Like the controller, it is recommended that you use the absolute path for the loop functions library so that the execution location is flexible.
```xml
<loop_functions
        library="build/src/loop_functions/libsensor_degradation_filter_loop_functions"
        label="sensor_deg_loop_functions">

    <!-- Number of trials to repeat -->
    <num_trials value="3" />

    <!-- Number of tiles for the arena in the x and y direction -->
    <!-- NOTE: must have equal number of tile counts -->
    <arena_tiles tile_count_x="500" tile_count_y="500" />

    <!-- Target fill ratio between 0.0 and 1.0 to generate in the arena -->
    <target_fill_ratio value="0.75" />

    <!-- Flawed robot parameters -->
    <!--
        num: number of flawed robots in the experiment
        acc_b: assumed sensor accuracy (black tile) of flawed robots
        acc_w: assumed sensor accuracy (white tile) of flawed robots
        activate_filter_for_all: whether to activate the filter for all robots or just those that have a flawed accuracy initially
    -->
    <!-- Note: both acc_b and acc_w are for flawed robots only; the assumed accuracies of non-flawed robots are set by the
        ground_sensor node in the controller node above -->
    <flawed_robots num="1" acc_b="0.75" acc_w="0.75" activate_filter_for_all="true" />

    <!-- Folder to store the output JSON data -->
    <path folder="data/temp" />

    <!-- Verbosity level ("full", "none") -->
    <verbosity level="full" /> <!-- "full", "none" -->

</loop_functions>
```

### Arena size and swarm density
The arena size can be modified as explained in the official ARGoS documentation. The effect it has on the generated tile size is described by the equation `arena_size_*/arena_tile_count_*` for both the x and y directions.

The swarm density is modified indirectly through the positions of the 4 walls that constrain the robots' movable space. Use the `compute_wall_positions` script (see [here](./utility_scripts_functions.md)) to obtain the appropriate values based on the desired swarm density.
```xml
<arena size="5, 5, 1" center="0,0,0.5">

    <!-- Method to generate the arena floor -->
    <floor id="floor" source="loop_functions" pixels_per_meter="200" />

    <!-- Place four boxes in a square to delimit the arena -->
    <box id="wall_north" size="10,0.1,0.5" movable="false">
        <body position="0,0.9273198961208501,0" orientation="0,0,0" />
    </box>
    <box id="wall_south" size="10,0.1,0.5" movable="false">
        <body position="0,-0.9273198961208501,0" orientation="0,0,0" />
    </box>
    <box id="wall_east" size="0.1,10,0.5" movable="false">
        <body position="0.9273198961208501,0,0" orientation="0,0,0" />
    </box>
    <box id="wall_west" size="0.1,10,0.5" movable="false">
        <body position="-0.9273198961208501,0,0" orientation="0,0,0" />
    </box>

    <distribute>

        <!-- Robot placement distributino -->
        <position method="uniform"
                  min="-0.9273198961208501,-0.9273198961208501,0"
                  max="0.9273198961208501,0.9273198961208501,0" />
        <orientation method="uniform" min="0,0,0" max="360,0,0" />

        <!-- Number of robots to be distributed -->
        <entity quantity="20" max_trials="100" base_num="0">
            <kheperaiv id="kiv" rab_data_size="50" rab_range="0.7">
                <controller config="kdmc" />
            </kheperaiv>
        </entity>

    </distribute>

</arena>
```