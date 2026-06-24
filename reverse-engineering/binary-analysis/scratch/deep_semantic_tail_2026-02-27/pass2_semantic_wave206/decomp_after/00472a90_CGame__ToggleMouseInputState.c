/* address: 0x00472a90 */
/* name: CGame__ToggleMouseInputState */
/* signature: void __fastcall CGame__ToggleMouseInputState(int param_1) */


void __fastcall CGame__ToggleMouseInputState(int param_1)

{
  int iVar1;
  bool bVar2;

  bVar2 = *(char *)(param_1 + 0x1c) == '\0';
  *(bool *)(param_1 + 0x1c) = bVar2;
  if (bVar2) {
    *(undefined4 *)(param_1 + 0x20) = 0;
    iVar1 = *(int *)(param_1 + 0x2c);
    while ((iVar1 == 0 && (*(int *)(param_1 + 0x20) < 6))) {
      iVar1 = *(int *)(param_1 + 0x20) + 1;
      *(int *)(param_1 + 0x20) = iVar1;
      iVar1 = *(int *)(param_1 + 0x2c + iVar1 * 4);
    }
    *(undefined1 *)(param_1 + 0x14) = 0;
    PlatformInput__ShutdownMouse();
    return;
  }
  PlatformInput__InitMouse();
  return;
}
