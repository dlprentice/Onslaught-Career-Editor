/* address: 0x004a40f0 */
/* name: CMenuItemDropdown__CommitSelection */
/* signature: undefined CMenuItemDropdown__CommitSelection(void) */


void __fastcall CMenuItemDropdown__CommitSelection(int *param_1)

{
  if (param_1[8] != param_1[7]) {
    (**(code **)(*param_1 + 0x38))(param_1[8]);
    param_1[7] = param_1[8];
  }
  return;
}
