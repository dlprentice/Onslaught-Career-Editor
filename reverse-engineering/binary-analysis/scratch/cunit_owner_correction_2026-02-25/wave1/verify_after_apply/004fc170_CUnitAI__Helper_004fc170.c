/* address: 0x004fc170 */
/* name: CUnitAI__Helper_004fc170 */
/* signature: void __fastcall CUnitAI__Helper_004fc170(int param_1) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void __fastcall CUnitAI__Helper_004fc170(int param_1)

{
  void *pvVar1;
  int iVar2;
  float fVar3;

  if ((*(int *)(param_1 + 0x140) != 0) &&
     (pvVar1 = *(void **)(*(int *)(*(int *)(param_1 + 0x140) + 0xa0) + 0x14), pvVar1 != (void *)0x0)
     ) {
    CSoundManager__Unk_004e1940(&DAT_00896988,pvVar1,(void *)param_1);
  }
  CUnit__Unk_004fc220((void *)param_1);
  *(undefined4 *)(param_1 + 0x1e8) = 0;
  if ((*(int *)(param_1 + 0x140) != 0) &&
     (iVar2 = *(int *)(*(int *)(param_1 + 0x140) + 0xa0), *(float *)(iVar2 + 0x8c) != _DAT_005d856c)
     ) {
    fVar3 = DAT_00672fd0 + *(float *)(iVar2 + 0x8c);
    *(undefined4 *)(param_1 + 0x168) = 2;
    *(float *)(param_1 + 0x16c) = fVar3;
    return;
  }
  *(undefined4 *)(param_1 + 0x168) = 0;
  return;
}
