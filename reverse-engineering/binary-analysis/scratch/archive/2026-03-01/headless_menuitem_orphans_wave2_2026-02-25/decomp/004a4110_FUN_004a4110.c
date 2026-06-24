/* address: 0x004a4110 */
/* name: FUN_004a4110 */
/* signature: undefined FUN_004a4110(void) */


void __thiscall FUN_004a4110(int *param_1,undefined4 param_2,undefined4 param_3)

{
  byte bVar1;
  int iVar2;

  switch(param_3) {
  case 0x2a:
  case 0x36:
    CFrontEnd__PlaySound(0);
    iVar2 = param_1[8];
    param_1[8] = iVar2 + -1;
    if (iVar2 + -1 < 0) {
      param_1[8] = 0;
    }
    *(undefined1 *)(param_1 + 9) = 1;
    return;
  case 0x2b:
  case 0x37:
    CFrontEnd__PlaySound(0);
    param_1[8] = param_1[8] + 1;
    iVar2 = (**(code **)(*param_1 + 0x40))();
    if (iVar2 <= param_1[8]) {
      iVar2 = (**(code **)(*param_1 + 0x40))();
      param_1[8] = iVar2 + -1;
    }
    *(undefined1 *)(param_1 + 9) = 1;
    return;
  case 0x2c:
    CFrontEnd__PlaySound(1);
    if (((char)param_1[9] == '\0') && (iVar2 = (**(code **)(*param_1 + 0x40))(), iVar2 < 2)) {
      CFrontEnd__PlaySound(2);
      return;
    }
    bVar1 = *(byte *)(param_1 + 9);
    *(byte *)(param_1 + 9) = bVar1 ^ 1;
    if ((((bVar1 ^ 1) == 0) && (*(char *)((int)param_1 + 0x25) == '\0')) &&
       (iVar2 = param_1[8], param_1[7] != iVar2)) {
      param_1[7] = iVar2;
      (**(code **)(*param_1 + 0x38))(iVar2);
      return;
    }
    break;
  case 0x2e:
    if ((char)param_1[9] != '\0') {
      CFrontEnd__PlaySound(2);
      *(undefined1 *)(param_1 + 9) = 0;
      param_1[8] = param_1[7];
    }
  }
  return;
}
