/* address: 0x00428cb0 */
/* name: CExplosionInitThing__TriggerHitAnimationAndSetFlag */
/* signature: void __fastcall CExplosionInitThing__TriggerHitAnimationAndSetFlag(void * param_1) */


void __fastcall CExplosionInitThing__TriggerHitAnimationAndSetFlag(void *param_1)

{
  int iVar1;
  void *this;
  int iVar2;
  undefined **ppuVar3;
  void *pvVar4;

  iVar1 = *(int *)param_1;
  pvVar4 = (void *)0x1;
  ppuVar3 = &PTR_DAT_006248e8;
  this = (void *)(**(code **)(**(int **)((int)param_1 + 0x30) + 0x24))(&PTR_DAT_006248e8,1,0);
  iVar2 = FindAnimationIndex(this,(int)ppuVar3,pvVar4);
  (**(code **)(iVar1 + 0xf0))(iVar2);
  *(undefined4 *)((int)param_1 + 700) = 1;
  return;
}
