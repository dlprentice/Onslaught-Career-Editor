/* address: 0x00528540 */
/* name: CEngine__Unk_00528540 */
/* signature: void CEngine__Unk_00528540(void) */


/* WARNING: Removing unreachable block (ram,0x00528562) */
/* WARNING: Removing unreachable block (ram,0x0052856b) */
/* WARNING: Unknown calling convention -- yet parameter storage is locked */

void CEngine__Unk_00528540(void)

{
  int iVar1;
  void *local_4;

  if (DAT_0089bec8 != (int *)0x0) {
    (**(code **)(*DAT_0089bec8 + 0x24))(DAT_0089bec8);
    iVar1 = CEngine__Helper_0055f8a1(local_4,&DAT_0089bed4);
    if (iVar1 == 0) {
      return;
    }
    CEngine__Helper_0055f807(&DAT_0089bed4,local_4,0xff);
    DAT_0089beac = 0;
    SetEvent(DAT_0089beb8);
  }
  return;
}
