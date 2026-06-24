/* address: 0x004fd5b0 */
/* name: CUnit__IsActiveAndNotInState12 */
/* signature: int __stdcall CUnit__IsActiveAndNotInState12(int param_1) */


int CUnit__IsActiveAndNotInState12(int param_1)

{
  if ((((param_1 != 0) && ((*(byte *)(param_1 + 0x2c) & 4) == 0)) &&
      (*(int *)(param_1 + 0x244) != 1)) && (*(int *)(param_1 + 0x244) != 2)) {
    return 1;
  }
  return 0;
}
