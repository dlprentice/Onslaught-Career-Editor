/* address: 0x0047ce80 */
/* name: CCannon__MarkDestroyedAndResetState */
/* signature: int __fastcall CCannon__MarkDestroyedAndResetState(int param_1) */


int __fastcall CCannon__MarkDestroyedAndResetState(int param_1)

{
  int iVar1;

  iVar1 = CUnit__MarkDestroyedAndCleanupLinks(param_1);
  if (iVar1 == 0) {
    return 0;
  }
  *(undefined4 *)(param_1 + 0x25c) = 0;
  return 1;
}
