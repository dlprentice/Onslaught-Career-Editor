/* address: 0x00566104 */
/* name: CRT__InvokeLocaleValidationCallback */
/* signature: int __cdecl CRT__InvokeLocaleValidationCallback(int param_1) */


int __cdecl CRT__InvokeLocaleValidationCallback(int param_1)

{
  int iVar1;

  if (DAT_009d09b8 != (code *)0x0) {
    iVar1 = (*DAT_009d09b8)(param_1);
    if (iVar1 != 0) {
      return 1;
    }
  }
  return 0;
}
