# Overview

Just for fun project about airfoil shape optimization with OpenFOAM and Bayesian optimization.
The code will be updated once in a while. The idea is the following:

- optimize airfoil geometries for subsonic flows (low Re & Ma)
- airfoils are parameterized using CST method
- Bayesian optimization is used to find the best parameters for given flow conditions
- the flow is solved with `simpleFoam` for now
- chord length is kept constant at $c = 0.15$ within the simulation, however, the chord length defined in the setup is used
to compute the Reynolds number accordingly
- the airfoil is optimized for a design range, which is specified within the setup dict
- the objective is the minimization of $c_D$ and $c_M$ (pitching moment) while maximizing $c_L$ for a given AoA $\alpha$

## Next steps / ideas / still TODO

1. improvement and generalization of BayesOpt routine, e.g. use batches instead of serial execution
2. transition model not working properly due to grid sensitivity -> deactivated for now
3. decrease mesh size to accelerate optimization
4. IO via YAML config file
5. validate modification of setup -> Re & Ma set correctly, ...
6. improvement of convergence behavior -> use DMD for that -> refer to test project steady DMD -> if new mesh isn't improving convergence behavoior
7. test different objective functions
8. replace meshing with [airfoil_meshing](https://github.com/AndreWeiner/airfoil_meshing) once that is implemented
9. maybe use wall function in case the grid is messed up 
10. avoid writing surface data for all time steps since steady state simulation -> how to set purgeWrite for surface sampling? 
11. validation of the numerical setup using NACA0012 standard benchmark case (grid convergence, ...)
12. extend for compressible flows and higher Re
13. therefore add extended CST from Seidler -> for transonic flows
14. refactoring main script (ongoing)
15. add checkpoints, logging, ... 
16. parallel execution, HPC support etc.
17. add BL suction and optimization of suction profil etc.
18. extend to 2.5D optimization of (swept) wings 
19. Documentation, unit tests, ...

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
