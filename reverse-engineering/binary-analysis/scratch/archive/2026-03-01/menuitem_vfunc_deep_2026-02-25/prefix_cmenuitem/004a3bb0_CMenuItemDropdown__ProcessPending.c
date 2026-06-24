/* address: 0x004a3bb0 */
/* name: CMenuItemDropdown__ProcessPending */
/* signature: undefined CMenuItemDropdown__ProcessPending(void) */


void CMenuItemDropdown__ProcessPending(void)

{
  int iVar1;

  iVar1 = DAT_0070486c;
  DAT_0070486c = 0;
  if (iVar1 != 0) {
    CMenuItemDropdown__Render(DAT_00704874,DAT_00704870,1);
  }
  return;
}
