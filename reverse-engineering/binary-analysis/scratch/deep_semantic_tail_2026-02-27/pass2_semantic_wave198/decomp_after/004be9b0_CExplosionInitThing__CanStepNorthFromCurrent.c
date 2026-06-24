/* address: 0x004be9b0 */
/* name: CExplosionInitThing__CanStepNorthFromCurrent */
/* signature: int CExplosionInitThing__CanStepNorthFromCurrent(void) */


/* WARNING: Unknown calling convention -- yet parameter storage is locked */

int CExplosionInitThing__CanStepNorthFromCurrent(void)

{
  uint uVar1;

  if ((0 < DAT_00829dc0) &&
     (*(short *)(&DAT_00809bc0 + (DAT_00829dc0 * 0x100 + DAT_00809dbc) * 2) == -1)) {
    uVar1 = DAT_00829dc0 - 1U & 0x80000007;
    if ((int)uVar1 < 0) {
      uVar1 = (uVar1 - 1 | 0xfffffff8) + 1;
    }
    if ((*(byte *)(((int)(DAT_00829dc0 - 1U) >> 3) * 0x100 + DAT_00809db8 + DAT_00809dbc) &
        (byte)(1 << ((byte)uVar1 & 0x1f))) != 0) {
      return 1;
    }
  }
  return 0;
}
