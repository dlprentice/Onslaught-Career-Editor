/* address: 0x004d05c0 */
/* name: CMenuItemRange__IsBindingActive */
/* signature: int __fastcall CMenuItemRange__IsBindingActive(int param_1) */


int __fastcall CMenuItemRange__IsBindingActive(int param_1)

{
  if ((*(int *)(param_1 + 8) != 0) && (*(char *)(*(int *)(param_1 + 8) + 8) != '\0')) {
    return 1;
  }
  return 0;
}
