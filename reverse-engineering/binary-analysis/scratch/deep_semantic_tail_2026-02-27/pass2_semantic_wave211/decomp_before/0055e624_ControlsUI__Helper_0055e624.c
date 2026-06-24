/* address: 0x0055e624 */
/* name: ControlsUI__Helper_0055e624 */
/* signature: void __cdecl ControlsUI__Helper_0055e624(void * param_1, void * param_2) */


void __cdecl ControlsUI__Helper_0055e624(void *param_1,void *param_2)

{
  short sVar1;

  sVar1 = *(short *)param_1;
  while (sVar1 != 0) {
    param_1 = (void *)((int)param_1 + 2);
    sVar1 = *(short *)param_1;
  }
  do {
    sVar1 = *(short *)param_2;
    *(short *)param_1 = sVar1;
    param_1 = (void *)((int)param_1 + 2);
    param_2 = (void *)((int)param_2 + 2);
  } while (sVar1 != 0);
  return;
}
