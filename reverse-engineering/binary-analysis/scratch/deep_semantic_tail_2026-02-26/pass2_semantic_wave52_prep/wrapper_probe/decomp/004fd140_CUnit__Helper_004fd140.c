/* address: 0x004fd140 */
/* name: CUnit__Helper_004fd140 */
/* signature: int __fastcall CUnit__Helper_004fd140(int param_1) */


int __fastcall CUnit__Helper_004fd140(int param_1)

{
  undefined4 *puVar1;
  int *value;
  int iVar2;
  void *unaff_ESI;

  if ((*(byte *)(param_1 + 0x2c) & 4) != 0) {
    return 0;
  }
  CSoundManager__KillSamplesForThing(&DAT_00896988,param_1,unaff_ESI);
  iVar2 = *(int *)(param_1 + 0x164);
  *(byte *)(param_1 + 0x2c) = *(byte *)(param_1 + 0x2c) | 4;
  if (iVar2 != 0) {
    if (*(int *)(param_1 + 0x138) == 0) {
      *(int *)(&DAT_008551c0 + *(int *)(iVar2 + 0xe0) * 4) =
           *(int *)(&DAT_008551c0 + *(int *)(iVar2 + 0xe0) * 4) + -1;
      iVar2 = CUnit__Helper_00511510(*(int *)(param_1 + 0x164));
      iVar2 = -iVar2;
    }
    else {
      if (*(int *)(param_1 + 0x138) != 1) goto LAB_004fd1d2;
      *(int *)(&DAT_00855228 + *(int *)(iVar2 + 0xe0) * 4) =
           *(int *)(&DAT_00855228 + *(int *)(iVar2 + 0xe0) * 4) + -1;
      iVar2 = CUnit__Helper_00511510(*(int *)(param_1 + 0x164));
    }
    DAT_008a9b8c = DAT_008a9b8c + iVar2;
    *(byte *)(param_1 + 0x2d) = *(byte *)(param_1 + 0x2d) | 1;
  }
LAB_004fd1d2:
  if (*(int *)(param_1 + 0x178) != 0) {
    CDestructableSegmentsController__TriggerCascadeIfThresholdExceeded(*(int *)(param_1 + 0x178));
  }
  if (*(int *)(param_1 + 0x74) != 0) {
    IScript__Unk_00533660(*(int *)(param_1 + 0x74));
  }
  CGenericActiveReader__SetReader((void *)(param_1 + 0x144),(void *)0x0);
  while ((puVar1 = *(undefined4 **)(param_1 + 0x18c), puVar1 != (undefined4 *)0x0 &&
         (value = (int *)*puVar1, value != (int *)0x0))) {
    CSPtrSet__Remove((int *)(param_1 + 0x18c),value);
    (**(code **)(*value + 8))();
  }
  return 1;
}
