/* address: 0x004d2010 */
/* name: CExplosionInitThing__UpdateAttackLaunchAnimationState */
/* signature: int __fastcall CExplosionInitThing__UpdateAttackLaunchAnimationState(void * param_1) */


int __fastcall CExplosionInitThing__UpdateAttackLaunchAnimationState(void *param_1)

{
  int iVar1;
  void *pvVar2;
  int iVar3;
  char *pcVar4;
  void *pvVar5;

  iVar1 = (**(code **)(*(int *)((int)param_1 + 8) + 0x58))();
  if (iVar1 != -1) {
    if (*(int *)((int)param_1 + 0x27c) == 2) {
      iVar1 = *(int *)param_1;
      pvVar5 = (void *)0x1;
      pcVar4 = s_attack_00624438;
      pvVar2 = (void *)(**(code **)(**(int **)((int)param_1 + 0x30) + 0x24))(s_attack_00624438,1,1);
      iVar3 = FindAnimationIndex(pvVar2,(int)pcVar4,pvVar5);
      (**(code **)(iVar1 + 0xf0))(iVar3);
      *(undefined4 *)((int)param_1 + 0x27c) = 4;
    }
    else if (*(int *)((int)param_1 + 0x27c) == 3) {
      iVar1 = *(int *)param_1;
      pvVar5 = (void *)0x1;
      pcVar4 = s_launch_006243f8;
      pvVar2 = (void *)(**(code **)(**(int **)((int)param_1 + 0x30) + 0x24))(s_launch_006243f8,1,1);
      iVar3 = FindAnimationIndex(pvVar2,(int)pcVar4,pvVar5);
      (**(code **)(iVar1 + 0xf0))(iVar3);
      *(undefined4 *)((int)param_1 + 0x27c) = 1;
      return 0;
    }
  }
  return 0;
}
