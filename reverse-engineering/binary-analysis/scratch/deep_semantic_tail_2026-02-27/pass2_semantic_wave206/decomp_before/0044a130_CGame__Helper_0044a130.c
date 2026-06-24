/* address: 0x0044a130 */
/* name: CGame__Helper_0044a130 */
/* signature: void CGame__Helper_0044a130(void) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */
/* WARNING: Unknown calling convention -- yet parameter storage is locked */

void CGame__Helper_0044a130(void)

{
  int *piVar1;
  uint uVar2;
  int iVar3;

  CDamage__ResetDamageTables(&DAT_008aa9f0);
  piVar1 = DAT_00855090;
  if (DAT_00855090 == (int *)0x0) {
    iVar3 = 0;
  }
  else {
    iVar3 = *DAT_00855090;
  }
  while (iVar3 != 0) {
    if ((*(uint *)(iVar3 + 0x34) & 0x2000000) != 0) {
      uVar2 = CTree__ComputeLodBucket(iVar3);
      CDXEngine__ApplyLandscapeDamageStamp
                (*(float *)(iVar3 + 0x1c) - _DAT_005d8c40,*(float *)(iVar3 + 0x20) + _DAT_005d85c0,
                 uVar2 & 0xff);
    }
    piVar1 = (int *)piVar1[1];
    if (piVar1 == (int *)0x0) {
      iVar3 = 0;
    }
    else {
      iVar3 = *piVar1;
    }
  }
  _DAT_008c0278 = DAT_008c0274;
  CDXLandscape__Reset();
  return;
}
