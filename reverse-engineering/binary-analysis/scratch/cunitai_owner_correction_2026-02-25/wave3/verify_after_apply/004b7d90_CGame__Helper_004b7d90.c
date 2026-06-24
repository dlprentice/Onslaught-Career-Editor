/* address: 0x004b7d90 */
/* name: CGame__Helper_004b7d90 */
/* signature: void CGame__Helper_004b7d90(void) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */
/* WARNING: Unknown calling convention -- yet parameter storage is locked */

void CGame__Helper_004b7d90(void)

{
  int iVar1;

  if (((DAT_008a9ac4 == 0) && (DAT_008a9ac0 < 4)) && ((char)DAT_00704e74 != '\0')) {
    iVar1 = CBinkOpenThread__IsRunning();
    if (iVar1 == 0) {
      if (DAT_008073d0 != (undefined4 *)0x0) {
        (**(code **)*DAT_008073d0)(1);
        DAT_008073d0 = (undefined4 *)0x0;
      }
      if (DAT_0080738c == 0) {
        if (DAT_0089c808 != '\0') {
          FatalError__ExitWithLocalizedPrefix_A(&DAT_00704e74);
          return;
        }
      }
      else {
        CBinkOpenThread__Lock();
        DAT_008073d0 = (undefined4 *)
                       CPCSoundManager__CreateSampleFromData(&DAT_00707288,DAT_0080738c,0,0);
        DAT_0080738c = 0;
        CBinkOpenThread__Unlock();
        if (DAT_008073d0 != (undefined4 *)0x0) {
          CSoundManager__Unk_004e0b30();
        }
        DAT_00704e74._0_1_ = '\0';
        CGenericActiveReader__SetReader(&DAT_00704e70,(void *)0x0);
      }
    }
  }
  return;
}
