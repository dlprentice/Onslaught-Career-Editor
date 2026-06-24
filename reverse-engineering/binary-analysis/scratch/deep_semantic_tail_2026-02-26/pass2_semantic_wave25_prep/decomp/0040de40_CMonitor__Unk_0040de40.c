/* address: 0x0040de40 */
/* name: CMonitor__Unk_0040de40 */
/* signature: void __fastcall CMonitor__Unk_0040de40(void * param_1) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void __fastcall CMonitor__Unk_0040de40(void *param_1)

{
  int iVar1;
  int iVar2;
  void *pvVar3;
  int unaff_EDI;
  char acStack_100 [256];

  iVar2 = *(int *)(*(int *)((int)param_1 + 0x578) + 0x18);
  iVar1 = *(int *)(*(int *)(iVar2 + 0xa4) + 0x24);
  if ((*(int *)((int)param_1 + iVar1 * 4 + 0x55c) != 0) ||
     (_DAT_005d856c < *(float *)((int)param_1 + iVar1 * 4 + 0x52c))) {
    iVar1 = (**(code **)(*(int *)param_1 + 0x1d4))();
    if (iVar2 == iVar1) {
      iVar2 = (**(code **)(*(int *)param_1 + 0x1d4))();
      iVar2 = *(int *)(*(int *)(iVar2 + 0xa4) + 0x34);
      *(undefined4 *)((int)param_1 + 0x588) = 0;
      if (*(int *)((int)param_1 + 0x260) == 2) {
        CMonitor__Unk_00414010();
      }
      else if (*(int *)((int)param_1 + 0x260) == 3) {
        CMonitor__Unk_00412000(*(void **)((int)param_1 + 0x57c));
      }
      iVar1 = (**(code **)(*(int *)param_1 + 0x1d4))();
      if (iVar2 != *(int *)(*(int *)(iVar1 + 0xa4) + 0x34)) {
        *(undefined4 *)((int)param_1 + 0x2cc) = 0x3f800000;
      }
    }
    *(undefined4 *)((int)param_1 + 0x300) = DAT_00672fd0;
    *(undefined4 *)((int)param_1 + 0x2f8) = 0x41200000;
    *(undefined4 *)((int)param_1 + 0x2fc) = 1;
    sprintf(acStack_100,s_hud__s_00623314);
    pvVar3 = (void *)CBattleEngine__Helper_004e1910(&DAT_00896988,(int)acStack_100,0,unaff_EDI);
    CMonitor__Helper_004e1940(&DAT_00896988,pvVar3,param_1);
    *(undefined4 *)((int)param_1 + 0x30c) = DAT_00672fd0;
  }
  return;
}
