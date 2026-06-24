/* address: 0x00429280 */
/* name: FUN_00429280 */
/* signature: undefined FUN_00429280(void) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void __fastcall FUN_00429280(int param_1)

{
  float fVar1;
  float fVar2;
  float fVar3;
  float fVar4;
  int iVar5;
  int unaff_ESI;
  int unaff_EDI;
  float10 fVar6;
  float10 fVar7;
  float10 fVar8;
  float10 fVar9;
  double dVar10;
  float fStack00000008;

  if (param_1 == 0) {
    return;
  }
  if ((*(byte *)(unaff_ESI + 0x2c) & 4) != 0) {
    return;
  }
  if ((*(byte *)(param_1 + 0x2c) & 4) != 0) {
    return;
  }
  iVar5 = CUnitAI__Helper_004fde10(param_1);
  if (iVar5 != 0) {
    return;
  }
  fVar1 = *(float *)(unaff_EDI + 8);
  fVar2 = *(float *)(*(int *)(unaff_EDI + 0x18) + 0x1c);
  fVar3 = *(float *)(unaff_EDI + 0xc);
  fVar4 = *(float *)(*(int *)(unaff_EDI + 0x18) + 0x20);
  dVar10 = CFrontEndPage__Unk_00428bc0(unaff_ESI);
  fVar8 = (float10)dVar10;
  fVar9 = fVar8;
  if (*(int *)(unaff_EDI + 0x1c) != 0) {
    fVar9 = (float10)fpatan((float10)(fVar1 - fVar2),(float10)(fVar3 - fVar4));
    fVar9 = -fVar9;
  }
  fVar6 = fVar8 + (float10)*(float *)(unaff_ESI + 0x250);
  fVar7 = (float10)_DAT_005d85e8;
  *(float *)(unaff_ESI + 0x250) = (float)fVar6;
  if (fVar6 <= fVar7) {
    if (fVar6 < (float10)_DAT_005d85dc) {
      *(float *)(unaff_ESI + 0x250) = (float)(fVar6 + (float10)_DAT_005d85e0);
    }
  }
  else {
    *(float *)(unaff_ESI + 0x250) = (float)(fVar6 - (float10)_DAT_005d85e0);
  }
  fVar1 = *(float *)(unaff_ESI + 0x250);
  if ((_DAT_005d85c8 <= fVar1) || (fVar9 <= (float10)_DAT_005d85e4)) {
    fVar7 = fVar9;
    if ((_DAT_005d85e4 < fVar1) && (fVar9 < (float10)_DAT_005d85c8)) {
      fVar7 = fVar9 + (float10)_DAT_005d85e0;
    }
  }
  else {
    fVar7 = fVar9 - (float10)_DAT_005d85e0;
  }
  iVar5 = *(int *)(unaff_ESI + 0x164);
  fVar7 = ABS((float10)fVar1 - fVar7) * (float10)_DAT_005d85c0;
  fStack00000008 = (float)fVar7;
  if ((float10)*(float *)(iVar5 + 0xb8) < fVar7) {
    fStack00000008 = *(float *)(iVar5 + 0xb8);
  }
  if (fVar9 <= (float10)*(float *)(unaff_ESI + 0x250)) {
    if ((float10)_DAT_005d85e8 < (float10)*(float *)(unaff_ESI + 0x250) - fVar9) {
      fStack00000008 = fStack00000008 + *(float *)(unaff_ESI + 0x250);
      goto LAB_00429415;
    }
  }
  else if (fVar9 - (float10)*(float *)(unaff_ESI + 0x250) <= (float10)_DAT_005d85e8) {
    fStack00000008 = fStack00000008 + *(float *)(unaff_ESI + 0x250);
    goto LAB_00429415;
  }
  fStack00000008 = *(float *)(unaff_ESI + 0x250) - fStack00000008;
LAB_00429415:
  *(float *)(unaff_ESI + 0x250) = fStack00000008;
  fVar8 = (float10)*(float *)(unaff_ESI + 0x250) - fVar8;
  fVar9 = (float10)_DAT_005d85e8;
  *(float *)(unaff_ESI + 0x250) = (float)fVar8;
  if (fVar8 <= fVar9) {
    if (fVar8 < (float10)_DAT_005d85dc) {
      *(float *)(unaff_ESI + 0x250) = (float)(fVar8 + (float10)_DAT_005d85e0);
    }
  }
  else {
    *(float *)(unaff_ESI + 0x250) = (float)(fVar8 - (float10)_DAT_005d85e0);
  }
  if (*(float *)(unaff_ESI + 0x250) <= *(float *)(iVar5 + 0xd8)) {
    fVar1 = -*(float *)(iVar5 + 0xd8);
    if (fVar1 <= *(float *)(unaff_ESI + 0x250)) {
      return;
    }
    *(float *)(unaff_ESI + 0x250) = fVar1;
    return;
  }
  *(float *)(unaff_ESI + 0x250) = *(float *)(iVar5 + 0xd8);
  return;
}
