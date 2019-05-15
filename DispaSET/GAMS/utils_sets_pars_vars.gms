*===============================================================================
*Definition of   sets and parameters
*===============================================================================
SETS
mk               Markets
n                Nodes
l                Lines
u                All Units
uc(u)            Units expanded by CEP
ue(u)            Existing units
t                Generation technologies
tr(t)            Renewable generation technologies
f                Fuel types
p                Pollutants
s(u)             Storage Units (with reservoir)
chp(u)           CHP units
h                Hours
i(h)             Subset of simulated hours for one iteration
z(h)             Subset of all simulated hours
iter /i1 * i1000/
ii(iter)         Subset of iter used for the BD loop
i_(iter)         Subset of i to index $i - 1$
dam(s)
psp(s)
;


SETS

* only needed to define blockiter
subiter /1*1000/
blockiter(subiter);

Alias(mk,mkmk);
Alias(n,nn);
Alias(l,ll);
Alias(u,uu);
Alias(t,tt);
Alias(f,ff);
Alias(p,pp);
Alias(s,ss);
Alias(h,hh);
Alias(i,ii_);

*Parameters as defined in the input file
* /u indicate that the value is provided for one single unit
PARAMETERS
AvailabilityFactor(u,h)          [%]      Availability factor AA
CHPPowerLossFactor(u)            [%]      Power loss when generating heat
CHPPowerToHeat(u)                [%]      Nominal power-to-heat factor
CHPMaxHeat(chp)                  [MW per u]     Maximum heat capacity of chp plant
CHPType
CommittedInitial(u)              [n.a.]   Initial committment status
Config
*CostCurtailment(n,h)             [EUR per MW]  Curtailment costs
CostFixed(u)                     [EUR per h]    Fixed costs
CostRampUp(u)                    [EUR per MW per h] Ramp-up costs
CostRampDown(u)                  [EUR per MW per h] Ramp-down costs
CostShutDown(u)                  [EUR per u]    Shut-down costs
CostStartUp(u)                   [EUR per u]    Start-up costs
CostVariable(u,h)                [EUR per MW]   Variable costs
CostHeatSlack(chp,h)             [EUR per MWh]  Cost of supplying heat via other means
CostLoadShedding(n,h)            [EUR per MWh] Cost of load shedding
Curtailment(n)                   [n.a]    Curtailment allowed or not {1 0} at node n
Demand(mk,n,h)                   [MW]     Demand
Efficiency(u)                    [%]      Efficiency
EmissionMaximum(n,p)             [tP]     Emission limit
EmissionRate(u,p)                [tP per MWh] P emission rate
FlowMaximum(l,h)                 [MW]     Line limits
FlowMinimum(l,h)                 [MW]     Minimum flow
FuelPrice(n,f,h)                 [EUR per F]  Fuel price
Fuel(u,f)                        [n.a.]   Fuel type {1 0}
HeatDemand(chp,h)                [MWh per u]  Heat demand profile for chp units
LineNode(l,n)                    [n.a.]   Incidence matrix {-1 +1}
LoadShedding(n,h)                [MW]   Load shedding capacity
Location(u,n)                    [n.a.]   Location {1 0}
Markup(u,h)                      [EUR per MW]   Markup
OutageFactor(u,h)                [%]      Outage Factor (100% = full outage)
PartLoadMin(u)                   [%]      Minimum part load
PowerCapacity(u)                 [MW per u]     Installed capacity
PowerInitial(u)                  [MW per u]     Power output before initial period
PowerMinStable(u)                [MW per u]     Minimum power output
PriceTransmission(l,h)           [EUR per MWh]  Transmission price
StorageChargingCapacity(u)       [MW per u]     Storage capacity
StorageChargingEfficiency(u)     [%]      Charging efficiency
StorageSelfDischarge(u)          [% per day]  Self-discharge of the storage units
RampDownMaximum(u)               [MW per h per u]   Ramp down limit
RampShutDownMaximum(u)           [MW per h per u]   Shut-down ramp limit
RampStartUpMaximum(u)            [MW per h per u]   Start-up ramp limit
RampStartUpMaximumH(u,h)         [MW per h per u]   Start-up ramp limit - Clustered formulation
RampShutDownMaximumH(u,h)        [MW per h per u]   Shut-down ramp limit - Clustered formulation
RampUpMaximum(u)                 [MW per h per u]   Ramp up limit
Reserve(t)                       [n.a.]   Reserve technology {1 0}
StorageCapacity(u)               [MWh per u]    Storage capacity
StorageDischargeEfficiency(u)    [%]      Discharge efficiency
StorageOutflow(u,h)              [MWh per u]    Storage outflows
StorageInflow(u,h)               [MWh per u]    Storage inflows (potential energy)
StorageInitial(u)                [MWh]    Storage level before initial period
StorageProfile(u,h)              [MWh]    Storage level to be resepected at the end of each horizon
StorageMinimum(u)                [MWh per u]    Storage minimum
Technology(u,t)                  [n.a.]   Technology type {1 0}
TimeDownMinimum(u)               [h]      Minimum down time
TimeUpMinimum(u)                 [h]      Minimum up time
$If %RetrieveStatus% == 1 CommittedCalc(u,z)               [n.a.]   Committment status as for the MILP
Nunits(u)                        [n.a.]   Number of units inside the cluster (upper bound value for integer variables)
K_QuickStart(n)                  [n.a.]   Percentage of reserve provided by nonsynchronised offline resources (e.g. quick start units or demand response
QuickStartPower(u,h)             [MW per h per u]   Available max capacity in tertiary regulation up from fast-starting power plants - TC formulation
Investment(uc)                   [EUR]?Investment cost
EconomicLifetime(uc)             Economic Lifetime of the power plants
C_inv(uc)                        Investment cost
;



*Parameters as used within the loop
PARAMETERS
CostLoadShedding(n,h)            [EUR per MW]  Value of lost load
LoadMaximum(u,h)                 [%]     Maximum load given AF and OF
PowerMustRun(u,h)                [MW per u]    Minimum power output
StorageFinalMin(s)               [MWh]   Minimum storage level at the end of the optimization horizon
;

* Scalar variables necessary to the loop:
scalar FirstHour,LastHour,LastKeptHour,day,ndays,failed, RollingHorizon;
FirstHour = 1;

scalar intrate_investment       interest rate for investments [%] /0.09/;



Scalar
curt_penalty     penalty fee for curtailment
dem_penalty
epsilon / 0.01 /
EndOfWhile / 0 /
iteration





*===============================================================================
*Data import
*===============================================================================

$gdxin %inputfilename%
$LOAD u
$LOAD mk
$LOAD n
$LOAD l
$LOAD uc
$LOAD ue
$LOAD t
$LOAD tr
$LOAD f
$LOAD p
$LOAD s
$LOAD chp
$LOAD h
$LOAD z

$LOAD AvailabilityFactor
$LOAD CHPPowerLossFactor
$LOAD CHPPowerToHeat
$LOAD CHPMaxHeat
$LOAD CHPType
$LOAD Config
$LOAD CostFixed
$LOAD CostHeatSlack
$LOAD CostLoadShedding
$LOAD CostShutDown
$LOAD CostStartUp
$LOAD CostVariable
$LOAD Curtailment
$LOAD Demand
$LOAD StorageDischargeEfficiency
$LOAD Efficiency
$LOAD EmissionMaximum
$LOAD EmissionRate
$LOAD FlowMaximum
$LOAD FlowMinimum
$LOAD FuelPrice
$LOAD Fuel
$LOAD HeatDemand
$LOAD LineNode
$LOAD LoadShedding
$LOAD Location
$LOAD Markup
$LOAD Nunits
$LOAD OutageFactor
$LOAD PowerCapacity
$LOAD PowerInitial
$LOAD PartLoadMin
$LOAD PriceTransmission
$LOAD StorageChargingCapacity
$LOAD StorageChargingEfficiency
$LOAD StorageSelfDischarge
$LOAD RampDownMaximum
$LOAD RampShutDownMaximum
$LOAD RampStartUpMaximum
$LOAD RampUpMaximum
$LOAD Reserve
$LOAD StorageCapacity
$LOAD StorageInflow
$LOAD StorageInitial
$LOAD StorageProfile
$LOAD StorageMinimum
$LOAD StorageOutflow
$LOAD Technology
$LOAD TimeDownMinimum
$LOAD TimeUpMinimum
$LOAD CostRampUp
$LOAD CostRampDown
$If %RetrieveStatus% == 1 $LOAD CommittedCalc
$LOAD Investment
$LOAD EconomicLifetime
;



$If %Verbose% == 0 $goto skipdisplay

Display
mk,
n,
l,
u,
t,
tr,
f,
p,
s,
chp,
h,
AvailabilityFactor,
CHPPowerLossFactor,
CHPPowerToHeat,
CHPMaxHeat,
CHPType,
Config,
CostFixed,
CostShutDown,
CostStartUp,
CostRampUp,
CostVariable,
Demand,
StorageDischargeEfficiency,
Efficiency,
EmissionMaximum,
EmissionRate,
FlowMaximum,
FlowMinimum,
FuelPrice,
Fuel,
HeatDemand,
LineNode,
Location,
LoadShedding
Markup,
OutageFactor,
PartLoadMin,
PowerCapacity,
PowerInitial,
PriceTransmission,
StorageChargingCapacity,
StorageChargingEfficiency,
StorageSelfDischarge,
RampDownMaximum,
RampShutDownMaximum,
RampStartUpMaximum,
RampUpMaximum,
Reserve,
StorageCapacity,
StorageInflow,
StorageInitial,
StorageProfile,
StorageMinimum,
StorageOutflow,
Technology,
TimeDownMinimum,
TimeUpMinimum
$If %RetrieveStatus% == 1 , CommittedCalc
;

$label skipdisplay

*===============================================================================
*Definition of variables
*===============================================================================
VARIABLES
Committed(u,h)             [n.a.]  Unit committed at hour h {1 0} or integer
StartUp(u,h)        [n.a.]  Unit start up at hour h {1 0}  or integer
ShutDown(u,h)       [n.a.]  Unit shut down at hour h {1 0} or integer
;

$If %LPFormulation% == 1 POSITIVE VARIABLES Committed (u,h) ; Committed.UP(u,h) = 1 ;
$If not %LPFormulation% == 1 INTEGER VARIABLES Committed (u,h), StartUp(u,h), ShutDown(uc,h) ; Committed.UP(u,h) = Nunits(u) ; StartUp.UP(u,h) = Nunits(u) ; ShutDown.UP(u,h) = Nunits(u) ;

POSITIVE VARIABLES
CostStartUpH(u,h)          [EUR]   Cost of starting up
CostShutDownH(u,h)         [EUR]   cost of shutting down
CostRampUpH(u,h)           [EUR]   Ramping cost
CostRampDownH(u,h)         [EUR]   Ramping cost
CurtailedPower(n,h)        [MW]    Curtailed power at node n
Flow(l,h)                  [MW]    Flow through lines
Power(u,h)                 [MW]    Power output
ShedLoad(n,h)              [MW]    Shed load
StorageInput(u,h)          [MWh]   Charging input for storage units
StorageLevel(u,h)          [MWh]   Storage level of charge
LL_MaxPower(n,h)           [MW]    Deficit in terms of maximum power
LL_RampUp(u,h)             [MW]    Deficit in terms of ramping up for each plant
LL_RampDown(u,h)           [MW]    Deficit in terms of ramping down
LL_MinPower(n,h)           [MW]    Power exceeding the demand
LL_2U(n,h)                 [MW]    Deficit in reserve up
LL_3U(n,h)                 [MW]    Deficit in reserve up - non spinning
LL_2D(n,h)                 [MW]    Deficit in reserve down
spillage(s,h)              [MWh]   spillage from water reservoirs
SystemCost(h)              [EUR]   Hourly system cost
Reserve_2U(u,h)            [MW]    Spinning reserve up
Reserve_2D(u,h)            [MW]    Spinning reserve down
Reserve_3U(u,h)            [MW]    Non spinning quick start reserve up
Heat(chp,h)                [MW]    Heat output by chp plant
HeatSlack(chp,h)           [MW]    Heat satisfied by other sources
Expanded(uc)               []      Additional capacity to install (Generation Expansion)
DUMP_STOR(s,h)
CURT_STOR(s,h)
;

free variable
SystemCostD                ![EUR]   Total system cost for one optimization period
;
