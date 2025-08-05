# Overview

Just for fun project about airfoil shape optimization with OpenFOAM and Bayesian optimization.
The code will be updated once in a while. The idea is the following:

- optimize airfoil geometries for subsonic flows (low Re & Ma)
- airfoils are parameterized using CST method
- Bayesian optimization is used to find the best parameters for given flow conditions
- the flow is solved with `simpleFoam`
- chord length is kept constant at $c = 0.15$ within the simulation, however, the chord length defined in the setup is used
to compute the Reynolds number accordingly
- the airfoil is optimized for a design range, which is specified within the setup dict
- the objective is the minimization of $c_D$ and $c_M$ (pitching moment) while maximizing $c_L$ for a given AoA $\alpha$

## Next steps / ideas / still TODO

1. improvement and generalization of BayesOpt routine
2. check if initialization works -> initial residual in Time = 1 still 1 and simulation approx same time
2. decrease mesh size to accelerate optimization
3. IO via YAML config file
4. improvement of convergence behavior
5. test different objective functions
6. replace meshing with [airfoil_meshing](https://github.com/AndreWeiner/airfoil_meshing) once that is implemented
7. maybe use wall function in case the grid is messed up 
8. maybe add rounding of LE and TE (in case bayesOpt isn't able to detect unsuitable AF shapes with sharp TE)
9. avoid writing surface data for all time steps since steady state simulation -> how to set purgeWrite for surface sampling? 
10. validation of the numerical setup using NACA0012 standard benchmark case (grid convergence, ...)
11. extend for compressible flows and higher Re
12. refactoring main script (ongoing)
13. add checkpoints, logging, ... 
14. parallel execution, HPC support etc.

...

## References

### GitHub repositories
- numerical setup adopted from the [buffet_oat15](https://github.com/JanisGeise/buffet_oat15/tree/jgeise) repository
- Bayesian optimization adopted from [BayesOpt_solverSettings](https://github.com/JanisGeise/BayesOpt_solverSettings) repository
- execution of OpenFOAM inspired by [drlfoam](https://github.com/OFDataCommittee/drlfoam) repository

### Literature

CST method:
- Kulfan, Brenda. (2008). *Universal Parametric Geometry Representation Method*. Journal of Aircraft - J AIRCRAFT. 45. 142-158. 10.2514/1.29958

computation of camber line & other:
- Schlichting, H. and Truckenbrodt, E.: *Aerodynamik des Flugzeuges*. 3rd ed. Vol. 1. Berlin, Heidelberg: Springer Berlin Heidelberg, 2001. doi: 10.1007/978-3-642-56911-1
