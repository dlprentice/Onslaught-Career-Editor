/* address: 0x004e7f40 */
/* name: CSquadNormal__Unk_004e7f40 */
/* signature: int __fastcall CSquadNormal__Unk_004e7f40(int param_1) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

int __fastcall CSquadNormal__Unk_004e7f40(int param_1)

{
  float fVar1;
  int iVar2;
  float fVar3;
  int *piVar4;
  undefined4 *puVar5;
  int iVar6;

  puVar5 = *(undefined4 **)(param_1 + 0xa4);
  iVar6 = 0;
  if (puVar5 == (undefined4 *)0x0) {
    piVar4 = (int *)0x0;
  }
  else {
    piVar4 = (int *)*puVar5;
  }
  if (piVar4 != (int *)0x0) {
    fVar1 = 0.0;
    fVar3 = _DAT_005d856c;
    do {
      iVar2 = *piVar4;
      if (iVar2 != 0) {
        fVar3 = fVar3 + *(float *)(iVar2 + 0x1c);
        fVar1 = fVar1 + *(float *)(iVar2 + 0x20);
        iVar6 = iVar6 + 1;
      }
      puVar5 = (undefined4 *)puVar5[1];
      if (puVar5 == (undefined4 *)0x0) {
        piVar4 = (int *)0x0;
      }
      else {
        piVar4 = (int *)*puVar5;
      }
    } while (piVar4 != (int *)0x0);
    if ((iVar6 != 0) &&
       (fVar3 = *(float *)(param_1 + 0x1c) - fVar3 / (float)iVar6,
       fVar1 = *(float *)(param_1 + 0x20) - fVar1 / (float)iVar6,
       SQRT(fVar3 * fVar3 + fVar1 * fVar1) < *(float *)(param_1 + 0x10c) * _DAT_005d857c)) {
      return 1;
    }
  }
  return 0;
}
