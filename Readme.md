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
2. `mapFields` not working properly -> revise
3. transition model not working properly due to grid sensitivity -> deactivated for now
4. decrease mesh size to accelerate optimization
5. IO via YAML config file
6. improvement of convergence behavior -> use DMD for that -> refer to test project steady DMD
7. test different objective functions
8. replace meshing with [airfoil_meshing](https://github.com/AndreWeiner/airfoil_meshing) once that is implemented
9. maybe use wall function in case the grid is messed up 
10. maybe add rounding of LE and TE (in case bayesOpt isn't able to detect unsuitable AF shapes with sharp TE)
11. avoid writing surface data for all time steps since steady state simulation -> how to set purgeWrite for surface sampling? 
12. validation of the numerical setup using NACA0012 standard benchmark case (grid convergence, ...)
13. extend for compressible flows and higher Re
14. refactoring main script (ongoing)
15. add checkpoints, logging, ... 
16. parallel execution, HPC support etc.

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
