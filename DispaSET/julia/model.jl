using JuMP
using Parameters # used as syntactic sugar for assign multiple values
using NamedArrays
using PyCall
using Gurobi



# TODO
### 1) Rolling Horizon
### 2) MIP Formulation
### 3) Missing equations
### 4) Output

LPFormulation = 1

### Pickle #TODO
include("load_pickle.jl") # include some helpers to from pickle
include("utils.jl") # helper functions for syntactical sugar

###### convention
# set is defined by single capital letter ::Array
# parameters are indexed by direct set name ::NamedArry or in 1d ::Dictionary
#
filepath = "Inputs_year.p"
InputDict = myunpickle(filepath)

#### GDX #TODO

## Sets
#h = InputDict["sets"]["h"]     # Hours
#mk = InputDict["sets"]["mk"]   # Market
#p = InputDict["sets"]["p"]     # Pollutant
#n = InputDict["sets"]["n"]     # Nodes
#l = InputDict["sets"]["l"]     # Lines
#f = InputDict["sets"]["f"]     # Fuel types
#u = InputDict["sets"]["u"]     # units
#t = InputDict["sets"]["t"]     # Generation technologies
#s = InputDict["sets"]["s"]     # Storage Unit (with reservoir)
#tr = InputDict["sets"]["tr"]   # Renewable generation technologies
#chp = InputDict["sets"]["chp"]


# naming convention: element ∈ SET
sets = Dict{Symbol,Array{String}}(Symbol(uppercase(k)) => v for (k,v) in InputDict["sets"])
#n = map(x -> sets[Symbol(uppercase(x))], a)

#a_set = InputDict["parameters"]["CostShutDown"]["sets"]
#a_val = InputDict["parameters"]["CostShutDown"]["val"]
#a_set = map(x -> sets[Symbol(uppercase(x))], a_set)
#NamedArray(a_val, a_set)

### Create named parameters using Namedarrays
parameters =  Dict{Symbol,Any}()
for (k,v) in InputDict["parameters"]
        #println(typeof(v["val"][1]))
        if length(v["val"])>0
                if (typeof(v["val"][1]) == PyObject)
                        val = convert(Array{Float64},v["val"])
                        #println(val)
                else
                        val = v["val"]
                end
                parameters[Symbol(k)] = NamedArray(val, map(x -> sets[Symbol(uppercase(x))], v["sets"]))
        else
                ### empty parm
                sets_ = map(x -> sets[Symbol(uppercase(x))], v["sets"])
                sets_dim = tuple(map(x -> length(x), sets_)...)
                #parameters[Symbol(k)] = NamedArray(zeros(sets_dim), sets_)
                parameters[Symbol(k)] = missing
        end
end


#Value assignment
#@unpack h, mk, n, p, l, f, u, t, s, tr, chp = sets
@unpack H, MK, N, P, L, F, U, T, S, TR, CHP = sets

H = map(x -> parse(Int,x), H)


## Load parameters
@unpack AvailabilityFactor, CostFixed, CostLoadShedding, CostRampDown, CostRampUp,
        CostShutDown, CostStartUp, CostVariable, Demand, Efficiency, EmissionMaximum, EmissionRate,
        FlowMaximum, FlowMinimum, FuelPrice, Fuel, LineNode, LoadShedding, Location, OutageFactor,
        PartLoadMin, PowerCapacity, PowerInitial, PriceTransmission, StorageChargingCapacity,
        StorageChargingEfficiency, RampDownMaximum, RampShutDownMaximum, RampStartUpMaximum, RampUpMaximum,
        Reserve, StorageCapacity, StorageDischargeEfficiency, StorageInflow, StorageInitial, StorageMinimum,
        StorageOutflow, Technology, TimeUpMinimum, TimeDownMinimum, PowerInitial, Nunits, CHPPowerLossFactor,
        CHPType, Config = parameters



tech = Dict()
for (rowindex, row) in enumerate(axes(Technology.array,1))
        tech_index = findfirst(Technology.array[row, :]) ## Assumption -> only one technology per unit
        tech[names(Technology)[1][rowindex]] = names(Technology)[2][tech_index]
end


Uᴿ = [u for u in U if tech[u] ∈ TR] # Renewables
Uᶜ = [u for u in U if tech[u] ∉ TR] # Nonrenewables

Uˢ = filter(x -> !(x in S), U) # units without storages
H⁺  = H[H .> 1] # h>1
H₀ = H[H .== 1] # h=1


# TODO Think about better Data Structure/Override indexing

#### Parameter definitions

# CommittedInitial = Dict(U .=> 0)
CommittedInitial = NamedArray(zeros(length(U)), ([U]))
CommittedInitial[PowerInitial .> 0] .= 1

PowerMinStable = PartLoadMin.*PowerCapacity;
LoadMaximum= AvailabilityFactor.*(1 .- OutageFactor)

filtered_QSP = RampStartUpMaximum.>PowerMinStable*4

QuickStartPower = NamedArray(zeros(length(U), length(H)), (U,H))
QuickStartPower[filtered_QSP,:] = PowerCapacity[filtered_QSP] .* LoadMaximum[filtered_QSP,:]

RampStartUpMaximumH = min.(PowerCapacity .* LoadMaximum, max.(RampStartUpMaximum,PowerMinStable,QuickStartPower));
RampStartUpMaximumH = NamedArray(RampStartUpMaximumH, (U,H))
RampShutDownMaximumH = min.(PowerCapacity.*LoadMaximum, max.(RampShutDownMaximum,PowerMinStable));
RampShutDownMaximumH = NamedArray(RampShutDownMaximumH, (U,H))

PowerMustRun = PowerMinStable.*LoadMaximum
PowerMustRun = NamedArray(PowerMustRun, (U, H))
PowerMustRun[Uᴿ,:] = PowerCapacity[Uᴿ] .* LoadMaximum[Uᴿ,:]

K_QuickStart = Dict(n => 0.5 for n in N)



StorageFinalMin = Dict(S .=> 0)

if CHPType === missing
        CHP_extraction = Array([])
else
        CHP_extraction = CHP[CHPType == "Extraction"]
end


###### Commitment

# TODO 2 Adapt config
ValueOfLostLoad = 1E9
CostSpillage = 1E9



# function model()


#
# macro if_lp(expr)
#         if LPFormulation==1
#                 return expr
#         else
#                 return 0
#         end
# end
#
# function if_lp(expr)
#
#         if LPFormulation==1
#                 return JuMP.parseExpr(expr)
#         else
#                 return 0
#         end
# end
#
# b = 3
# if_lp(:(2+2))
#
#
#
LPFormulation=1


############################## Model definition
m = Model()


@variables m begin
        CostRampUpH[U, H]            >= 0
        CostRampDownH[U, H]          >= 0
        Power[U, H]                  >= 0
        Flow[L, H]                   >= 0
        ShedLoad[N, H]               >= 0
        HeatSlack[U, H]              >= 0
        Heat[CHP, H]                 >= 0
        CostShutDownH[U,H]           >= 0
        CurtailedPower[N,H]          >= 0
        PowerMaximum[U,H]            >= 0
        PowerMinimum[U,H]            >= 0
        StorageInput[U,H]            >= 0
        StorageLevel[U,H]            >= 0
        CostStartUpH[U,H]            >= 0
        LL_MaxPower[N,H]             >= 0
        LL_RampUp[U,H]               >= 0
        LL_RampDown[U,H]             >= 0
        LL_MinPower[N,H]             >= 0
        LL_2U[N,H]                   >= 0
        LL_3U[N,H]                   >= 0
        LL_2D[N,H]                   >= 0
        spillage[S,H]                >= 0
        Reserve_2U[U, H]             >= 0
        Reserve_2D[U,H]              >= 0
        Reserve_3U[U,H]              >= 0
        StartUp[U,H]                 >= 0
        ShutDown[U,H]                >= 0
        WaterSlack[S]                >= 0
        SystemCost[H]                >= 0

        0 <= Committed[U, H]         <= 1
end

############################ Model formulation
#### Minimize
@objective(m, Min, sum(SystemCost[h] for h in H))






@constraint(m, EQ_SystemCost[h in H],
                SystemCost[h]
                ==
                sum(CostFixed[u]*Committed[u,h] for u in U)
                + sum(CostRampUpH[u,h] + CostRampDownH[u,h] for u in U)
                + sum(CostVariable[u,h] * Power[u,h] for u in U)
                + sum(PriceTransmission[l,h] * Flow[l,h] for l in L)
                + sum(CostLoadShedding[n,h] * ShedLoad[n,h] for n in N)
                + sum(CostHeatSlack[chp,h] * HeatSlack[chp,h] for chp in CHP)
                + sum(CostVariable[chp,h] * CHPPowerLossFactor[chp] * Heat[chp,h] for chp in CHP)
                #+ if_lp(:(sum(CostStartUpH[u,h] + CostShutDownH[u,h] for u in U)))
#Config("ValueOfLostLoad","val")
                + ValueOfLostLoad*(sum(LL_MaxPower[n,h]+LL_MinPower[n,h] for n in N))
                +0.8*ValueOfLostLoad*(sum(LL_2U[n,h]+LL_2D[n,h]+LL_3U[n,h] for n in N))
                +0.7*ValueOfLostLoad*sum(LL_RampUp[u,h]+LL_RampDown[u,h] for u in U)
                +CostSpillage*sum(spillage[s,h] for s in S)
                )


#### Subject to

# @constraint(m, EQ_Commitment[u in U, h in H],
#                 Committed[u, h] - start_value_parameter(h, Committed, CommittedInitial, u)
#                 ==
#                 StartUp[u, h] - ShutDown[u, h])

@constraint(m, EQ_Commitment_initial[u in U, h in H₀],
                Committed[u, h] - CommittedInitial[u] == StartUp[u, h] - ShutDown[u, h])



@constraint(m, EQ_Commitment[u in U, h in H⁺],
                Committed[u, h] - Committed[u, h-1] == StartUp[u, h] - ShutDown[u, h])



@constraint(m, Test[u in U, h in H₀],
        Committed[u, h] == CommittedInitial[u])




# TODO
# @constraint(m, EQ_MinUpTime[u in U, h in H],
#                     sum( - TimeUpMinimum[u] -  for u ∈ U for t ∈ T)
#                     <=
#                     Committed[u, h]

# TODO
# @constraint(m, EQ_MinDownTime[u in U, h in H],


###### Ramping

@constraint(m, EQ_RampUp_TC[u in Uᶜ, h in H⁺],
                -Power[u,h-1] + Power[u,h]
                <=
                (Committed[u,h] - StartUp[u,h]) * RampUpMaximum[u] + RampStartUpMaximumH[u,h] * StartUp[u,h] -
                        PowerMustRun[u,h] * ShutDown[u,h] + LL_RampUp[u,h] )

@constraint(m, EQ_RampUp_TC_initial[u in Uᶜ, h in H₀],
                -PowerInitial[u] + Power[u,h]
                <=
                (Committed[u,h] - StartUp[u,h]) * RampUpMaximum[u] + RampStartUpMaximumH[u,h] * StartUp[u,h] -
                        PowerMustRun[u,h] * ShutDown[u,h] + LL_RampUp[u,h] )

@constraint(m, EQ_RampDown_TC[u in Uᶜ, h in H⁺],
                -Power[u,h-1] + Power[u,h]
                <=
                (Committed[u,h] - StartUp[u,h]) * RampDownMaximum[u] + RampShutDownMaximumH[u,h] * ShutDown[u,h] -
                        PowerMustRun[u,h] * StartUp[u,h] + LL_RampDown[u,h] )

@constraint(m, EQ_RampDown_TC_initial[u in Uᶜ, h in H₀],
                -PowerInitial[u] + Power[u,h]
                <=
                (Committed[u,h] - StartUp[u,h]) * RampDownMaximum[u] + RampShutDownMaximumH[u,h] * ShutDown[u,h] -
                        PowerMustRun[u,h] * StartUp[u,h] + LL_RampDown[u,h] )


# ###### Costs
# @constraint(m, EQ_CostStartUp[u in U[CostStartUp.>0], h in H],
#                 CostStartUpH[u, h] == CostStartUp[u]*StartUp[u, h])
#
#
# @constraint(m, EQ_CostShutDown[u in U[CostShutDown.>0], h in H],
#                 CostShutDownH[u, h] == CostShutDown[u]*ShutDown[u, h])
#
#
#
# @constraint(m, EQ_CostRampUp_FirstHour[u in U[CostRampUp.>0], h in H₀],
#                 CostRampUpH >= CostRampUp[u]*(Power[u,h]-PowerInitial)  )
#
# @constraint(m, EQ_CostRampUp[u in U[CostRampUp.>0], h in H⁺],
#                 CostRampUpH >= CostRampUp[u]*(Power[u,h]-Power[u,h-1])  )
#


@constraint(m, EQ_CostRampDown_FirstHour[u in U[CostRampDown.>0], h in H₀],
                CostRampDownH >= CostRampDown[u]*(PowerInitial-Power[u,h])  )

@constraint(m, EQ_CostRampDown[u in U[CostRampDown.>0], h in H⁺],
                CostRampDownH >= CostRampDown[u]*(Power[u,h-1]-Power[u,h])  )


## Demand balances
@constraint(m, EQ_Demand_balance_DA[n in N, h in H],
                sum(Power[u,h]*Location[u,n] for u ∈ U)
                +sum(Flow[l,h]*LineNode[l,n] for l ∈ L)
                ==
                Demand["DA",n,h]
                +sum(StorageInput[s,h]*Location[s,n] for s ∈ S)
                -ShedLoad[n,h]
                -LL_MaxPower[n,h]
                +LL_MinPower[n,h] )

@constraint(m, EQ_Demand_balance_2U[n in N, h in H],
                sum(Reserve_2U[u,h]*Technology[u,t]*Reserve[t]*Location[u,n] for u ∈ U for t ∈ T)
                 >=
                 +Demand["2U",n,h]*(1-K_QuickStart[n])
                 -LL_2U[n,h] )

#Hourly demand balance in the upwards non-spinning reserve market for each node
@constraint(m, EQ_Demand_balance_3U[n in N, i in H],
                    sum((Reserve_2U[u,i] + Reserve_3U[u,i])*Technology[u,t]*Reserve[t]*Location[u,n]
                        for u ∈ U for t ∈ T)
                    >=
                    +Demand["2U",n,i]
                    -LL_3U[n,i] )

#Hourly demand balance in the downwards reserve market for each node
@constraint(m, EQ_Demand_balance_2D[n in N, h in H],
              sum(Reserve_2D[u,h]*Technology[u,t]*Reserve[t]*Location[u,n] for u ∈ U for t ∈ T)
              >=
              +Demand["2D",n,h]
              -LL_2D[n,h] )

################################# Reserves

@constraint(m, EQ_Reserve_2U_capability[u in U, h in H],
                Reserve_2U[u,h]
                <=
                PowerCapacity[u]*LoadMaximum[u,h]*Committed[u,h] - Power[u,h] )

@constraint(m, EQ_Reserve_2D_capability[u in U, h in H; !(u in S)],
                Reserve_2D[u,h]
                <=
                (Power[u,h] - PowerMustRun[u,h] * Committed[u,h]) )

@constraint(m, EQ_Reserve_2D_capability_storages[u in S, h in H],
                Reserve_2D[u,h]
                <=
                (Power[u,h] - PowerMustRun[u,h] * Committed[u,h]) + (StorageChargingCapacity[u]*Nunits[u]-StorageInput[u,h]) )



@constraint(m, EQ_Reserve_3U_capability[u in U, h in H; QuickStartPower[u,h]>0],
                Reserve_3U[u,h]
                <=
                (Nunits[u]-Committed[u,h])*QuickStartPower[u,h] )



H_old = H

H = H[1:24*1]
H⁺  = H[H .> 1] # h>1
H₀ = H[H .== 1] # h=1

H⁺ = H⁺[1:24*1-1]



# TODO
#Minimum power output is above the must-run output level for each unit in all periods
@constraint(m, EQ_Power_must_run[u in U, i in H],
                PowerMustRun[u,i] * Committed[u,i] -
                cond(CHP_extraction,"StorageInput[u,i] * CHPPowerLossFactor[u] ")
                <=
                Power[u,i] )

#Maximum power output is below the available capacity
@constraint(m, EQ_Power_available[u in U, h in H],
                Power[u,h]
                <=
                PowerCapacity[u]*LoadMaximum[u,h]*Committed[u,h] )



@constraint(m, EQ_Storage_level[s in S, h in H],
                StorageLevel[s,h]
                <=
                StorageCapacity[s]*AvailabilityFactor[s,h]*Nunits[s] )

@constraint(m, EQ_Storage_input[s in S, h in H],
                StorageInput[s,h]
                <=
                StorageChargingCapacity[s]*(Nunits[s]-Committed[s,h]) )


@constraint(m, EQ_Storage_MaxDischarge[s in S, h in H],
                (Power[s,h] / (max(StorageDischargeEfficiency[s], 0.0001))) + StorageOutflow[s,h]*Nunits[s]
                + spillage[s,h] - StorageInflow[s,h]*Nunits[s]
                <=
                StorageLevel[s,h]
                )

@constraint(m, EQ_Storage_MaxCharge[s in S, h in H],
                StorageInput[s,h] * StorageChargingEfficiency[s] - StorageOutflow[s,h]*Nunits[s]
                - spillage[s,h] + StorageInflow[s,h] * Nunits[s]
                <=
                StorageCapacity[s] * AvailabilityFactor[s,h] * Nunits[s] - StorageLevel[s,h]
                )



@constraint(m, EQ_Storage_balance[s in S, h in H],
                start_value_parameter(h, StorageLevel, StorageInitial, s)
                + StorageInflow[s,h]*Nunits[s]
                + StorageInput[s,h] * StorageChargingEfficiency[s]
                ==
                StorageLevel[s, h] + StorageOutflow[s,h] * Nunits[s]
                + spillage[s,h]
                + Power[s,h] / (max(StorageDischargeEfficiency[s], 0.0001))
                )

@constraint(m, EQ_Storage_boundaries[s in S, h in H[end]],
                StorageFinalMin[s]
                <=
                StorageLevel[s,h] + WaterSlack[s]
                )

@constraint(m, EQ_Emission_limits[n in N, h in H, p in P],
                sum(Power[u,h]*EmissionRate[u,p]*Location[u,n] for u ∈ U)
                <=
                EmissionMaximum[n,p]
                )


@constraint(m, EQ_Flow_limits_lower[l in L, h in H],
                FlowMinimum[l, h]
                <=
                Flow[l,h]
                )



@constraint(m, EQ_Flow_limits_upper[l in L, h in H],
                Flow[l, h]
                <=
                FlowMaximum[l,h]
                )


@constraint(m, EQ_Force_Commitment[u in Uᴿ, h in H; LoadMaximum[u,h]>0],
                Committed[u, h]
                >=
                1
                )



@constraint(m, EQ_Force_DeCommitment[u in U, h in H; LoadMaximum[u,h]==0],
                Committed[u, h]
                ==
                0
                )

@constraint(m, EQ_LoadShedding[n in N, h in H],
                ShedLoad[n, h]
                <=
                LoadShedding[n,h]
                )

@constraint(m, EQ_CHP_extraction[chp in CHP_extraction, h in H],
                Power[chp,h]
                >=
                StorageInput[chp,h]*CHPPowerToHeat[chp]
                )


# TODO
@constraint(m, EQ_CHP_extraction_Pmax[chp in CHP_extraction, h in H],
                Power[chp,h]
                <=
                StorageInput[chp,h]*CHPPowerToHeat[chp]
                )

                # EQ_CHP_extraction_Pmax(chp,i)$(CHPType(chp,'Extraction') or CHPType(chp,'P2H'))..
                #          Power(chp,i)
                #          =L=
                #          PowerCapacity(chp)*Nunits(chp)  - StorageInput(chp,i) * CHPPowerLossFactor(chp)

# TODO
@constraint(m, EQ_CHP_backpressure[chp in CHP_extraction, h in H],
                Power[chp,h]
                ==
                StorageInput[chp,h]*CHPPowerToHeat[chp]
                )


@constraint(m, EQ_CHP_max_heat[chp in CHP, h in H],
                StorageInput[chp,h]
                <=
                CHPMaxHeat[chp]*Nunits[chp]
                )


@constraint(m, EQ_CHP_demand_satisfaction[chp in CHP, h in H],
                Heat[chp,h] + HeatSlack[chp,h]
                ==
                HeatDemand[chp,h]
                )


@constraint(m, EQ_Heat_Storage_balance[chp in CHP, h in H₀],
                StorageInitial[chp] +  StorageInput
                ==
                StorageLevel[chp,h] + Heat[chp,h] + StorageSelfDischarge[chp]* StorageLevel[chp,h]/24
                )


@constraint(m, EQ_Heat_Storage_balance_First_hour[chp in CHP, h in H⁺],
                StorageLevel[chp, h-1] +  StorageInput
                ==
                StorageLevel[chp,h] + Heat[chp,h] + StorageSelfDischarge[chp]* StorageLevel[chp,h]/24
                )

@constraint(m, EQ_Heat_Storage_minimum[chp in CHP, h in H],
                StorageMinimum[chp] * Nunits[chp]
                <=
                StorageLevel[chp,h]
                )

@constraint(m, EQ_Heat_Storage_level[chp in CHP, h in H],
                StorageLevel[chp,h]
                <=
                StorageCapacity[chp]*Nunits[chp]
                )


@constraint(m, EQ_Heat_Storage_boundaries[chp in CHP, h in H[end]],
                StorageFinalMin[chp]
                <=
                StorageLevel[chp,h]
                )


m


optimize!(m, with_optimizer(Gurobi.Optimizer))
