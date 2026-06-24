/* address: 0x005aeaf0 */
/* name: CDXTexture__Helper_005aeaf0 */
/* signature: void __fastcall CDXTexture__Helper_005aeaf0(int param_1, int param_2, int param_3) */


void __fastcall CDXTexture__Helper_005aeaf0(int param_1,int param_2,int param_3)

{
  byte bVar1;
  int iVar2;
  byte *pbVar3;
  byte *pbVar4;
  int iVar5;
  undefined4 *in_EAX;
  int iVar6;
  int iVar7;
  undefined4 *puVar8;
  uint uVar9;

  puVar8 = (undefined4 *)*in_EAX;
  if (0 < *(int *)(param_1 + 0x13c)) {
    iVar2 = *(int *)(param_2 + 0x28);
    iVar6 = param_3 - (int)puVar8;
    param_3 = *(int *)(param_1 + 0x13c);
    do {
      pbVar3 = *(byte **)(iVar6 + (int)puVar8);
      bVar1 = *pbVar3;
      uVar9 = (uint)pbVar3[1];
      pbVar4 = (byte *)*puVar8;
      *pbVar4 = bVar1;
      pbVar4[1] = (byte)((int)((uint)bVar1 * 3 + 2 + uVar9) >> 2);
      pbVar3 = pbVar3 + 1;
      for (iVar7 = iVar2 + -2; pbVar4 = pbVar4 + 2, iVar7 != 0; iVar7 = iVar7 + -1) {
        iVar5 = uVar9 * 3;
        uVar9 = (uint)pbVar3[1];
        *pbVar4 = (byte)((int)(pbVar3[-1] + 1 + iVar5) >> 2);
        pbVar4[1] = (byte)((int)(uVar9 + 2 + iVar5) >> 2);
        pbVar3 = pbVar3 + 1;
      }
      bVar1 = *pbVar3;
      *pbVar4 = (byte)((int)(pbVar3[-1] + 1 + (uint)bVar1 * 3) >> 2);
      pbVar4[1] = bVar1;
      puVar8 = puVar8 + 1;
      param_3 = param_3 + -1;
    } while (param_3 != 0);
  }
  return;
}
