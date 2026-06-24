/* address: 0x00413b90 */
/* name: CCylinder__Unk_00413b90 */
/* signature: void __fastcall CCylinder__Unk_00413b90(int param_1) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void __fastcall CCylinder__Unk_00413b90(int param_1)

{
  int iVar1;
  float fVar2;
  float unaff_ESI;
  int iVar3;
  float fStack_50;
  float fStack_44;
  float local_40;
  float fStack_3c;
  float fStack_34;
  float fStack_30;
  float fStack_2c;
  float fStack_24;
  float fStack_20;
  float fStack_14;
  float fStack_10;
  float fStack_c;

  iVar3 = 0;
  while( true ) {
    (**(code **)(**(int **)(param_1 + 0x20) + 0x6c))(&local_40);
    iVar1 = *(int *)(param_1 + 0x20);
    fStack_2c = fStack_3c + *(float *)(iVar1 + 0x24);
    fStack_30 = local_40 + *(float *)(iVar1 + 0x20);
    fStack_34 = fStack_44 + *(float *)(iVar1 + 0x1c);
    CMonitor__Helper_0047ec60(0x6fadc8,&stack0xffffffac,&fStack_34);
    fVar2 = SQRT(unaff_ESI * unaff_ESI + fStack_50 * fStack_50);
    if (fVar2 != _DAT_005d856c) {
      fVar2 = _DAT_005d8568 / fVar2;
      unaff_ESI = fVar2 * unaff_ESI;
      fStack_50 = fStack_50 * fVar2;
    }
    fVar2 = fStack_3c * 0.0 + fStack_44 * unaff_ESI + fStack_50 * local_40;
    if (_DAT_005d8ce0 < fVar2) break;
    fStack_24 = unaff_ESI * fVar2;
    fStack_20 = fStack_50 * fVar2;
    fStack_14 = fStack_44 - fStack_24;
    fStack_10 = local_40 - fStack_20;
    fStack_c = fStack_3c - fVar2 * 0.0;
    (**(code **)(**(int **)(param_1 + 0x20) + 0x70))(&fStack_14);
    iVar3 = iVar3 + 1;
    if (5 < iVar3) {
      return;
    }
  }
  return;
}
