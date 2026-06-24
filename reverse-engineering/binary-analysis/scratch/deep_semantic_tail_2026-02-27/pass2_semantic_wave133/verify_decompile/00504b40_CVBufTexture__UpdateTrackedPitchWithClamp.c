/* address: 0x00504b40 */
/* name: CVBufTexture__UpdateTrackedPitchWithClamp */
/* signature: void __fastcall CVBufTexture__UpdateTrackedPitchWithClamp(int param_1) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void __fastcall CVBufTexture__UpdateTrackedPitchWithClamp(int param_1)

{
  int *piVar1;
  int iVar2;
  int unaff_ESI;
  double dVar3;
  float local_10;
  float fStack_c;
  float fStack_8;

  if ((*(byte *)(param_1 + 0x2c) & 4) == 0) {
    if ((*(int *)(param_1 + 0x13c) == 0) ||
       (piVar1 = *(int **)(*(int *)(param_1 + 0x13c) + 0xc), piVar1 == (int *)0x0)) {
      if (*(float *)(param_1 + 0x20c) < DAT_00672fd0) {
        *(undefined4 *)(param_1 + 0xec) = *(undefined4 *)(param_1 + 0xf4);
      }
    }
    else {
      if (*(int *)(param_1 + 0x140) != 0) {
        (**(code **)(*piVar1 + 0x168))(&local_10);
        iVar2 = *(int *)((int)*(void **)(param_1 + 0x140) + 0xa0);
        if ((iVar2 != 0) && (*(int *)(iVar2 + 0x18) != 0)) {
          dVar3 = CEngine__Unk_005094b0
                            (*(void **)(param_1 + 0x140),unaff_ESI,local_10,fStack_c,fStack_8);
          *(float *)(param_1 + 0xec) = (float)dVar3;
        }
      }
      *(float *)(param_1 + 0x20c) = DAT_00672fd0 + _DAT_005d85cc;
    }
    if (*(float *)(param_1 + 0xec) < _DAT_005dfc44) {
      *(undefined4 *)(param_1 + 0xec) = 0xbfa78d36;
      return;
    }
    if (_DAT_005d85d8 < *(float *)(param_1 + 0xec)) {
      *(undefined4 *)(param_1 + 0xec) = 0x40a00000;
    }
  }
  return;
}
