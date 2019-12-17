using StructJuMP
using StructJuMPSolverInterface

#using ParPipsNlpInterface

structJuMPSolve = ParPipsNlpInterface.structJuMPSolve

numScen = 2
m = StructuredModel(num_scenarios=numScen)
@variable(m, x[1:2])
@NLconstraint(m, x[1] + x[2] == 100)
@NLobjective(m, Min, x[1]^2 + x[2]^2 + x[1]*x[2])

for i in 1:numScen
    bl = StructuredModel(parent=m, id=i)
    @variable(bl, y[1:2])
    @NLconstraint(bl, x[1] + y[1] + y[2] ≥  0)
    @NLconstraint(bl, x[2] + y[1] + y[2] ≤ 50)
    @NLobjective(bl, Min, y[1]^2 + y[2]^2 + y[1]*y[2])
end

solve(solver="PipsNlp")
#structJuMPSolve(m)
