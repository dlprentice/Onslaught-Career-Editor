/* address: 0x0059bd60 */
/* name: CDXTexture__Unk_0059bd60 */
/* signature: int __stdcall CDXTexture__Unk_0059bd60(void * param_1, int param_2, int param_3, uint param_4) */


int CDXTexture__Unk_0059bd60(void *param_1,int param_2,int param_3,uint param_4)

{
  undefined4 *puVar1;
  uint uVar2;
  int iVar3;
  int iVar4;
  uint uVar5;
  uint uVar6;

  uVar2 = (uint)(0x3b9ac9f0 / (ulonglong)(uint)(param_3 * 0x80));
  iVar3 = *(int *)((int)param_1 + 4);
  if (uVar2 == 0) {
    puVar1 = *(undefined4 **)param_1;
    puVar1[5] = 0x46;
    (*(code *)*puVar1)(param_1);
  }
  if ((int)param_4 <= (int)uVar2) {
    uVar2 = param_4;
  }
  *(uint *)(iVar3 + 0x50) = uVar2;
  iVar3 = CDXTexture__Unk_0059bae0(param_1,param_2,param_4 << 2);
  uVar6 = 0;
  if (param_4 != 0) {
    do {
      if (param_4 - uVar6 <= uVar2) {
        uVar2 = param_4 - uVar6;
      }
      iVar4 = CDXTexture__Unk_0059bc10(param_1,param_2,uVar2 * param_3 * 0x80);
      for (uVar5 = uVar2; uVar5 != 0; uVar5 = uVar5 - 1) {
        *(int *)(iVar3 + uVar6 * 4) = iVar4;
        uVar6 = uVar6 + 1;
        iVar4 = iVar4 + param_3 * 0x80;
      }
    } while (uVar6 < param_4);
  }
  return iVar3;
}
