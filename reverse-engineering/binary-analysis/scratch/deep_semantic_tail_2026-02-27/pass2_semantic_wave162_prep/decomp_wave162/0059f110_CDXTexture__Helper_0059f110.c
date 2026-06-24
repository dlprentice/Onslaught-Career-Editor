/* address: 0x0059f110 */
/* name: CDXTexture__Helper_0059f110 */
/* signature: void __stdcall CDXTexture__Helper_0059f110(void * param_1) */


void CDXTexture__Helper_0059f110(void *param_1)

{
  int *piVar1;
  undefined4 *puVar2;
  undefined1 *puVar3;
  int iVar4;

  puVar2 = *(undefined4 **)((int)param_1 + 0x18);
  puVar3 = (undefined1 *)*puVar2;
  *puVar3 = 0xff;
  *puVar2 = puVar3 + 1;
  piVar1 = puVar2 + 1;
  *piVar1 = *piVar1 + -1;
  if (*piVar1 == 0) {
    iVar4 = (*(code *)puVar2[3])(param_1);
    if (iVar4 == 0) {
      puVar2 = *(undefined4 **)param_1;
      puVar2[5] = 0x18;
      (*(code *)*puVar2)(param_1);
    }
  }
  puVar2 = *(undefined4 **)((int)param_1 + 0x18);
  puVar3 = (undefined1 *)*puVar2;
  *puVar3 = 0xd9;
  *puVar2 = puVar3 + 1;
  piVar1 = puVar2 + 1;
  *piVar1 = *piVar1 + -1;
  if (*piVar1 == 0) {
    iVar4 = (*(code *)puVar2[3])(param_1);
    if (iVar4 == 0) {
      puVar2 = *(undefined4 **)param_1;
      puVar2[5] = 0x18;
      (*(code *)*puVar2)(param_1);
    }
  }
  return;
}
