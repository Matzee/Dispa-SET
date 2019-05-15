* THIS FILE PREPARES THE INDEPENDENT BLOCKS FOR INDEPENDENT SOLVING
scalar block_i /1/;
scalar LastHour_firstP;
set min_i(h);
min_i(h) = no;
set foriter(subiter);

*alias(blockiter, foriter)

* GAMS particularity: I can not select two subsets for GUSS which are the complete union of the parent set
*   without any domain violation --> Attention! Risk of bug
blockiter(subiter) = YES;
StorageInitial_block(blockiter, u) = 0;

Config("RollingHorizon LookAhead","day") = 1;

i(h) = YES;

* Do  not make any sense for independent blocks -> incorrect sum
*Config("RollingHorizon Length","day") = 7;



sets
  my_week_hours(h)
  trow(h)
  hour_mapping(h,hh);

hour_mapping(h,hh) = NO;
my_week_hours(h) = YES$(ord(h) <= FirstHour + (Config("RollingHorizon Length","day")+Config("RollingHorizon LookAhead","day")) * 24 - 1)


PARAMETER
**** USED FOR the blocks
AvailabilityFactor_block_(subiter,u,h)
CostVariable_block_(subiter,u,h)
CostHeatSlack_block_(subiter,chp,h)
CostLoadShedding_block_(subiter,n,h)
Demand_block_(subiter,mk,n,h)
FlowMaximum_block_(subiter,l,h)
FlowMinimum_block_(subiter,l,h)
FuelPrice_block_(subiter,n,f,h)
HeatDemand_block_(subiter,chp,h)
LoadShedding_block_(subiter,n,h)
Markup_block_(subiter,u,h)
OutageFactor_block_(subiter,u,h)
PriceTransmission_block_(subiter,l,h)
RampStartUpMaximumH_block_(subiter,u,h)
RampShutDownMaximumH_block_(subiter,u,h)
StorageOutflow_block_(subiter,u,h)
StorageInflow_block_(subiter,u,h)
StorageProfile_block_(subiter,u,h)
QuickStartPower_block_(subiter,u,h)
CostLoadShedding_block_(subiter,n,h)
LoadMaximum_block_(subiter,u,h)
PowerMustRun_block_(subiter,u,h)
StorageInitial_block_(subiter, u)
CommittedInitial_series_block_(subiter,u,h)
PowerInitial_series_block_(subiter,u,h)
CapacityFactorHDAM_block_(subiter, h)
StorageOutflow_block_(subiter, u, h)
StorageInflow_block_(subiter, u, h)
lasthour_week(subiter)
;

parameter testtt(subiter,mk,n,h);
parameter LastHour_s(subiter);
set i_ss(subiter, h);


* Prepare blocks
*         rh_1                    rh_2
* ----------------------------------
*                          ---------------------------------

* Config("RollingHorizon Length","day") = 1;
FOR(day = 1 TO ndays-Config("RollingHorizon LookAhead","day") by Config("RollingHorizon Length","day"),
                foriter(subiter) = NO;
*                blockiter(subiter) = NO;
                blockiter(subiter)$(ord(subiter) = block_i) = YES;
                foriter(subiter)$(ord(subiter) = block_i) = YES;

                FirstHour = (day-1)*24+1;
                FirstHour_s(foriter) = FirstHour;
                LastHour = min(card(h),FirstHour + (Config("RollingHorizon Length","day")+Config("RollingHorizon LookAhead","day")) * 24 - 1);
                LastHour_s(foriter) = LastHour;
                hour_mapping(my_week_hours,h)$(ord(h)>=FirstHour and ord(h)<=lasthour) = YES;
                if (day=1, LastHour_firstP = LastHour; min_i(h)$(ord(h)<=LastHour_firstP) = YES;);
                LastKeptHour_s(foriter) = LastHour - Config("RollingHorizon LookAhead","day") * 24;
                i_ss(foriter,h) = NO;
                i_ss(foriter,h)$(ord(h)>=firsthour and ord(h)<=lasthour) = YES;
                lasthour_week(foriter) = lasthour - FirstHour;
*                ####### DEFINE ALL PARAMETERS INTO BLOCKS WHICH ARE USED BY GUSS
                StorageInitial_block_(foriter, psp) = 0.5 *Nunits(psp)*StorageCapacity(psp);


*                Defining the minimum level at the end of the horizon, ensuring that it is feasible with the provided inflows:
                i(h) = NO;
                i(h)$(ord(h)>=firsthour and ord(h)<=lasthour) = YES;

                StorageInitial(hdam) = StorageCapacity(hdam)*sum(h, StorageProfile(hdam, h)$(ord(h) = FirstHour))*Nunits(hdam);
                StorageInitial_block_(foriter, hdam) = StorageInitial(hdam);

                StorageFinalMin(s) =  min(
                                            StorageInitial(s) + (sum(i,StorageInflow(s,i)) - sum(i,StorageOutflow(s,i)))*Nunits(s)
                                            ,
                                            sum(i$(ord(i)=card(i)),StorageProfile(s,i)*Nunits(s)*StorageCapacity(s)*AvailabilityFactor(s,i))
                                        );
*               Correcting the minimum level to avoid the infeasibility in case it is too close to the StorageCapacity:
                StorageFinalMin_s(foriter, s) = min(StorageFinalMin(s),Nunits(s)*StorageCapacity(s));


*               ##################################### TEMPORARY BLOCKS
*                testtt(mk,n,my_week_hours) = Demand(mk,n,h$(ord(h) + FirstHour >= FirstHour and ord(h) + FirstHour <=LastHour + FirstHour);
*               interdependant
*CommittedInitial_series_block_(foriter,u,h)  = CommittedInitial_series(u,h)      $(ord(h) >=FirstHour and ord(h)  <=lasthour);
                PowerInitial_series_block_(foriter,u,h)                   = PowerInitial_series    (u,h)      $(ord(h) >=FirstHour and ord(h)  <=lasthour);

*               simple time dependant parameters
                AvailabilityFactor_block_            (foriter,u,h)       = AvailabilityFactor       (u,h)      $(ord(h) >=FirstHour and ord(h)  <=lasthour);
                CostVariable_block_                  (foriter,u,h)             = CostVariable       (u,h)      $(ord(h) >=FirstHour and ord(h)  <=lasthour);
                CostHeatSlack_block_                 (foriter,chp,h)          = CostHeatSlack       (chp,h)    $(ord(h) >=FirstHour and ord(h)  <=lasthour);
                CostLoadShedding_block_              (foriter,n,h)         = CostLoadShedding       (n,h)      $(ord(h) >=FirstHour and ord(h)  <=lasthour);
                Demand_block_                        (foriter,mk,n,h)                = Demand       (mk,n,h)   $(ord(h) >=FirstHour and ord(h)  <=lasthour);
                FlowMaximum_block_                   (foriter,l,h)              = FlowMaximum       (l,h)      $(ord(h) >=FirstHour and ord(h)  <=lasthour);
                FlowMinimum_block_                   (foriter,l,h)              = FlowMinimum       (l,h)      $(ord(h) >=FirstHour and ord(h)  <=lasthour);
                FuelPrice_block_                     (foriter,n,f,h)              = FuelPrice       (n,f,h)    $(ord(h) >=FirstHour and ord(h)  <=lasthour);
                HeatDemand_block_                    (foriter,chp,h)             = HeatDemand       (chp,h)    $(ord(h) >=FirstHour and ord(h)  <=lasthour);
                LoadShedding_block_                  (foriter,n,h)             = LoadShedding       (n,h)      $(ord(h) >=FirstHour and ord(h)  <=lasthour);
                Markup_block_                        (foriter,u,h)                   = Markup       (u,h)      $(ord(h) >=FirstHour and ord(h)  <=lasthour);
                OutageFactor_block_                  (foriter,u,h)             = OutageFactor       (u,h)      $(ord(h) >=FirstHour and ord(h)  <=lasthour);
                PriceTransmission_block_             (foriter,l,h)        = PriceTransmission       (l,h)      $(ord(h) >=FirstHour and ord(h)  <=lasthour);
                RampStartUpMaximumH_block_           (foriter,u,h)      = RampStartUpMaximumH       (u,h)      $(ord(h) >=FirstHour and ord(h)  <=lasthour);
                RampShutDownMaximumH_block_          (foriter,u,h)     = RampShutDownMaximumH       (u,h)      $(ord(h) >=FirstHour and ord(h)  <=lasthour);
                StorageOutflow_block_                (foriter,u,h)           = StorageOutflow       (u,h)      $(ord(h) >=FirstHour and ord(h)  <=lasthour);
                StorageInflow_block_                 (foriter,u,h)            = StorageInflow       (u,h)      $(ord(h) >=FirstHour and ord(h)  <=lasthour);
                StorageProfile_block_                (foriter,u,h)           = StorageProfile       (u,h)      $(ord(h) >=FirstHour and ord(h)  <=lasthour);
                QuickStartPower_block_               (foriter,u,h)          = QuickStartPower       (u,h)      $(ord(h) >=FirstHour and ord(h)  <=lasthour);
                CostLoadShedding_block_              (foriter,n,h)         = CostLoadShedding       (n,h)      $(ord(h) >=FirstHour and ord(h)  <=lasthour);
                LoadMaximum_block_                   (foriter,u,h)              = LoadMaximum       (u,h)      $(ord(h) >=FirstHour and ord(h)  <=lasthour);
                PowerMustRun_block_                  (foriter,u,h)             = PowerMustRun       (u,h)      $(ord(h) >=FirstHour and ord(h)  <=lasthour);
*                CapacityFactorHDAM_block_             (foriter, h)             = CapacityFactorHDAM     (h)        $(ord(h) >=FirstHour and ord(h)  <=lasthour);
                StorageOutflow_block_                (foriter, u,h)             = StorageOutflow    (u, h)     $(ord(h) >=FirstHour and ord(h)  <=lasthour);
                StorageInflow_block_                 (foriter, u,h)             = StorageInflow     (u, h)     $(ord(h) >=FirstHour and ord(h)  <=lasthour);

                block_i=block_i+1
);


scalar row ;
row = 1 ;

blockiter(subiter) = NO;
blockiter(subiter)$(ord(subiter) <= block_i-1) = YES;

CommittedInitial_series_block_(blockiter,u,h) = CommittedInitial_series(u, h);
*PowerInitial_series_block_(foriter,u,h)      = PowerInitial_series    (u,h);
PowerInitial_series_block_(subiter,u,h)$(ord(subiter)>1) = 0;
CommittedInitial_series_block_(subiter,u,h)$(ord(subiter)>1) = 0;
StorageInitial_block(subiter, s)  = StorageInitial_block_(subiter, s);

*StorageProfile_block(blockiter,s,my_week_hours) = 0;

scalar LastHourZ;
LastHourZ =smax(blockiter, LastKeptHour_s(blockiter));

* Turn into blocks and reset the inital point of the rolling horizon
*             time period i
*   rh_1 -------------------------
*   rh_2  ------------------------
* !!! MUST HAVE SAME LENGTH!! (for guss, for grid not)


loop(blockiter,
    loop(my_week_hours,

        trow(h) = NO ;
        trow(h) = YES $ (ord(h) = row);

        Demand_block(blockiter,mk,n,my_week_hours)                                 =sum(trow, Demand_block_(blockiter,mk,n,trow)              );
        CommittedInitial_series_block(blockiter,u,my_week_hours)                   =sum(trow, CommittedInitial_series_block_(blockiter,u,trow));
        PowerInitial_series_block(blockiter,u,my_week_hours)                       =sum(trow, PowerInitial_series_block_(blockiter,u,trow)    );
*       ATTENTION: AvailabilityFactor only for storages (GUSS)
        AvailabilityFactor_block(blockiter,s,my_week_hours)                        =sum(trow, AvailabilityFactor_block_(blockiter,s,trow)     );
        CostVariable_block(blockiter,u,my_week_hours)                              =sum(trow, CostVariable_block_(blockiter,u,trow)           );
        CostHeatSlack_block(blockiter,chp,my_week_hours)                           =sum(trow, CostHeatSlack_block_(blockiter,chp,trow)        );
        CostLoadShedding_block(blockiter,n,my_week_hours)                          =sum(trow, CostLoadShedding_block_(blockiter,n,trow)       );
        Demand_block(blockiter,mk,n,my_week_hours)                                 =sum(trow, Demand_block_(blockiter,mk,n,trow)              );
        FlowMaximum_block(blockiter,l,my_week_hours)                               =sum(trow, FlowMaximum_block_(blockiter,l,trow)            );
        FlowMinimum_block(blockiter,l,my_week_hours)                               =sum(trow, FlowMinimum_block_(blockiter,l,trow)            );
        FuelPrice_block(blockiter,n,f,my_week_hours)                               =sum(trow, FuelPrice_block_(blockiter,n,f,trow)            );
        HeatDemand_block(blockiter,chp,my_week_hours)                              =sum(trow, HeatDemand_block_(blockiter,chp,trow)           );
        LoadShedding_block(blockiter,n,my_week_hours)                              =sum(trow, LoadShedding_block_(blockiter,n,trow)           );
        Markup_block(blockiter,u,my_week_hours)                                    =sum(trow, Markup_block_(blockiter,u,trow)                 );
        OutageFactor_block(blockiter,u,my_week_hours)                              =sum(trow, OutageFactor_block_(blockiter,u,trow)           );
        PriceTransmission_block(blockiter,l,my_week_hours)                         =sum(trow, PriceTransmission_block_(blockiter,l,trow)      );
        RampStartUpMaximumH_block(blockiter,u,my_week_hours)                       =sum(trow, RampStartUpMaximumH_block_(blockiter,u,trow)    );
        RampShutDownMaximumH_block(blockiter,u,my_week_hours)                      =sum(trow, RampShutDownMaximumH_block_(blockiter,u,trow)   );
        StorageOutflow_block(blockiter,u,my_week_hours)                            =sum(trow, StorageOutflow_block_(blockiter,u,trow)         );
        StorageProfile_block(blockiter,u,my_week_hours)                            =sum(trow, StorageProfile_block_(blockiter,u,trow)         );
        QuickStartPower_block(blockiter,u,my_week_hours)                           =sum(trow, QuickStartPower_block_(blockiter,u,trow)        );
        CostLoadShedding_block(blockiter,n,my_week_hours)                          =sum(trow, CostLoadShedding_block_(blockiter,n,trow)       );
        LoadMaximum_block(blockiter,u,my_week_hours)                               =sum(trow, LoadMaximum_block_(blockiter,u,trow)            );
        PowerMustRun_block(blockiter,u,my_week_hours)                              =sum(trow, PowerMustRun_block_(blockiter,u,trow)           );
*        CapacityFactorHDAM_block(blockiter, my_week_hours)                         =sum(trow, CapacityFactorHDAM_block_(blockiter, trow)      );
        StorageOutflow_block(blockiter, u, my_week_hours)                          =sum(trow, StorageOutflow_block_(blockiter, u, trow)       );
        StorageInflow_block(blockiter, u, my_week_hours)                           =sum(trow, StorageInflow_block_(blockiter, u, trow)        );
        row = row + 1;
    );
*   This avoids the wrong initial point as it repeats the look ahead period
    row = row - Config("RollingHorizon LookAhead","day")*24;
);

*CapacityFactorHDAM_block(blockiter, my_week_hours)$(ord(my_week_hours) <> 1 and ord(my_week_hours) <> card(my_week_hours) )  = 0;
* GUSS particularity
StorageProfile_block(blockiter, s, my_week_hours)$(ord(my_week_hours) <> 1 and ord(my_week_hours)  <> 168)  = 0;
*StorageProfile_block(blockiter, s, my_week_hours)$(ord(my_week_hours) = 192)  = 0;

*StorageProfile_block(blockiter, s, my_week_hours)$(ord(my_week_hours) = 168)  = 0;
*StorageInitial_block(blockiter, s)  = sum(my_week_hours,  StorageCapacity(s)*Nunits(s)*StorageProfile_block(blockiter, s, my_week_hours)$(ord(my_week_hours) = 1));

*StorageFinalMin_block(blockiter, s)  = sum(my_week_hours,  StorageCapacity(s)*Nunits(s)*StorageProfile_block(blockiter, s, my_week_hours)$(ord(my_week_hours) = lasthour_week(blockiter)));
StorageFinalMin_block(blockiter, s) = 0;
StorageFinalMin_block(blockiter, s)$(ord(blockiter)=card(blockiter)) = sum(h$(ord(h)=LastHourZ),
                                                                        StorageProfile(s,h)*Nunits(s)*StorageCapacity(s)*AvailabilityFactor(s,h));


* This is now managed by the last equation which FIXES the amount
*StorageFinalMin_block(blockiter, s) = 0;
*StorageProfile_block(blockiter,psp,my_week_hours) = 0;
*AvailabilityFactor_block(blockiter,u,my_week_hours)$(ord(my_week_hours) <> 1 and ord(my_week_hours) <> card(my_week_hours))  = 0;

i(h) = NO;
i(h)$(ord(h) <= (Config("RollingHorizon Length","day")+Config("RollingHorizon LookAhead","day")) * 24)  = YES;

parameter objective_period(subiter);
objective_period(subiter) = NO;



* the objective normalization is either the period until the hour -24 or if the period is not long enough until the last hour

objective_period(blockiter) = lasthour_week(blockiter) + 1 - 24;

scalar LastHourLastWeek;
LastHourLastWeek = LastKeptHour*24*Config("RollingHorizon Length","day");
set lastblock(subiter);
lastblock(subiter) = NO;
lastblock(blockiter)$(ord(blockiter) = card(blockiter)) = YES;

Parameter StartProfile(s);
StartProfile(s) = StorageProfile(s, '1');

* last block to ensure accuracy for GUSS
StorageProfile_block(lastblock, s, h)$(ord(h)=LastKeptHour) =  0;
StorageProfile_block(lastblock, s, h)$(ord(h)=168) =  0;

execute_unload '%filepath%%outputname%' ;
