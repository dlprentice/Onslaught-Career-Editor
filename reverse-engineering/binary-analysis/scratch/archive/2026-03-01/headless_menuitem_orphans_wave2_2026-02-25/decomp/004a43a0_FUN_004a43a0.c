/* address: 0x004a43a0 */
/* name: FUN_004a43a0 */
/* signature: undefined FUN_004a43a0(void) */


void __thiscall FUN_004a43a0(int *param_1,undefined4 param_2,int param_3)

{
  int iVar1;
  bool bVar2;

  bVar2 = false;
  if (param_3 == 0x2c) {
    if ((int *)param_1[0xd] != (int *)0x0) {
      (**(code **)(*(int *)param_1[0xd] + 0x18))(param_1);
    }
    param_1[10] = param_1[9];
  }
  else if (param_3 == 0x36) {
    iVar1 = param_1[9];
    param_1[9] = iVar1 + -1;
    if (iVar1 + -1 < 0) {
      param_1[9] = 0;
      bVar2 = true;
    }
    else {
      (**(code **)(*param_1 + 0x38))();
      CFrontEnd__PlaySound(0);
      bVar2 = true;
    }
  }
  else if (param_3 == 0x37) {
    iVar1 = param_1[9];
    param_1[9] = iVar1 + 1;
    if (param_1[0xb] < iVar1 + 1) {
      param_1[9] = param_1[0xb];
      bVar2 = true;
    }
    else {
      (**(code **)(*param_1 + 0x38))();
      CFrontEnd__PlaySound(0);
      bVar2 = true;
    }
  }
  if (((char)param_1[0xc] != '\0') && (bVar2)) {
    if ((int *)param_1[0xd] != (int *)0x0) {
      (**(code **)(*(int *)param_1[0xd] + 0x18))(param_1);
    }
    param_1[10] = param_1[9];
  }
  return;
}
