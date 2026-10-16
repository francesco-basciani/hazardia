! Synthetic component checks of the pinned, unmodified HMC storage routines.
! Not a basin simulation, calibrated intervention, or HMC->REFlEx integration.
program storage_probe
 use HMC_Module_Phys_HydraulicStructure, only: HMC_Phys_Dam_Spilling,HMC_Phys_Lake_Tank
 use HMC_Module_Vars_Loader, only: oHMC_Vars
 use HMC_Module_Namelist, only: oHMC_Namelist
 implicit none
 real(kind=4) :: v(1),q(1),coeff(1),length(1),hydro(3,3),deep(3,3),initial,dt
 allocate(oHMC_Vars(1)%a1dVMaxDam(1),oHMC_Vars(1)%a1dHMaxDam(1),oHMC_Vars(1)%a1dQcSLDam(1))
 allocate(oHMC_Vars(1)%a2iXYDam(1,2),oHMC_Vars(1)%a2dVDam(1,3),oHMC_Vars(1)%a2dLDam(1,3))
 allocate(oHMC_Vars(1)%a2dAreaCell(3,3))
 oHMC_Namelist(1)%dTV=0.5; oHMC_Namelist(1)%dDamSpillH=1.0
 oHMC_Vars(1)%a1dVMaxDam=1000.; oHMC_Vars(1)%a1dHMaxDam=10.; oHMC_Vars(1)%a1dQcSLDam=1.
 oHMC_Vars(1)%a2iXYDam=2; oHMC_Vars(1)%a2dVDam(1,:)=[0.,500.,1000.]
 oHMC_Vars(1)%a2dLDam(1,:)=[0.,5.,10.]; oHMC_Vars(1)%a2dAreaCell=100.
 coeff=0.;length=10.
 call dam_case('below_static_storage',450.,10.,450.,0.)
 call dam_case('below_spill_height',800.,10.,800.,0.)
 call dam_case('capped_spill',950.,10.,940.,100.)
 call dam_case('overflow_above_capacity',1200.,10.,1000.,2000.)
 call dam_case('static_storage_lower_bound',950.,1000.,500.,4500.)
 allocate(oHMC_Vars(1)%a1dVMinLake(1),oHMC_Vars(1)%a1dCostLake(1),oHMC_Vars(1)%a1dCodeLake(1))
 allocate(oHMC_Vars(1)%a2iXYLake(1,2),oHMC_Vars(1)%a2iPNT(3,3), &
          oHMC_Vars(1)%a2iChoice(3,3),oHMC_Vars(1)%a2iMask(3,3))
 oHMC_Vars(1)%a1dVMinLake=100.;oHMC_Vars(1)%a1dCostLake=.1;oHMC_Vars(1)%a1dCodeLake=0.
 oHMC_Vars(1)%a2iXYLake=2;oHMC_Vars(1)%a2iPNT=6;oHMC_Vars(1)%a2iChoice=0;oHMC_Vars(1)%a2iMask=1
 v=1100.;initial=v(1);dt=3600.;hydro=0.;deep=0.
 call HMC_Phys_Lake_Tank(1,3,3,dt,1,v,q,hydro,deep)
 call near('lake_volume_m3',v(1),1000.)
 call near('lake_outflow_mm_per_h',q(1),1000.)
 call near('lake_downstream_mm',deep(2,3),1000.)
 call near('lake_volume_balance_m3',initial-v(1),sum(deep)*100./1000.)
 write(*,*) 'LAKE',v(1),q(1),deep(2,3)
 v=50.;deep=0.;hydro=0.
 call HMC_Phys_Lake_Tank(1,3,3,dt,1,v,q,hydro,deep)
 call near('lake_below_min_volume',v(1),50.);call near('lake_below_min_release',q(1),0.)
 write(*,*) 'ALL_COMPONENT_CHECKS_PASS'
 contains
 subroutine near(name,actual,expected)
 character(len=*),intent(in)::name
 real(kind=4),intent(in)::actual,expected
 if (.not.(abs(actual-expected)<=max(1.e-4,abs(expected)*1.e-5))) then
  write(*,*) 'FAIL',name,actual,expected
  stop 1
 endif
 write(*,*) 'PASS',name,actual,expected
 end subroutine
 subroutine dam_case(name,start,step,expected_v,expected_q_mm)
 character(len=*),intent(in)::name
 real(kind=4),intent(in)::start,step,expected_v,expected_q_mm
 v=start
 call HMC_Phys_Dam_Spilling(1,1,step,v,q,coeff,length)
 call near(name//'_storage_m3',v(1),expected_v)
 call near(name//'_release_mm_per_step',q(1),expected_q_mm)
 call near(name//'_balance_m3',start-v(1),q(1)*100./1000.)
 write(*,*) 'DAM',name,start,step,v(1),q(1)
 end subroutine
end program
