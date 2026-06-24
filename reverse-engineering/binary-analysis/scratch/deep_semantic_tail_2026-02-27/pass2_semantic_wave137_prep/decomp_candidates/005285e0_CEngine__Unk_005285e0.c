/* address: 0x005285e0 */
/* name: CEngine__Unk_005285e0 */
/* signature: void CEngine__Unk_005285e0(void) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */
/* WARNING: Unknown calling convention -- yet parameter storage is locked */

void CEngine__Unk_005285e0(void)

{
  int *piVar1;
  float10 extraout_ST0;
  float10 fVar2;
  undefined4 local_8;

  piVar1 = DAT_0089bec8;
  if (DAT_0089bec8 != (int *)0x0) {
    CMeshCollisionVolume__Helper_0055fa40();
    if ((float10)_DAT_005d856c <= extraout_ST0) {
      fVar2 = extraout_ST0;
      if ((float10)_DAT_005d8568 < extraout_ST0) {
        fVar2 = (float10)_DAT_005d8568;
      }
    }
    else {
      fVar2 = (float10)_DAT_005d856c;
    }
    local_8 = (undefined4)(longlong)ROUND(fVar2 * (float10)_DAT_005db3b4 - (float10)_DAT_005db3b4);
    (**(code **)(*piVar1 + 0x3c))(piVar1,local_8);
  }
  return;
}
