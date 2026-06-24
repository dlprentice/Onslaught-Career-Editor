/* address: 0x0059ee20 */
/* name: CDXTexture__Helper_0059ee20 */
/* signature: void __stdcall CDXTexture__Helper_0059ee20(void * param_1, int param_2, uint param_3) */


void CDXTexture__Helper_0059ee20(void *param_1,int param_2,uint param_3)

{
  undefined4 *puVar1;
  int *piVar2;
  undefined1 *puVar3;
  int *piVar4;
  int iVar5;

  if (0xfffd < param_3) {
    puVar1 = *(undefined4 **)param_1;
    puVar1[5] = 0xb;
    (*(code *)*puVar1)(param_1);
  }
  CDXTexture__Helper_0059e0b0(param_2);
  piVar2 = *(int **)((int)param_1 + 0x18);
  puVar3 = (undefined1 *)*piVar2;
  *puVar3 = (char)(param_3 + 2 >> 8);
  *piVar2 = (int)(puVar3 + 1);
  piVar4 = piVar2 + 1;
  *piVar4 = *piVar4 + -1;
  if (*piVar4 == 0) {
    iVar5 = (*(code *)piVar2[3])(param_1);
    if (iVar5 == 0) {
      puVar1 = *(undefined4 **)param_1;
      puVar1[5] = 0x18;
      (*(code *)*puVar1)(param_1);
    }
  }
  piVar4 = *(int **)((int)param_1 + 0x18);
  puVar3 = (undefined1 *)*piVar4;
  *puVar3 = (char)(param_3 + 2);
  *piVar4 = (int)(puVar3 + 1);
  iVar5 = piVar4[1];
  piVar4[1] = iVar5 + -1;
  if (iVar5 + -1 == 0) {
    iVar5 = (*(code *)piVar4[3])(param_1);
    if (iVar5 == 0) {
      puVar1 = *(undefined4 **)param_1;
      puVar1[5] = 0x18;
      (*(code *)*puVar1)(param_1);
    }
  }
  return;
}
