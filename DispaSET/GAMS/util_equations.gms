*===============================================================================
*Declaration and definition of equations
*   NOTE: not all equations are used in the programs which reference to this file
*===============================================================================
EQUATIONS
EQ_Objective_function
EQ_CHP_extraction_Pmax
EQ_CHP_extraction
EQ_CHP_backpressure
EQ_CHP_demand_satisfaction
EQ_CHP_max_heat
EQ_Heat_Storage_balance
EQ_Heat_Storage_minimum
EQ_Heat_Storage_level
EQ_Commitment
EQ_MinUpTime
EQ_MinDownTime
EQ_RampUp_TC
EQ_RampDown_TC
EQ_CostStartUp
EQ_CostShutDown
EQ_CostRampUp
EQ_CostRampDown
EQ_Demand_balance_DA
EQ_Demand_balance_2U
EQ_Demand_balance_3U
EQ_Demand_balance_2D
EQ_Power_must_run
EQ_Power_available
EQ_Reserve_2U_capability
EQ_Reserve_2D_capability
EQ_Reserve_3U_capability
EQ_Storage_minimum
EQ_Storage_level
EQ_Storage_input
EQ_Storage_MaxDischarge
EQ_Storage_MaxCharge
EQ_Storage_balance
EQ_Storage_boundaries
EQ_SystemCost
EQ_Emission_limits
EQ_Flow_limits_lower
EQ_Flow_limits_upper
EQ_Force_Commitment
EQ_Force_DeCommitment
EQ_LoadShedding
EQ_Generation_Delta_Cap
EQ_Power_available_Cap
EQ_Committed_Cap
EQ_Startup_Cap
EQ_Shutdown_Cap
$If %RetrieveStatus% == 1 EQ_CommittedCalc

;

$If %RetrieveStatus% == 0 $goto skipequation

EQ_CommittedCalc(u,z)..
         Committed(u,z)
         =E=
         CommittedCalc(u,z)
;

$label skipequation

*Objective function


$ifthen %LPFormulation% == 1
EQ_SystemCost(i)..
         SystemCost(i)
         =E=
(         sum(u,CostFixed(u)*Committed(u,i)*PowerCapacity(u))* 1/8760
         +sum(u,CostRampUpH(u,i) + CostRampDownH(u,i))
         +sum(u,(CostVariable(u,i) ) * Power(u,i))
         +sum((u,n), Power(u,i)*EmissionRate(u,'CO2')*Location(u,n)) * 6
         +sum(l,PriceTransmission(l,i)*Flow(l,i))
         +sum(n,CostLoadShedding(n,i)*ShedLoad(n,i))
         +sum(chp, CostHeatSlack(chp,i) * HeatSlack(chp,i))
         +sum(chp, CostVariable(chp,i) * CHPPowerLossFactor(chp) * Heat(chp,i))
         +100E3*(sum(n,LL_MaxPower(n,i)+LL_MinPower(n,i)))
         +80E3*(sum(n,LL_2U(n,i)+LL_2D(n,i)+LL_3U(n,i)))
         +70E3*sum(u,LL_RampUp(u,i)+LL_RampDown(u,i))
         +1*sum(s,spillage(s,i))
         + sum(uc, Expanded(uc) * C_inv(uc)*PowerCapacity(uc)* 1/8760)
)/1E6

;
$else

EQ_SystemCost(i)..
         SystemCost(i)
         =E=
(         sum(u,CostFixed(u)*Committed(u,i)*PowerCapacity(u))* 1/8760
         +sum(u,CostStartUpH(u,i) + CostShutDownH(u,i))
         +sum(u,CostRampUpH(u,i) + CostRampDownH(u,i))
         +sum(u,CostVariable(u,i) * Power(u,i))
         +sum(l,PriceTransmission(l,i)*Flow(l,i))
         +sum(n,CostLoadShedding(n,i)*ShedLoad(n,i))
         +sum(chp, CostHeatSlack(chp,i) * HeatSlack(chp,i))
         +sum(chp, CostVariable(chp,i) * CHPPowerLossFactor(chp) * Heat(chp,i))
         +100E3*(sum(n,LL_MaxPower(n,i)+LL_MinPower(n,i)))
         +80E3*(sum(n,LL_2U(n,i)+LL_2D(n,i)+LL_3U(n,i)))
         +70E3*sum(u,LL_RampUp(u,i)+LL_RampDown(u,i))
         +1*sum(s,spillage(s,i))
         + sum(uc, Expanded(uc) * C_inv(uc)*PowerCapacity(uc)* 1/8760)
)/1E6
;
$endIf
;

EQ_Objective_function..
         SystemCostD
         =E=
         sum(i,SystemCost(i))
;

* 3 binary commitment status
EQ_Commitment(u,i)..
         Committed(u,i)-CommittedInitial(u)$(ord(i) = 1)-Committed(u,i-1)$(ord(i) > 1)
         =E=
         StartUp(u,i) - ShutDown(u,i)
;

* minimum up time
EQ_MinUpTime(u,i)..
         sum(ii_$( (ord(ii_) >= ord(i) - TimeUpMinimum(u)) and (ord(ii_) <= ord(i)) ), StartUp(u,ii_))
         + sum(h$( (ord(h) >= FirstHour + ord(i) - TimeUpMinimum(u) -1) and (ord(h) < FirstHour)),StartUp.L(u,h))
         =L=
         Committed(u,i)
;

* minimum down time
EQ_MinDownTime(u,i)..
         sum(ii_$( (ord(ii_) >= ord(i) - TimeDownMinimum(u)) and (ord(ii_) <= ord(i)) ), ShutDown(u,ii_))
         + sum(h$( (ord(h) >= FirstHour + ord(i) - TimeDownMinimum(u) -1) and (ord(h) < FirstHour)),ShutDown.L(u,h))
         =L=
         Nunits(u)-Committed(u,i)
;

* ramp up constraints
EQ_RampUp_TC(u,i)$(sum(tr,Technology(u,tr))=0)..
         - Power(u,i-1)$(ord(i) > 1) - PowerInitial(u)$(ord(i) = 1) + Power(u,i)
         =L=
         (Committed(u,i) - StartUp(u,i)) * RampUpMaximum(u) + RampStartUpMaximumH(u,i) * StartUp(u,i) - PowerMustRun(u,i) * ShutDown(u,i) + LL_RampUp(u,i)
;

* ramp down constraints
EQ_RampDown_TC(u,i)$(sum(tr,Technology(u,tr))=0)..
         Power(u,i-1)$(ord(i) > 1) + PowerInitial(u)$(ord(i) = 1) - Power(u,i)
         =L=
         (Committed(u,i) - StartUp(u,i)) * RampDownMaximum(u) + RampShutDownMaximumH(u,i) * ShutDown(u,i) - PowerMustRun(u,i) * StartUp(u,i) + LL_RampDown(u,i)
;

* Start up cost
EQ_CostStartUp(u,i)$(CostStartUp(u) <> 0)..
         CostStartUpH(u,i)
         =E=
         CostStartUp(u)*StartUp(u,i)
;

* Start up cost
EQ_CostShutDown(u,i)$(CostShutDown(u) <> 0)..
         CostShutDownH(u,i)
         =E=
         CostShutDown(u)*ShutDown(u,i)
;

EQ_CostRampUp(u,i)$(CostRampUp(u) <> 0)..
         CostRampUpH(u,i)
         =G=
         CostRampUp(u)*(Power(u,i)-PowerInitial(u)$(ord(i) = 1)-Power(u,i-1)$(ord(i) > 1))
;

EQ_CostRampDown(u,i)$(CostRampDown(u) <> 0)..
         CostRampDownH(u,i)
         =G=
         CostRampDown(u)*(PowerInitial(u)$(ord(i) = 1)+Power(u,i-1)$(ord(i) > 1)-Power(u,i))
;

*Hourly demand balance in the day-ahead market for each node
EQ_Demand_balance_DA(n,i)..
         sum(u,Power(u,i)*Location(u,n))
          +sum(l,Flow(l,i)*LineNode(l,n))
         =E=
         Demand("DA",n,i)
         +sum(s,StorageInput(s,i)*Location(s,n))
         -ShedLoad(n,i)
         -LL_MaxPower(n,i)
         +LL_MinPower(n,i)
;

*Hourly demand balance in the upwards spinning reserve market for each node
EQ_Demand_balance_2U(n,i)..
         sum((u,t),Reserve_2U(u,i)*Technology(u,t)*Reserve(t)*Location(u,n))
         =G=
         +Demand("2U",n,i)*(1-K_QuickStart(n))
         -LL_2U(n,i)
;

*Hourly demand balance in the upwards non-spinning reserve market for each node
EQ_Demand_balance_3U(n,i)..
         sum((u,t),(Reserve_2U(u,i) + Reserve_3U(u,i) )*Technology(u,t)*Reserve(t)*Location(u,n))
         =G=
         +Demand("2U",n,i)
         -LL_3U(n,i)
;

*Hourly demand balance in the downwards reserve market for each node
EQ_Demand_balance_2D(n,i)..
         sum((u,t),Reserve_2D(u,i)*Technology(u,t)*Reserve(t)*Location(u,n))
         =G=
         Demand("2D",n,i)
         -LL_2D(n,i)
;

EQ_Reserve_2U_capability(u,i)..
         Reserve_2U(u,i)
         =L=
         PowerCapacity(u)*LoadMaximum(u,i)*Committed(u,i) - Power(u,i)
;

EQ_Reserve_2D_capability(u,i)..
         Reserve_2D(u,i)
         =L=
         (Power(u,i) - PowerMustRun(u,i) * Committed(u,i)) + (StorageChargingCapacity(u)*Nunits(u)-StorageInput(u,i))$(s(u))
;

EQ_Reserve_3U_capability(u,i)$(QuickStartPower(u,i) > 0)..
         Reserve_3U(u,i)
         =L=
         (Nunits(u)-Committed(u,i))*QuickStartPower(u,i)
;

*Minimum power output is above the must-run output level for each unit in all periods
EQ_Power_must_run(u,i)..
         PowerMustRun(u,i) * Committed(u,i) - (StorageInput(u,i) * CHPPowerLossFactor(u) )$(chp(u) and (CHPType(u,'Extraction') or CHPType(u,'P2H')))
         =L=
         Power(u,i)
;

*Maximum power output is below the available capacity
EQ_Power_available(u,i)..
         Power(u,i)
         =L=
         PowerCapacity(u)*LoadMaximum(u,i)*Committed(u,i)
;

**** CAPACITY EXPANSION (Redundant)
EQ_Power_available_Cap(uc,i)..
        Power(uc,i)
        =L=
        Expanded(uc)*PowerCapacity(uc)*LoadMaximum(uc,i);

**** CAPACITY EXPANSION
EQ_Committed_Cap(uc,i)..
        Committed(uc,i)
        =L=
        Expanded(uc);

**** CAPACITY EXPANSION
EQ_Startup_Cap(uc,i)..
        StartUp(uc,i)
        =L=
        Committed(uc,i);

**** CAPACITY EXPANSION
EQ_Shutdown_Cap(uc,i)..
        ShutDown(uc,i)
        =L=
        Committed(uc, i);

*Storage level must be above a minimum
EQ_Storage_minimum(s,i)..
         StorageMinimum(s)* Nunits(s)
         =L=
         StorageLevel(s,i)
;

*Storage level must below storage capacity
EQ_Storage_level(s,i)..
         StorageLevel(s,i)
         =L=
         StorageCapacity(s)*AvailabilityFactor(s,i)*Nunits(s)
;

* Storage charging is bounded by the maximum capacity
EQ_Storage_input(s,i)..
         StorageInput(s,i)
         =L=
         StorageChargingCapacity(s)*(Nunits(s)-Committed(s,i))
;
* The system could curtail by pumping and turbining at the same time if Nunits>1. This should be included into the curtailment equation!

*Discharge is limited by the storage level
EQ_Storage_MaxDischarge(s,i)..
         Power(s,i)/(max(StorageDischargeEfficiency(s),0.0001))
         +StorageOutflow(s,i)*Nunits(s) +Spillage(s,i) - StorageInflow(s,i)*Nunits(s)
         =L=
         StorageLevel(s,i)
;

*Charging is limited by the remaining storage capacity
EQ_Storage_MaxCharge(s,i)..
         StorageInput(s,i) * StorageChargingEfficiency(s)
         -StorageOutflow(s,i)*Nunits(s) -spillage(s,i) + StorageInflow(s,i)*Nunits(s)
         =L=
         StorageCapacity(s)*AvailabilityFactor(s,i)*Nunits(s) - StorageLevel(s,i)
;

*Storage balance
EQ_Storage_balance(s,i)..
         StorageInitial(s)$(ord(i) = 1)
         +StorageLevel(s,i-1)$(ord(i) > 1)
*         +StorageLevelH(h--1,s)
         +StorageInflow(s,i)*Nunits(s)
         +StorageInput(s,i)*StorageChargingEfficiency(s)
         =E=
         StorageLevel(s,i)
         +StorageOutflow(s,i)*Nunits(s)
         +spillage(s,i)
         +Power(s,i)/(max(StorageDischargeEfficiency(s),0.0001))

;

* Minimum level at the end of the optimization horizon:
EQ_Storage_boundaries(s,i)$(ord(i) = card(i))..
         StorageFinalMin(s)
         =L=
         StorageLevel(s,i)
;

*Total emissions are capped
EQ_Emission_limits(n,i,p)..
         sum(u,Power(u,i)*EmissionRate(u,p)*Location(u,n))
         =L=
         EmissionMaximum(n,p)
;

*Flows are above minimum values
EQ_Flow_limits_lower(l,i)..
         FlowMinimum(l,i)
         =L=
         Flow(l,i)
;

*Flows are below maximum values
EQ_Flow_limits_upper(l,i)..
         Flow(l,i)
         =L=
         FlowMaximum(l,i)
;

*Force Unit commitment/decommitment:
* E.g: renewable units with AF>0 must be committed
EQ_Force_Commitment(u,i)$((sum(tr,Technology(u,tr))>=1 and LoadMaximum(u,i)>0))..
         Committed(u,i)
         =G=
         1;

* E.g: renewable units with AF=0 must be decommitted
EQ_Force_DeCommitment(u,i)$(LoadMaximum(u,i)=0)..
         Committed(u,i)
         =E=
         0;

*Load shedding
EQ_LoadShedding(n,i)..
         ShedLoad(n,i)
         =L=
         LoadShedding(n,i)
;

* CHP units:
EQ_CHP_extraction(chp,i)$(CHPType(chp,'Extraction'))..
         Power(chp,i)
         =G=
         StorageInput(chp,i) * CHPPowerToHeat(chp)
;

EQ_CHP_extraction_Pmax(chp,i)$(CHPType(chp,'Extraction') or CHPType(chp,'P2H'))..
         Power(chp,i)
         =L=
         PowerCapacity(chp)*Nunits(chp)  - StorageInput(chp,i) * CHPPowerLossFactor(chp)
;

EQ_CHP_backpressure(chp,i)$(CHPType(chp,'Back-Pressure'))..
         Power(chp,i)
         =E=
         StorageInput(chp,i) * CHPPowerToHeat(chp)
;

EQ_CHP_max_heat(chp,i)..
         StorageInput(chp,i)
         =L=
         CHPMaxHeat(chp)*Nunits(chp)
;

EQ_CHP_demand_satisfaction(chp,i)..
         Heat(chp,i) + HeatSlack(chp,i)
         =E=
         HeatDemand(chp,i)
;

*Heat Storage balance
EQ_Heat_Storage_balance(chp,i)..
          StorageInitial(chp)$(ord(i) = 1)
         +StorageLevel(chp,i-1)$(ord(i) > 1)
         +StorageInput(chp,i)
         =E=
         StorageLevel(chp,i)
         +Heat(chp,i) + StorageSelfDischarge(chp) * StorageLevel(chp,i)/24
;
* The self-discharge proportional to the charging level is a bold hypothesis, but it avoids keeping self-discharging if the level reaches zero

*Storage level must be above a minimum
EQ_Heat_Storage_minimum(chp,i)..
         StorageMinimum(chp)*Nunits(chp)
         =L=
         StorageLevel(chp,i)
;


*Storage level must below storage capacity
EQ_Heat_Storage_level(chp,i)..
         StorageLevel(chp,i)
         =L=
         StorageCapacity(chp)*Nunits(chp)
;
