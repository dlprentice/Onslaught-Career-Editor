/* address: 0x0059c610 */
/* name: CFastVB__ReleaseOwnedObjectAndReset_Core */
/* signature: void __stdcall CFastVB__ReleaseOwnedObjectAndReset_Core(int param_1) */


void CFastVB__ReleaseOwnedObjectAndReset_Core(int param_1)

{
  if (*(int *)(param_1 + 4) != 0) {
    (**(code **)(*(int *)(param_1 + 4) + 0x28))(param_1);
  }
  *(undefined4 *)(param_1 + 4) = 0;
  *(undefined4 *)(param_1 + 0x14) = 0;
  return;
}
