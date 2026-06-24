/* address: 0x004e2e60 */
/* name: CUnit__PlayImpactSoundForMaterials */
/* signature: void __cdecl CUnit__PlayImpactSoundForMaterials(void * param_1, void * param_2) */


void __cdecl CUnit__PlayImpactSoundForMaterials(void *param_1,void *param_2)

{
  int iVar1;
  int iVar2;
  int iVar3;
  void *pvVar4;
  int unaff_EDI;
  char *pcVar5;
  char acStack_c [12];

  if ((param_1 != (void *)0x0) && (param_2 != (void *)0x0)) {
    iVar1 = (**(code **)(*(int *)param_1 + 0xac))();
    iVar2 = (**(code **)(*(int *)param_2 + 0xac))();
    iVar3 = iVar2;
    if (iVar2 < iVar1) {
      iVar3 = iVar1;
      iVar1 = iVar2;
    }
    if ((0 < iVar1) && (iVar1 < 9)) {
      if (iVar3 == 0x66) {
        pcVar5 = s_impact_Wood_00632640;
      }
      else {
        _rand();
        sprintf(acStack_c,s_hit__d_00632638);
        pcVar5 = acStack_c;
      }
      pvVar4 = (void *)CBattleEngine__Helper_004e1910(&DAT_00896988,(int)pcVar5,0,unaff_EDI);
      if (pvVar4 != (void *)0x0) {
        CMonitor__Helper_004e1940(&DAT_00896988,pvVar4,param_1);
      }
    }
  }
  return;
}
