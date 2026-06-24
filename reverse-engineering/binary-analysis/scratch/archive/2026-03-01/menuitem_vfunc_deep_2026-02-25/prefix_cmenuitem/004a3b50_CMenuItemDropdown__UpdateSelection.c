/* address: 0x004a3b50 */
/* name: CMenuItemDropdown__UpdateSelection */
/* signature: undefined CMenuItemDropdown__UpdateSelection(void) */


void __fastcall CMenuItemDropdown__UpdateSelection(int *param_1)

{
  int iVar1;

  iVar1 = (**(code **)(*param_1 + 0x3c))();
  param_1[7] = iVar1;
  param_1[8] = iVar1;
  return;
}
