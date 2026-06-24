/* address: 0x004bea70 */
/* name: CExplosionInitThing__Helper_004bea70 */
/* signature: int CExplosionInitThing__Helper_004bea70(void) */


/* WARNING: Unknown calling convention -- yet parameter storage is locked */

int CExplosionInitThing__Helper_004bea70(void)

{
  uint uVar1;

  if ((DAT_00829dc0 < 0xff) &&
     (*(short *)((int)&DAT_00809fc0 + (DAT_00829dc0 * 0x100 + DAT_00809dbc) * 2) == -1)) {
    uVar1 = DAT_00829dc0 + 1U & 0x80000007;
    if ((int)uVar1 < 0) {
      uVar1 = (uVar1 - 1 | 0xfffffff8) + 1;
    }
    if ((*(byte *)(((int)(DAT_00829dc0 + 1U) >> 3) * 0x100 + DAT_00809db8 + DAT_00809dbc) &
        (byte)(1 << ((byte)uVar1 & 0x1f))) != 0) {
      return 1;
    }
  }
  return 0;
}
