* Calculates start values for independent blocks
*HOURS:     1,2,3,...,24,1,2,...,24,...,24
*DAYS:       1,...    4,          5      6
*                      _          _      _
savemyi(h) = i(h);
i(h) = NO;
i(h)$(ord(h)<24*7)=YES;

* get mean of these days as estimate
StorageFinalMin(s) = min(StorageInitial(s) + (sum(i,StorageInflow(s,i)) - sum(i,StorageOutflow(s,i)))*Nunits(s), sum(i$(ord(i)=card(i)),StorageProfile(s,i)*Nunits(s)*StorageCapacity(s)*AvailabilityFactor(s,i)));
StorageFinalMin(s) = min(StorageFinalMin(s), Nunits(s)*StorageCapacity(s) - Nunits(s)*smax(i,StorageInflow(s,i)));
solve Subproblem minimizing Z_SUB using lp;
CommittedInitial(u) = round(sum(i$(ord(i)=96 or ord(i) = 120 or ord(i) = 144),Committed.L(u,i))/3, 3);
PowerInitial(u) = round(sum(i$(ord(i)=96 or ord(i) = 120 or ord(i) = 144),Power.L(u,i))/3, 3);

* Remove side effects
i(h) = NO;
i(h) = savemyi(h);
