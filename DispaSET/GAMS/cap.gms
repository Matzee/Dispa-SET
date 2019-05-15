$Title UCM model

$eolcom //
Option threads=8;
Option IterLim=1000000000;
Option ResLim = 10000000000;
*Option optca=0.0;

$setglobal filepath '/projects/p_kraftwerk/';
$setglobal filepath 'Test/';
$setglobal inputname 'Inputs_clusteredYear.gdx';
$setglobal outputname 'cap.gdx';

scalar time_total;
scalar start_program;
start_program = jnow;

// Reduce .lst file size

// Turn off the listing of the input file
$offlisting
$offlog

// Turn off the listing and cross-reference of the symbols used
$offsymxref offsymlist

option
    limrow = 0,     // equations listed per block
    limcol = 0,     // variables listed per block
    solprint = off,     // solver's solution output printed
    sysout = off;       // solver's system output printed

$onecho > CPLEX.opt
     scaind -1
     simdisplay 1
$offecho


* Whole time horizon




*===============================================================================
*Definition of the dataset-related options
*===============================================================================

* Print results to excel files (0 for no, 1 for yes)
$set Verbose 0

* Set debug mode. !! This breaks the loop and requires a debug.gdx file !!
* (0 for no, 1 for yes)
$set Debug 0

* Print results to excel files (0 for no, 1 for yes)
$set PrintResults 0

* Name of the input file (Ideally, stick to the default Input.gdx)
*$set InputFileName Input.gdx
$set InputFileName %filepath%%inputname%

* Definition of the equations that will be present in LP or MIP
* (1 for LP 0 for MIP TC)
$setglobal LPFormulation 1
* Flag to retrieve status or not
* (1 to retrieve 0 to not)
$setglobal RetrieveStatus 0

*===============================================================================
* Model formulation
*===============================================================================


*============= Define sets, parametrs and variables ==================================================================

$include utils_sets_pars_vars.gms


*===============================================================================
*Assignment of initial values
*===============================================================================

******************** NOTE: The following variables are only valid for the plants which are not Expanded
************************** The other variabels are restricted by the upper bounds of the corresponding VARIABLES
*************************** this guarantees feasibility to the cost of worse interpretability (the parameter of uc should be looked carefully)


*Initial commitment status
CommittedInitial(u)=0;
CommittedInitial(u)$(PowerInitial(u)>0)=1;

* Definition of the minimum stable load:
PowerMinStable(u) = PartLoadMin(u)*PowerCapacity(u);

LoadMaximum(u,h) = AvailabilityFactor(u,h)*(1-OutageFactor(u,h));

* parameters for clustered formulation (quickstart is defined as the capability to go to minimum power in 15 min)
QuickStartPower(u,h) = 0;
QuickStartPower(u,h)$(RampStartUpMaximum(u)>=PowerMinStable(u)*4) = PowerCapacity(u)*LoadMaximum(u,h);
RampStartUpMaximumH(u,h) = min(PowerCapacity(u)*LoadMaximum(u,h),max(RampStartUpMaximum(u),PowerMinStable(u),QuickStartPower(u,h)));
RampShutDownMaximumH(u,h) = min(PowerCapacity(u)*LoadMaximum(u,h),max(RampShutDownMaximum(u),PowerMinStable(u)));

PowerMustRun(u,h)=PowerMinStable(u)*LoadMaximum(u,h);
PowerMustRun(u,h)$(sum(tr,Technology(u,tr))>=1 and smin(n,Location(u,n)*(1-Curtailment(n)))=1) = PowerCapacity(u)*LoadMaximum(u,h);

* Part of the reserve that can be provided by offline quickstart units:
K_QuickStart(n) = 0.5;

intrate_investment  = 0.1;
Expanded.up(uc) = 1;

* Investment unit: EUR/kW, model unit MW -> 1/1/1000=01
C_inv(uc) = ((intrate_investment*(1+intrate_investment)**EconomicLifetime(uc))
                /((1+intrate_investment)**EconomicLifetime(uc)-1))*Investment(uc);


loop(n,
* Heuristic: Use maximum power capacity as the twice mean daily load -> Should always be much higher than upper bound but scales better for small countries
* For Germany for example each capacity is higher than 1E5, a small country like denmark it is only 8E3
  PowerCapacity(uc)$(Location(uc, n)) = floor(sum(h, Demand('DA', n,h))/(card(h))*2);
);
PowerCapacity(uc) = 1E5;

$If %Verbose% == 1 Display RampStartUpMaximum, RampShutDownMaximum, CommittedInitial;

$offorder

*===============================================================================
*Declaration and definition of equations
*===============================================================================
$include util_equations.gms


* Minimum level at the end of the optimization horizon:
*EQ_Heat_Storage_boundaries(chp,i)$(ord(i) = card(i))..
*         StorageFinalMin(chp)
*         =L=
*         StorageLevel(chp,i)
*;
*===============================================================================
*Definition of models
*===============================================================================

MODEL UCM_SIMPLE /
*EQ_Power_available_Cap,
EQ_Committed_Cap,
*$If %CEPFormulation% == 1 EQ_Power_available_Cap,
*$If %CEPFormulation% == 1 EQ_Committed_Cap,
EQ_Objective_function,
EQ_CHP_extraction_Pmax,
EQ_CHP_extraction,
EQ_CHP_backpressure,
EQ_CHP_demand_satisfaction,
EQ_CHP_max_heat,
EQ_CostRampUp,
EQ_CostRampDown,
EQ_Commitment,
EQ_RampUp_TC,
EQ_RampDown_TC,
EQ_Demand_balance_DA,
EQ_Demand_balance_2U,
EQ_Demand_balance_2D,
EQ_Demand_balance_3U,
EQ_Power_available,
EQ_Heat_Storage_balance,
EQ_Heat_Storage_minimum,
EQ_Heat_Storage_level,
EQ_Reserve_2U_capability,
EQ_Reserve_2D_capability,
EQ_Reserve_3U_capability,
EQ_Storage_minimum,
EQ_Storage_level,
EQ_Storage_input,
EQ_Storage_balance,
EQ_Storage_boundaries,
EQ_Storage_MaxCharge
EQ_Storage_MaxDischarge
EQ_SystemCost
*EQ_Emission_limits,
EQ_Flow_limits_lower,
EQ_Flow_limits_upper,
EQ_Force_Commitment,
EQ_Force_DeCommitment,
EQ_LoadShedding,
EQ_Startup_Cap,
EQ_Shutdown_Cap
$If %RetrieveStatus% == 1 EQ_CommittedCalc
/

;
UCM_SIMPLE.optcr = 0.00  ;
*UCM_SIMPLE.optfile=1;

*===============================================================================
*Solving loop
*===============================================================================

ndays = floor(card(h)/24);
if (Config("RollingHorizon LookAhead","day") > ndays -1, abort "The look ahead period is longer than the simulation length";);

* Some parameters used for debugging:
failed=0;
parameter CommittedInitial_dbg(u), PowerInitial_dbg(u), StorageInitial_dbg(s);

* Fixing the initial guesses:
*PowerH.L(u,i)=PowerInitial(u);
*Committed.L(u,i)=CommittedInitial(u);

* Defining a parameter that records the solver status:
set  tmp   "tpm"  / "model", "solver" /  ;
parameter status(tmp,h);

$if %Debug% == 1 $goto DebugSection


scalar starttime;
set days /1,'ndays'/;
display days;
PARAMETER elapsed(days);
PARAMETER Expanded_power(uc, h);

$include util_scaling.gms
UCM_SIMPLE.scaleopt = 1;

* No model generation time despite model generation time of CAP >> Benders Deecomp
scalar solve_time;
scalar start_time;
start_time = jnow;


* Only for test cases! !!!!!!!!!!!!!!!!!!!!!!! CAPACITY EXPANSION ON A ROLLING HORION DOES NOT MAKE ANY SENSE!
$setglobal RollingHorizon 0
$ifthen %RollingHorizon% == 1
* ***************************** ROLLING HORIZON **************************************************
FOR(day = 1 TO ndays-Config("RollingHorizon d","day") by Config("RollingHorizon Length","day"),
         FirstHour = (day-1)*24+1;
         LastHour = min(card(h),FirstHour + (Config("RollingHorizon Length","day")+Config("RollingHorizon d","day")) * 24 - 1);
         LastKeptHour = LastHour - Config("RollingHorizon LookAhead","day") * 24;
         i(h) = no;
         i(h)$(ord(h)>=firsthour and ord(h)<=lasthour)=yes;
         display day,FirstHour,LastHour,LastKeptHour;

*        Defining the minimum level at the end of the horizon, ensuring that it is feasible with the provided inflows:
         StorageFinalMin(s) =  min(StorageInitial(s) + (sum(i,StorageInflow(s,i)) - sum(i,StorageOutflow(s,i)))*Nunits(s), sum(i$(ord(i)=card(i)),StorageProfile(s,i)*Nunits(s)*StorageCapacity(s)*AvailabilityFactor(s,i)));
*        Correcting the minimum level to avoid the infeasibility in case it is too close to the StorageCapacity:
         StorageFinalMin(s) = min(StorageFinalMin(s),Nunits(s)*StorageCapacity(s) - Nunits(s)*smax(i,StorageInflow(s,i)));

$If %Verbose% == 1   Display PowerInitial,CommittedInitial,StorageFinalMin;

SOLVE UCM_SIMPLE USING LP MINIMIZING SystemCostD;

$If %Verbose% == 0 $goto skipdisplay2
$If %LPFormulation% == 1          Display EQ_Objective_function.M, EQ_CostRampUp.M, EQ_CostRampDown.M, EQ_Demand_balance_DA.M, EQ_Storage_minimum.M, EQ_Storage_level.M, EQ_Storage_input.M, EQ_Storage_balance.M, EQ_Storage_boundaries.M, EQ_Storage_MaxCharge.M, EQ_Storage_MaxDischarge.M, EQ_Flow_limits_lower.M ;
$If not %LPFormulation% == 1      Display EQ_Objective_function.M, EQ_CostStartUp.M, EQ_CostShutDown.M, EQ_Commitment.M, EQ_MinUpTime.M, EQ_MinDownTime.M, EQ_RampUp_TC.M, EQ_RampDown_TC.M, EQ_Demand_balance_DA.M, EQ_Demand_balance_2U.M, EQ_Demand_balance_2D.M, EQ_Demand_balance_3U.M, EQ_Reserve_2U_capability.M, EQ_Reserve_2D_capability.M, EQ_Reserve_3U_capability.M, EQ_Power_must_run.M, EQ_Power_available.M, EQ_Storage_minimum.M, EQ_Storage_level.M, EQ_Storage_input.M, EQ_Storage_balance.M, EQ_Storage_boundaries.M, EQ_Storage_MaxCharge.M, EQ_Storage_MaxDischarge.M, EQ_SystemCost.M, EQ_Flow_limits_lower.M, EQ_Flow_limits_upper.M, EQ_Force_Commitment.M, EQ_Force_DeCommitment.M, EQ_LoadShedding.M ;
$label skipdisplay2

         status("model",i) = UCM_SIMPLE.Modelstat;
         status("solver",i) = UCM_SIMPLE.Solvestat;

if(UCM_SIMPLE.Modelstat <> 1 and UCM_SIMPLE.Modelstat <> 8 and not failed, CommittedInitial_dbg(u) = CommittedInitial(u); PowerInitial_dbg(u) = PowerInitial(u); StorageInitial_dbg(s) = StorageInitial(s);
                                                                           EXECUTE_UNLOAD "debug.gdx" day, status, CommittedInitial_dbg, PowerInitial_dbg, StorageInitial_dbg;
                                                                           failed=1;);

         CommittedInitial(u)=sum(i$(ord(i)=LastKeptHour-FirstHour+1),Committed.L(u,i));
         PowerInitial(u) = sum(i$(ord(i)=LastKeptHour-FirstHour+1),Power.L(u,i));

         StorageInitial(s) =   sum(i$(ord(i)=LastKeptHour-FirstHour+1),StorageLevel.L(s,i));
         StorageInitial(chp) =   sum(i$(ord(i)=LastKeptHour-FirstHour+1),StorageLevel.L(chp,i));
         Expanded_power(uc, i) = Expanded.L(uc);

*Loop variables to display after solving:
$If %Verbose% == 1 Display LastKeptHour,PowerInitial,CostStartUpH.L,CostShutDownH.L,CostRampUpH.L;

);

        CurtailedPower.L(n,z)=sum(u,(Nunits(u)*PowerCapacity(u)*LoadMaximum(u,z)-Power.L(u,z))$(sum(tr,Technology(u,tr))>=1) * Location(u,n));

$If %Verbose% == 1 Display Flow.L,Power.L,Committed.L,ShedLoad.L,CurtailedPower.L,StorageLevel.L,StorageInput.L,SystemCost.L,LL_MaxPower.L,LL_MinPower.L,LL_2U.L,LL_2D.L,LL_RampUp.L,LL_RampDown.L;

$else

* ***************************** ! NO ROLLING HORIZON !**********************************************************************


day = 1;
FirstHour = 1;
LastHour = ndays*24;
i(h) = NO;
*i(h)$(ord(h)<=24*7*16) = YES;
i(h) = YES;
*i(h)$(ord(h)<=(ndays-Config("RollingHorizon LookAhead", "day"))*24) = YES;

*EXECUTE_UNLOAD "Inputs_ALL.gdx";

display day,FirstHour,LastHour;
*StorageFinalMin(s) = StorageInitial(s);
StorageFinalMin(s) =  min(StorageInitial(s) + (sum(i,StorageInflow(s,i)) - sum(i,StorageOutflow(s,i)))*Nunits(s), sum(i$(ord(i)=card(i)),StorageProfile(s,i)*Nunits(s)*StorageCapacity(s)*AvailabilityFactor(s,i)));
StorageFinalMin(s) = min(StorageFinalMin(s),Nunits(s)*StorageCapacity(s) - Nunits(s)*smax(i,StorageInflow(s,i)));
StorageFinalMin(s) = (StorageInitial(s) + (sum(i,StorageInflow(s,i)) - sum(i,StorageOutflow(s,i)))*Nunits(s))*0.95;
StorageFinalMin(s) = sum(i$(ord(i)=card(i)),StorageProfile(s,i)*Nunits(s)*StorageCapacity(s)*AvailabilityFactor(s,i));
EXECUTE_UNLOAD "ok.gdx";
LastKeptHour = 1


$If %Verbose% == 1   Display PowerInitial,CommittedInitial,StorageFinalMin;

$If %LPFormulation% == 1          SOLVE UCM_SIMPLE USING LP MINIMIZING SystemCostD;
$If not %LPFormulation% == 1      SOLVE UCM_SIMPLE USING MIP MINIMIZING SystemCostD;

$If %Verbose% == 0 $goto skipdisplay2
$If %LPFormulation% == 1          Display EQ_Objective_function.M, EQ_CostRampUp.M, EQ_CostRampDown.M, EQ_Demand_balance_DA.M, EQ_Storage_minimum.M, EQ_Storage_level.M, EQ_Storage_input.M, EQ_Storage_balance.M, EQ_Storage_boundaries.M, EQ_Storage_MaxCharge.M, EQ_Storage_MaxDischarge.M, EQ_Flow_limits_lower.M ;
$If not %LPFormulation% == 1      Display EQ_Objective_function.M, EQ_CostStartUp.M, EQ_CostShutDown.M, EQ_Commitment.M, EQ_MinUpTime.M, EQ_MinDownTime.M, EQ_RampUp_TC.M, EQ_RampDown_TC.M, EQ_Demand_balance_DA.M, EQ_Demand_balance_2U.M, EQ_Demand_balance_2D.M, EQ_Demand_balance_3U.M, EQ_Reserve_2U_capability.M, EQ_Reserve_2D_capability.M, EQ_Reserve_3U_capability.M, EQ_Power_must_run.M, EQ_Power_available.M, EQ_Storage_minimum.M, EQ_Storage_level.M, EQ_Storage_input.M, EQ_Storage_balance.M, EQ_Storage_boundaries.M, EQ_Storage_MaxCharge.M, EQ_Storage_MaxDischarge.M, EQ_SystemCost.M, EQ_Flow_limits_lower.M, EQ_Flow_limits_upper.M, EQ_Force_Commitment.M, EQ_Force_DeCommitment.M, EQ_LoadShedding.M ;
$label skipdisplay2

status("model",i) = UCM_SIMPLE.Modelstat;
status("solver",i) = UCM_SIMPLE.Solvestat;

if(UCM_SIMPLE.Modelstat <> 1 and UCM_SIMPLE.Modelstat <> 8 and not failed, CommittedInitial_dbg(u) = CommittedInitial(u); PowerInitial_dbg(u) = PowerInitial(u); StorageInitial_dbg(s) = StorageInitial(s);
                                                                           EXECUTE_UNLOAD "debug.gdx" day, status, CommittedInitial_dbg, PowerInitial_dbg, StorageInitial_dbg;
                                                                           failed=1;);

         CommittedInitial(u)=sum(i$(ord(i)=LastKeptHour-FirstHour+1),Committed.L(u,i));
         PowerInitial(u) = sum(i$(ord(i)=LastKeptHour-FirstHour+1),Power.L(u,i));

         StorageInitial(s) =   sum(i$(ord(i)=LastKeptHour-FirstHour+1),StorageLevel.L(s,i));
         StorageInitial(chp) =   sum(i$(ord(i)=LastKeptHour-FirstHour+1),StorageLevel.L(chp,i));


*Loop variables to display after solving:
$If %Verbose% == 1 Display LastKeptHour,PowerInitial,CostStartUpH.L,CostShutDownH.L,CostRampUpH.L;

CurtailedPower.L(n,z)=sum(u,(Nunits(u)*PowerCapacity(u)*LoadMaximum(u,z)-Power.L(u,z))$(sum(tr,Technology(u,tr))>=1) * Location(u,n));

$If %Verbose% == 1 Display Flow.L,Power.L,Committed.L,ShedLoad.L,CurtailedPower.L,StorageLevel.L,StorageInput.L,SystemCost.L,LL_MaxPower.L,LL_MinPower.L,LL_2U.L,LL_2D.L,LL_RampUp.L,LL_RampDown.L;


$endIf
;


solve_time = (jnow - start_time)*24*3600;
time_total = (jnow - start_program)*24*3600;


* See Mc Carlsen User Guide p. 212
scalar stat_memory;
scalar stat_compTime;
scalar stat_startupTime;
scalar stat_closingTime;
scalar stat_executationTime;

stat_memory = floor(Heapsize/1E6);
stat_compTime = Timecomp;
stat_startupTime = Timestart;
stat_executationTime = Timeexec;
stat_closingTime = Timeclose;

*===============================================================================
*Result export
*===============================================================================
$include utils_exportgdx.gms
