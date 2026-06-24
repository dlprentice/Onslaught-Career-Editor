/* address: 0x0059bc10 */
/* name: CDXTexture__Unk_0059bc10 */
/* signature: int __stdcall CDXTexture__Unk_0059bc10(void * param_1, int param_2, uint param_3) */


int CDXTexture__Unk_0059bc10(void *param_1,int param_2,uint param_3)

{
  int iVar1;
  undefined4 *puVar2;
  undefined4 uVar3;
  undefined4 *extraout_EAX;

  iVar1 = *(int *)((int)param_1 + 4);
  if (0x3b9ac9f0 < param_3) {
    puVar2 = *(undefined4 **)param_1;
    puVar2[5] = 0x36;
    puVar2[6] = 3;
    (*(code *)*puVar2)(param_1);
  }
  if ((param_3 & 7) != 0) {
    param_3 = param_3 + (8 - (param_3 & 7));
  }
  if ((param_2 < 0) || (1 < param_2)) {
    puVar2 = *(undefined4 **)param_1;
    puVar2[5] = 0xe;
    puVar2[6] = param_2;
    (*(code *)*puVar2)(param_1);
  }
  CDXTexture__Unk_005b1c00((int)param_1,param_3 + 0x10);
  if (extraout_EAX == (undefined4 *)0x0) {
    puVar2 = *(undefined4 **)param_1;
    puVar2[5] = 0x36;
    puVar2[6] = 4;
    (*(code *)*puVar2)(param_1);
  }
  *(uint *)(iVar1 + 0x4c) = *(int *)(iVar1 + 0x4c) + param_3 + 0x10;
  uVar3 = *(undefined4 *)(iVar1 + 0x3c + param_2 * 4);
  *(undefined4 **)(iVar1 + 0x3c + param_2 * 4) = extraout_EAX;
  extraout_EAX[1] = param_3;
  *extraout_EAX = uVar3;
  extraout_EAX[2] = 0;
  return (int)(extraout_EAX + 4);
}
