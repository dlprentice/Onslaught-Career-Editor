/* address: 0x005b6500 */
/* name: CDXTexture__Unk_005b6500 */
/* signature: void __fastcall CDXTexture__Unk_005b6500(void * param_1, int param_2, int param_3) */


void __fastcall CDXTexture__Unk_005b6500(void *param_1,int param_2,int param_3)

{
  int iVar1;
  int in_EAX;
  byte *pbVar2;
  undefined1 *puVar3;
  int iVar4;
  uint uVar5;
  int iVar6;

  iVar1 = *(int *)(param_2 + 0x1c);
  CDXTexture__Helper_005b6290
            ((int)param_1,*(int *)(in_EAX + 0xf4),*(int *)(in_EAX + 0x1c),iVar1 * 0x10);
  if (0 < *(int *)(param_2 + 0xc)) {
    iVar4 = param_3 - (int)param_1;
    param_3 = *(int *)(param_2 + 0xc);
    do {
      puVar3 = *(undefined1 **)(iVar4 + (int)param_1);
      pbVar2 = *(byte **)param_1;
      uVar5 = 0;
      for (iVar6 = iVar1 << 3; iVar6 != 0; iVar6 = iVar6 + -1) {
        *puVar3 = (char)((int)((uint)*pbVar2 + uVar5 + pbVar2[1]) >> 1);
        puVar3 = puVar3 + 1;
        uVar5 = uVar5 ^ 1;
        pbVar2 = pbVar2 + 2;
      }
      param_1 = (void *)((int)param_1 + 4);
      param_3 = param_3 + -1;
    } while (param_3 != 0);
  }
  return;
}
