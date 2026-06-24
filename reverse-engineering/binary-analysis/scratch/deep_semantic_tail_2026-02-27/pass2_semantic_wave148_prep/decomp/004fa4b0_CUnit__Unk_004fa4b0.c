/* address: 0x004fa4b0 */
/* name: CUnit__Unk_004fa4b0 */
/* signature: int CUnit__Unk_004fa4b0(void) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */
/* WARNING: Unknown calling convention -- yet parameter storage is locked */

int CUnit__Unk_004fa4b0(void)

{
  float fVar1;
  float fVar2;
  float fVar3;
  float fVar4;
  undefined2 extraout_var;
  int iVar5;
  int *in_ECX;
  int iVar6;
  float *pfVar7;
  float10 fVar8;
  float10 fVar9;
  float10 fVar10;
  float *in_stack_00000004;
  float *in_stack_00000008;
  float *in_stack_0000000c;
  float *in_stack_00000010;
  float afStack_30 [4];
  float fStack_20;
  float fStack_1c;
  float fStack_18;
  float fStack_10;
  float fStack_c;
  float fStack_8;

  fVar8 = (float10)(**(code **)(*in_ECX + 0x60))();
  if (*in_stack_00000004 != *in_stack_00000008) {
    fVar9 = (float10)*in_stack_00000008;
    fVar10 = (float10)*in_stack_00000004;
    if (((float10)_DAT_005d85c8 <= fVar10) || (fVar9 < (float10)_DAT_005d85e4)) {
      if (((float10)_DAT_005d85e4 <= fVar10) && (fVar9 < (float10)_DAT_005d85c8)) {
        fVar9 = fVar9 + (float10)_DAT_005d85e0;
      }
    }
    else {
      fVar9 = fVar9 - (float10)_DAT_005d85e0;
    }
    fVar9 = ABS(fVar10 - fVar9) * fVar8 * (float10)_DAT_005d85c0;
    if ((float10)(float)(fVar8 * (float10)*in_stack_0000000c) < fVar9) {
      fVar9 = (float10)(float)(fVar8 * (float10)*in_stack_0000000c);
    }
    if (*in_stack_00000008 <= *in_stack_00000004) {
      if (*in_stack_00000004 - *in_stack_00000008 <= _DAT_005d85e8) goto LAB_004fa583;
      *in_stack_00000004 = (float)(fVar9 + (float10)*in_stack_00000004);
    }
    else if (_DAT_005d85e8 < *in_stack_00000008 - *in_stack_00000004) {
LAB_004fa583:
      *in_stack_00000004 = (float)((float10)*in_stack_00000004 - fVar9);
    }
    else {
      *in_stack_00000004 = (float)(fVar9 + (float10)*in_stack_00000004);
    }
    if (*in_stack_00000004 <= _DAT_005d85e8) {
      if (_DAT_005d85dc <= *in_stack_00000004) goto LAB_004fa5bb;
      fVar1 = *in_stack_00000004 + _DAT_005d85e0;
    }
    else {
      fVar1 = *in_stack_00000004 - _DAT_005d85e0;
    }
    *in_stack_00000004 = fVar1;
  }
LAB_004fa5bb:
  if (in_stack_00000004[1] != in_stack_00000008[1]) {
    fVar9 = ABS(ABS((float10)in_stack_00000004[1] - (float10)in_stack_00000008[1])) * fVar8 *
            (float10)_DAT_005d85c0;
    if ((float10)(float)(fVar8 * (float10)in_stack_0000000c[1]) < fVar9) {
      fVar9 = (float10)(float)(fVar8 * (float10)in_stack_0000000c[1]);
    }
    if (in_stack_00000004[1] <= in_stack_00000008[1]) {
      in_stack_00000004[1] = (float)(fVar9 + (float10)in_stack_00000004[1]);
    }
    else {
      in_stack_00000004[1] = (float)((float10)in_stack_00000004[1] - fVar9);
    }
  }
  fVar1 = in_stack_00000004[2];
  fVar2 = in_stack_00000008[2];
  iVar5 = CONCAT22(extraout_var,
                   (ushort)(fVar1 < fVar2) << 8 | (ushort)(NAN(fVar1) || NAN(fVar2)) << 10 |
                   (ushort)(fVar1 == fVar2) << 0xe);
  if ((fVar1 == fVar2) != 0) goto LAB_004fa724;
  fVar9 = (float10)in_stack_00000008[2];
  fVar10 = (float10)in_stack_00000004[2];
  if (((float10)_DAT_005d85c8 <= fVar10) || (fVar9 < (float10)_DAT_005d85e4)) {
    if (((float10)_DAT_005d85e4 <= fVar10) && (fVar9 < (float10)_DAT_005d85c8)) {
      fVar9 = fVar9 + (float10)_DAT_005d85e0;
    }
  }
  else {
    fVar9 = fVar9 - (float10)_DAT_005d85e0;
  }
  fVar9 = ABS(fVar10 - fVar9) * fVar8 * (float10)_DAT_005d85c0;
  if ((float10)(float)(fVar8 * (float10)in_stack_0000000c[2]) < fVar9) {
    fVar9 = (float10)(float)(fVar8 * (float10)in_stack_0000000c[2]);
  }
  if (in_stack_00000008[2] <= in_stack_00000004[2]) {
    if (in_stack_00000004[2] - in_stack_00000008[2] <= _DAT_005d85e8) goto LAB_004fa6df;
    in_stack_00000004[2] = (float)(fVar9 + (float10)in_stack_00000004[2]);
  }
  else if (_DAT_005d85e8 < in_stack_00000008[2] - in_stack_00000004[2]) {
LAB_004fa6df:
    in_stack_00000004[2] = (float)((float10)in_stack_00000004[2] - fVar9);
  }
  else {
    in_stack_00000004[2] = (float)(fVar9 + (float10)in_stack_00000004[2]);
  }
  fVar1 = in_stack_00000004[2];
  fVar2 = in_stack_00000004[2];
  iVar5 = CONCAT22(extraout_var,
                   (ushort)(fVar1 < _DAT_005d85e8) << 8 |
                   (ushort)(NAN(fVar1) || NAN(_DAT_005d85e8)) << 10 |
                   (ushort)(fVar1 == _DAT_005d85e8) << 0xe);
  if (fVar1 < _DAT_005d85e8 || (fVar1 == _DAT_005d85e8) != 0) {
    iVar5 = CONCAT22(extraout_var,
                     (ushort)(fVar2 < _DAT_005d85dc) << 8 |
                     (ushort)(NAN(fVar2) || NAN(_DAT_005d85dc)) << 10 |
                     (ushort)(fVar2 == _DAT_005d85dc) << 0xe);
    if (fVar2 < _DAT_005d85dc) {
      in_stack_00000004[2] = in_stack_00000004[2] + _DAT_005d85e0;
    }
  }
  else {
    in_stack_00000004[2] = fVar2 - _DAT_005d85e0;
  }
LAB_004fa724:
  fVar8 = (float10)fcos((float10)*in_stack_00000004);
  fVar1 = (float)fVar8;
  fVar8 = (float10)fsin((float10)*in_stack_00000004);
  fVar2 = (float)fVar8;
  fVar8 = (float10)fcos((float10)in_stack_00000004[2]);
  fVar3 = (float)fVar8;
  fVar8 = (float10)fsin((float10)in_stack_00000004[2]);
  fVar9 = (float10)fcos((float10)in_stack_00000004[1]);
  fVar4 = (float)fVar9;
  fVar9 = (float10)fsin((float10)in_stack_00000004[1]);
  afStack_30[0] = (float)((float10)fVar3 * (float10)fVar1 - fVar9 * fVar8 * (float10)fVar2);
  afStack_30[1] = -(fVar4 * fVar2);
  afStack_30[2] = (float)(fVar8 * (float10)fVar1 + fVar9 * (float10)fVar3 * (float10)fVar2);
  fStack_20 = (float)((float10)fVar3 * (float10)fVar2 + fVar9 * fVar8 * (float10)fVar1);
  fStack_1c = fVar4 * fVar1;
  fStack_18 = (float)(fVar8 * (float10)fVar2 -
                     (float10)(float)(fVar9 * (float10)fVar3) * (float10)fVar1);
  fStack_10 = (float)-((float10)fVar4 * fVar8);
  fStack_c = (float)fVar9;
  fStack_8 = fVar4 * fVar3;
  pfVar7 = afStack_30;
  for (iVar6 = 0xc; iVar6 != 0; iVar6 = iVar6 + -1) {
    *in_stack_00000010 = *pfVar7;
    pfVar7 = pfVar7 + 1;
    in_stack_00000010 = in_stack_00000010 + 1;
  }
  return iVar5;
}
