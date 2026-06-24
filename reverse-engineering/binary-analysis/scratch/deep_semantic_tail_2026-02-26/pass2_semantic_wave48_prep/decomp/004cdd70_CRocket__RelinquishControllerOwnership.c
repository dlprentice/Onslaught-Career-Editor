/* address: 0x004cdd70 */
/* name: CRocket__RelinquishControllerOwnership */
/* signature: void __fastcall CRocket__RelinquishControllerOwnership(void * param_1) */


void __fastcall CRocket__RelinquishControllerOwnership(void *param_1)

{
  void *pvVar1;
  int number;

  number = 0;
  do {
    pvVar1 = CGame__GetController(&DAT_008a9a98,number);
    if (pvVar1 != (void *)0x0) {
      pvVar1 = CGame__GetController(&DAT_008a9a98,number);
      pvVar1 = CController__GetToControl(pvVar1);
      if (pvVar1 == param_1) {
        pvVar1 = CGame__GetController(&DAT_008a9a98,number);
        CController__RelinquishControl(pvVar1);
      }
    }
    number = number + 1;
  } while (number < 2);
  return;
}
