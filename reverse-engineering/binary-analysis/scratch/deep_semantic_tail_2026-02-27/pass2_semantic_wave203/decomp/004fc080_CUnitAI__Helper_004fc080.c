/* address: 0x004fc080 */
/* name: CUnitAI__Helper_004fc080 */
/* signature: int __fastcall CUnitAI__Helper_004fc080(void * param_1) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

int __fastcall CUnitAI__Helper_004fc080(void *param_1)

{
  float fVar1;
  int iVar2;
  int iVar3;

  iVar3 = 0;
  if (*(int *)((int)param_1 + 0x140) == 0) {
    if (*(int *)((int)param_1 + 0x144) != 0) {
      iVar2 = (**(code **)(*(int *)param_1 + 0x1cc))();
      if (iVar2 != 0) {
        iVar3 = CSpawnerThng__DoSpawn();
        iVar2 = *(int *)(*(int *)((int)param_1 + 0x144) + 0x3d0);
        if (*(float *)(iVar2 + 0x38) != _DAT_005d856c) {
          fVar1 = *(float *)(iVar2 + 0x38) + DAT_00672fd0;
          *(undefined4 *)((int)param_1 + 0x1e8) = 0;
          *(undefined4 *)((int)param_1 + 0x168) = 2;
          *(undefined4 *)((int)param_1 + 0x1ec) = 0;
          *(undefined4 *)((int)param_1 + 0x1e8) = 0;
          *(float *)((int)param_1 + 0x16c) = fVar1;
          return iVar3;
        }
        *(undefined4 *)((int)param_1 + 0x1e8) = 1;
        *(undefined4 *)((int)param_1 + 0x168) = 0;
      }
    }
  }
  else if (*(int *)((int)param_1 + 0x1e8) != 0) {
    iVar2 = CUnit__Helper_00509f70(*(int *)((int)param_1 + 0x140));
    if (iVar2 != 0) {
      CGeneralVolume__Helper_00506010(*(void **)((int)param_1 + 0x140));
      (**(code **)(*(int *)param_1 + 0x15c))();
      *(undefined4 *)((int)param_1 + 0x1ec) = 0;
      *(undefined4 *)((int)param_1 + 0x1e8) = 0;
      return 1;
    }
  }
  *(undefined4 *)((int)param_1 + 0x1ec) = 0;
  *(undefined4 *)((int)param_1 + 0x1e8) = 0;
  return iVar3;
}
