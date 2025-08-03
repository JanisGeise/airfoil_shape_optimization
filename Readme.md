# Overview

Just for fun project about airfoil shape optimization with OpenFOAM and Bayesian optimization.
The code will be updated once in a while. The idea is the following:

- optimize airfoil geometries for subsonic flows (low Re & Ma)
- airfoils are parameterized using CST method
- Bayesian optimization is used to find the best parameters for given flow conditions
- the flow is solved with `simpleFoam`
- chord length is kept constant at $c = 0.15$ within the simulation, however, the chord length defined in the setup is used
to compute the Reynolds number accordingly
- the airfoil is optimized for a single design point, later this will be extended to a design range (compare section TODO)
- the objective is the minimization of $c_D$ and $c_M$ (pitching moment) while maximizing $c_L$ for a given AoA $\alpha$

## Next steps / ideas / still TODO

1. improvement and generalization of BayesOpt routine
2. IO via YAML config file
3. improvement of convergence behavior
4. replace meshing with [airfoil_meshing](https://github.com/AndreWeiner/airfoil_meshing) once that is implemented
5. check of user input 
6. maybe use wall function in case the grid is messed up 
7. maybe add rounding of LE and TE (in case bayesOpt isn't able to detect unsuitable AF shapes with sharp TE)
8. avoid writing surface data for all time steps since steady state simulation -> how to set purgeWrite for surface sampling? 
9. validation of the numerical setup using NACA0012 standard benchmark case (grid convergence, ...)
10. extend design point to design range -> how to efficiently run $\alpha$ sweeps in OpenFOAM? -> initialize each new point with previous alpha 
11. extend for compressible flows and higher Re
12. refactoring (ongoing)
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
