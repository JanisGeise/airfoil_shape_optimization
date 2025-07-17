# Overview

Just for fun project about airfoil shape optimization with OpenFOAM and Bayesian optimization.
The code will be updated once in a while. The idea is the following:

- optimize airfoil geometries for subsonic flows (low Re & Ma)
- airfoils are parameterized using CST method
- Bayesian optimization is used to find the best parameters for given flow conditions
- the flow is solved with `simpleFoam`
- the airfoil is optimized for a single design point, later this will be extended to a design range (compare section TODO)
- the obejctive is the minimization of $c_D$ and $c_M$ (pitching moment) while maximizing $c_L$ for a given AoA $\alpha$

## Next steps / ideas / still TODO

1. improvement and generalization of BayesOpt routine, script for executing validation simulation of best parameters
2. file manipulation to set the inflow and boundary conditions for the case (Ma, Re, $\rho$, Tu, ...) -> k, omega, ...
3. IO via YAML config file
4. check of user input 
5. exception handling regarding the meshing for weird airfoil shapes and crashed simulations 
6. parameterize meshing so that different chord length can be used 
7. maybe use wall function in case the grid is messed up 
8. maybe add rounding of LE and TE (in case bayesOpt isn't able to detect unsuitable AF shapes with sharp TE)
9. avoid writing surface data for all time steps since steady state simulation -> how to set purgeWrite for surface sampling? 
10. validation of the numerical setup using NACA0012 standard benchmark case (grid convergence, ...)
11. comparison kOmegaSST with and without transition modeling (since low Re)
12. extend design point to design range -> how to efficiently run $\alpha$ sweeps in OpenFOAM? -> initialize each new point with previous alpah 
13. extend for compressible flows and higher Re
14. refactoring (ongoing)
15. add checkpoints, logging, post-processing of optimization results, ... 
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
