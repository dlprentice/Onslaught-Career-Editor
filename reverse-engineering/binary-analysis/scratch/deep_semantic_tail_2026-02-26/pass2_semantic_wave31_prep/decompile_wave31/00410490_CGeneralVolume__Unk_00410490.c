/* address: 0x00410490 */
/* name: CGeneralVolume__Unk_00410490 */
/* signature: void __fastcall CGeneralVolume__Unk_00410490(int param_1) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void __fastcall CGeneralVolume__Unk_00410490(int param_1)

{
  float *pfVar1;
  int iVar2;
  float unaff_ESI;
  double dVar3;
  float unaff_retaddr;
  float fVar4;
  float fStack_18;
  undefined1 auStack_14 [4];
  undefined1 local_10 [12];
  float fStack_4;

  if (((*(int *)(param_1 + 0x2c) == 0) && (*(float *)(param_1 + 0x48) == _DAT_005d856c)) &&
     (pfVar1 = (float *)(**(code **)(**(int **)(param_1 + 0x18) + 0x6c))(local_10),
     _DAT_005d8570 < pfVar1[1] * pfVar1[1] + *pfVar1 * *pfVar1 + pfVar1[2] * pfVar1[2])) {
    fVar4 = *(float *)(param_1 + 0x18);
    fStack_18 = fVar4;
    dVar3 = CGeneralVolume__Helper_00409e60(*(float *)((int)fVar4 + 0x2c8));
    fStack_18 = unaff_retaddr * *(float *)(*(int *)((int)fVar4 + 0x4b0) + 0x14) * _DAT_005d8c94 *
                (float)dVar3;
    CGeneralVolume__Helper_00409e60(*(float *)((int)fVar4 + 0x2c8));
    pfVar1 = (float *)(**(code **)(**(int **)(param_1 + 0x18) + 0x6c))(auStack_14);
    if ((pfVar1[2] * pfVar1[2] + pfVar1[1] * pfVar1[1] + *pfVar1 * *pfVar1 < _DAT_005d8568) &&
       (iVar2 = (**(code **)(**(int **)(param_1 + 0x18) + 0x10c))(), iVar2 != 0)) {
      pfVar1 = (float *)(**(code **)(**(int **)(param_1 + 0x18) + 0x6c))(&fStack_18);
      fVar4 = SQRT(pfVar1[2] * pfVar1[2] + pfVar1[1] * pfVar1[1] + *pfVar1 * *pfVar1);
      if (fVar4 < _DAT_005d85c0) {
        fVar4 = 0.0;
      }
      unaff_ESI = fVar4 * unaff_ESI;
      fStack_4 = fVar4 * fStack_4;
    }
    iVar2 = *(int *)(param_1 + 0x18);
    if (*(int *)(iVar2 + 0x588) != 0) {
      unaff_ESI = unaff_ESI * _DAT_005d858c;
      fStack_4 = fStack_4 * _DAT_005d858c;
    }
    if (DAT_00672fd0 < *(float *)(iVar2 + 0x520) + _DAT_005d8bd8) {
      fVar4 = (DAT_00672fd0 - *(float *)(iVar2 + 0x520)) * _DAT_005d8c64;
      unaff_ESI = fVar4 * unaff_ESI;
      fStack_4 = fVar4 * fStack_4;
    }
    *(float *)(iVar2 + 0x278) = *(float *)(iVar2 + 0x278) - unaff_ESI;
    *(float *)(*(int *)(param_1 + 0x18) + 0x27c) =
         *(float *)(*(int *)(param_1 + 0x18) + 0x27c) - fStack_4;
  }
  return;
}
