/* address: 0x0044a2d0 */
/* name: CDXEngine__Helper_0044a2d0 */
/* signature: void CDXEngine__Helper_0044a2d0(void) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */
/* WARNING: Unknown calling convention -- yet parameter storage is locked */

void CDXEngine__Helper_0044a2d0(void)

{
  float fVar1;
  int iVar2;
  undefined4 *puVar3;
  undefined4 *puVar4;
  float local_7c;
  float local_78;
  float local_74;
  int local_70;
  float local_6c;
  float local_68;
  float local_64;
  undefined4 local_5c [9];
  undefined4 local_38;
  undefined4 local_34;
  undefined4 local_30;
  undefined4 local_2c;
  undefined4 local_28;
  undefined4 local_24;
  undefined4 local_20;
  undefined4 local_1c;
  undefined4 local_18;
  undefined4 local_14;

  local_7c = -_DAT_006fbe6c;
  local_78 = -DAT_006fbe70;
  local_74 = -_DAT_006fbe74;
  fVar1 = SQRT(local_7c * local_7c + local_74 * local_74 + local_78 * local_78);
  if (fVar1 != _DAT_005d856c) {
    fVar1 = _DAT_005d8568 / fVar1;
    local_7c = fVar1 * local_7c;
    local_78 = fVar1 * local_78;
    local_74 = fVar1 * local_74;
  }
  Atmospherics__NotifyAll((int)&local_7c);
  CEngine__UpdateViewVector_005524a0(&DAT_009c7550,local_7c,local_78,local_74,local_70);
  DAT_009c68ad = 1;
  DAT_009c6910 = 1;
  local_5c[0] = 0;
  CDXEngine__Helper_0044a5f0();
  local_38 = 0;
  local_34 = 0;
  local_30 = 0;
  local_2c = 0;
  CDXEngine__Helper_0044a5f0();
  local_28 = 0;
  local_24 = 0;
  local_20 = 0;
  local_1c = 0;
  local_18 = 0;
  local_14 = 0;
  CDXEngine__Helper_0044a5f0();
  DAT_009c68a8 = DAT_006fbe54;
  DAT_009c690c = 1;
  MathMatrix3x4__AssignFromEightScalars();
  local_6c = -local_7c;
  puVar3 = local_5c;
  puVar4 = &DAT_009c65c0;
  for (iVar2 = 0x17; iVar2 != 0; iVar2 = iVar2 + -1) {
    *puVar4 = *puVar3;
    puVar3 = puVar3 + 1;
    puVar4 = puVar4 + 1;
  }
  local_68 = -local_78;
  local_64 = -local_74;
  DAT_009c68fc = 1;
  DAT_009c68a0 = 1;
  DAT_009c6904 = 1;
  MathMatrix3x4__AssignFromEightScalars();
  puVar3 = local_5c;
  puVar4 = &DAT_009c661c;
  for (iVar2 = 0x17; iVar2 != 0; iVar2 = iVar2 + -1) {
    *puVar4 = *puVar3;
    puVar3 = puVar3 + 1;
    puVar4 = puVar4 + 1;
  }
  DAT_009c68fd = 1;
  DAT_009c68a1 = 1;
  DAT_009c6905 = 1;
  DAT_009c68a2 = 0;
  DAT_009c6906 = 1;
  DAT_009c6907 = 1;
  DAT_009c6908 = 1;
  DAT_009c6909 = 1;
  DAT_009c690a = 1;
  DAT_009c690b = 1;
  DAT_009c68a3 = 0;
  DAT_009c68a4 = 0;
  DAT_009c68a5 = 0;
  DAT_009c68a6 = 0;
  DAT_009c68a7 = 0;
  return;
}
