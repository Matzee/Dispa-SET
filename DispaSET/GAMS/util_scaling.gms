* This file scales the variables for better numerical stability
*     Keep in mind that the scaling of the objective funcition is done manually
*     Scaling errors can still occur in the beginning, but later not anymore
CostStartUpH.scale(u,h) = 1E6;
CostShutDownH.scale(u,h) = 1E6;
CostRampUpH.scale(u,h) = 1E6;
CostRampDownH.scale(u,h) = 1E6;
Flow.scale(l,h)  = 1E3;
StorageInput.scale(u,h) = 1E3;
StorageLevel.scale(u,h) = 1E3;
LL_RampUp.scale(u,h) = 1E3;
LL_RampDown.scale(u,h)  = 1E3;
LL_MinPower.scale(n,h) = 1E3;
spillage.scale(s,h) = 1E3;
Reserve_2D.scale(u,h) = 1E3;
Reserve_3U.scale(u,h) = 1E3;
Heat.scale(chp,h) = 1E3;
Power.scale(u,h) = 1E3;
